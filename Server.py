import socket 
import re
import threading
import time
import select

# create global variables
HOST = "::1" # IPv6 connection 
PORT = 6667 #IRC port
clients = {} # store clients in dictinary
client_lock = threading.Lock() #locking to access 
channels = {} # store channels in dictinary
 
class Network_Handler: 
    
 def __init__(self):
        self.server = None
 #server socket
 def connect(self):
    
 # loop to keep looking for more clients until interrupted
     try:
        self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)   #AF.INET6 so socket uses IPv6  #SOCK stream so socket uses TCP
        print("socket created")
        self.server.bind((HOST, PORT)) # binding socket to specified HOST & PORT
        print ("socket binded to %s" %(PORT)) 
        self.server.listen(5) #accepting incoming connections
        print("socket listening")
        
        hostname = socket.gethostname()
        print('HOSTNAME: ' + hostname)
        
        while True:
            try: 
                clientsocket, address = self.server.accept() #accepting incoming connection 
                print("Accepted connection from" , address)

                client = Client(clientsocket, address, hostname)  # Create a new client instance

                # use of client_lock to making sure the thread is safe to access to clients dictionary
                with client_lock:
                    clients[address] = client  # store client info
                
                # Create and start a new thread to handle the client
                server = Server(self, hostname)  # Instantiate the Server class
                   
                #making a new thread to handle client, to allow for multiple concurrent clients
                newthread = threading.Thread(target=server.handling_client, args=(clientsocket, address))
                newthread.daemon = True #making sure thread exits when main program does
                newthread.start() #new thread to handle clients

            except Exception as e:
                print(f"Error while handling client: {e}")   

     except Exception as e:
        print("Error creating socket:", e)
        
     finally:
            server.close()
            print("Server closed")  
            
 def send(self, clientsocket, data):
        try:
            # Encode the data to bytes and send it to the client
            print("Sending data")
            clientsocket.send(data.encode('utf-8') + b'\r\n') 
        except Exception as e:
            print(f"Error sending data: {e}")
           # self.close_connection(clientsocket)

 def receive(self, clientsocket):
        try:
            # Receive up to 1024 bytes of data and decode it
            data = clientsocket.recv(1024).decode('utf-8').strip()
            if data:
                print(f"Received data: {data}")
                return data
            else:
                print("No data received, closing connection.")
                #self.close_connection(clientsocket)
                return None
        except Exception as e:
            print(f"Error receiving data: {e}")
            #self.close_connection(clientsocket)
            return None

 def close_connection(self, clientsocket):
        try:
            print("Closing connection...")
            clientsocket.close()  # Close the client socket
        except Exception as e:
            print(f"Error closing connection: {e}")







class Server:
 def __init__(self, network_handler, hostname):
        self.network_handler = network_handler  # store the reference to the Network_Handler instance
        self.hostname = hostname

 def handling_client(self, clientsocket, address):
    #print("handling_client called for:", clientsocket.getpeername())  # checking which client is connected
    
    last_activity_time = time.time()  # tracks the last time we received anything from client
    ping_interval = 20  # time for sending PING if no activity from the client

    pong_timeout = 60  # timeout for waiting for PONG or anything else
    welcomed = False

    try:
        dataBool = True
        while dataBool == True:
            # first check if we need to send a PING because there's been no activity
            if time.time() - last_activity_time > ping_interval:
                self.PING(clientsocket)  # send PING to client
                last_activity_time = time.time()  # reset last activity time

            # check for timeout
            if time.time() - last_activity_time > pong_timeout:
                print(f"No activity from {address} for {pong_timeout} seconds, disconnecting...")
                break  # disconnect the client

            #select to check if there is data available to read on the client socket
            readable, _, _ = select.select([clientsocket], [], [], 5)
            if readable:
                try:

                    data = self.network_handler.receive(clientsocket)  # Use the Network_Handler's receive method
                    if data:
                        print(f"Received message from {address}: {data}")

                        # reset last activity time
                        last_activity_time = time.time()

                        # Process other data

                        dataBool = self.processing_data(clientsocket, data, address)
                        
                        client = clients[address]
                        if client.username != None and client.nickname != None and welcomed == False:
                            self.welcomeMessage(clientsocket, client.nickname)
                            welcomed = True 

                    else:
                        print("No data received, closing connection.")
                        break 
                except (socket.error, UnicodeDecodeError) as e:
                    print(data)
                    print(f"Error with getting data: {e}")
                    break 
    finally:
        print("closing")

        for channel_name in channels:
            channels[channel_name].remove_member(clients[address])
            print("members")
            for members in channels[channel_name].members:
                print(members)
        
        message = clients[address].username
        self.quit_message(clientsocket, address, message)
        
        self.network_handler.close_connection(clientsocket) 
        print("Closed connection by", address)

# process data received
 def processing_data(self, clientsocket, data, address):
    print("data received:", data)
    lines = data.splitlines()
    client = clients[address]
    
    for line in lines:  # handle multiple lines
        
        #handling user command
        if line.startswith('USER'):
            client.set_username(line)

        # cap command
        elif line.startswith('CAP'):
            pass  
        
        #handling ping command 
        elif line.startswith('PING'):
            self.PONG(clientsocket, line)

        #handling nick command 
        elif line.startswith('NICK'):
            client.handle_nickname(clientsocket, address, line)
        
        #handling pong command
        elif line.startswith('PONG'):  # respond to PONG
            print(f"PONG received from {address}")
            last_pong_time = time.time()  # reset the pong time when PONG received

        #handling channel joining
        elif line.startswith('JOIN'):
            channel_name = line.split()[1]
            # if there are multiple channel names, split on commas
            if len(channel_name.split(",")) > 1:
                all_channel_names = channel_name.split(",")
                for channel_name in all_channel_names:
                    self.join_channel(clientsocket, address, channel_name)
            else:
                self.join_channel(clientsocket, address, channel_name)

        # handle leaving channel
        elif line.startswith('PART'):
            channel_name = line.split()[1]
            self.leave_channel(clientsocket, address, channel_name)
        
        #handling messages
        elif line.startswith('PRIVMSG'):
            self.handle_privmsg(line, clientsocket, address)

        #handling quit 
        elif line.startswith('QUIT'):
            # close the server
            #self.quit_message(clientsocket, address, line)

            '''if len(line.split(":")) > 1:
                message = line.split(":")[1]
            else:
                message = clients[address].username
            quit_message(clientsocket, address, message)'''

            return False
        
        elif line.startswith('MODE'):
            # channel mode message
            self.mode_message(line, clientsocket, address)

        elif line.startswith('WHO'):
            channel_name = line.split()[1]
            self.who_reply(channel_name, address,clientsocket)       
        else:
            # Unknown command if it is not in the list of known ones
            error_message = f":{self.hostname} 421 * {line} :Unknown command"
            self.network_handler.send(clientsocket, error_message)
    return True 

# send PING message
 def PING(self, client):
    try:
        print("PING")
        # Create the PING message
        ping_message = f"PING {self.hostname}"
        network_handler.send(client, ping_message)
        time.sleep(10)
        #print("PING sent to", client.getpeername())
    except socket.error as e: 
        print(f"error sending PING: {e}")

# send PONG message
 def PONG(self, clientsocket, line):
    response = f":{self.hostname} PONG {self.hostname} :{line.split()[1]}"
    network_handler.send(clientsocket, response)
    print(f"Sent: {response}")

 # display a welcome message to the user
 # created a list of all the messages that show at the start of the connection
 def welcomeMessage(self, clientsocket, nickname):
    
    hostname = self.hostname  # get the server hostname
    # displays welcome messages
    welcomeMessages =  [
        f":{hostname} 001 {nickname} :Hi, welcome to IRC",
        f":{hostname} 002 {nickname} :Your host is {hostname}, running version 1",
        f":{hostname} 003 {nickname} :This server was created sometime",
        f":{hostname} 004 {nickname} :{hostname} version 1",
        f":{hostname} 251 {nickname} :There are 1 users and 0 services on 1 server",
        f":{hostname} 422 {nickname} :MOTD File is missing"
    ]
     # send each welcome message to the client
    for message in welcomeMessages:
        if self.is_valid_message(message): # use the validation function before sending
            print(f"Sending valid message: {message}")
            #clientsocket.sendall(f"{message}\r\n".encode('utf-8'))
            network_handler.send(clientsocket, message)
        else:
            print(f"Garbage message detected: {message}")
            continue


 def is_valid_message(self, message):
    # checks if the message matches the exact IRC message format:
    # e.g. :hostname 001 nickname :Welcome to the IRC server

    # the regex pattern for the message format
    pattern = r'^:(\S+) (\d{3}) (\S+) :(.+)$'
    
    # compare message against the pattern
    match = re.match(pattern, message)
    
    if match:
        return True
    else:
        return False

# reply to the MODE command
 def mode_message(self, line, clientsocket, address):
     # channel mode
        channel_name = line.split()[1]
        channel_mode_message = f":{self.hostname} 324 {clients[address].nickname} {channel_name} :+"
        network_handler.send(clientsocket, channel_mode_message)


 def quit_message(self, clientsocket, address, message):
  
    quitmessage = f":{clients[address].nickname}!{clients[address].username}@{HOST} QUIT :{message}"
    print(quitmessage)
    # send quit message to others on the server
    for addr, client in clients.items():
        if client.socket != clientsocket: # don't send the message to the one that is quitting
            client.socket.send(quitmessage.encode("utf-8"))
    del clients[address]
    # send quit message to others on the server

 def join_channel(self, clientsocket, address, channel_name):
    global channels

    #if channel not in list of channels, make a new channel and add to the dictionary
    if channel_name not in channels:
        channels[channel_name] = Channel(channel_name)
        channels[channel_name].topic = f"Welcome to {channel_name}"
        channels[channel_name].operator = clients[address].nickname # set channel operator to first joined

    channel = channels[channel_name] #getting channel from dictionary 
    client = clients[address]

    #client joins channel
    if channel.add_member(client):
        # call function to actually join channel
        self.join_channel_messages(clientsocket, channel_name, channel, address)

    else:
        print(f"Failed to add {clients[address].nickname} to {channel_name}")  
    

 #for local client channel messages
 def join_channel_messages(self, clientsocket, channel_name, channel, address):

    # actually join the channel
    client = clients[address]
    join_message = f":{client.nickname}!{client.username}@{client.clientAddress[0]} JOIN {channel.name}"

    # send join channel message to all members in the channel to notify them 
    for member in channel.members:
        #member.socket.send(join_message.encode('utf-8'))
        network_handler.send(member.socket, join_message)  # Use network handler to send message

    #channel topic
    topic_message = f":{self.hostname} 331 {clients[address].nickname} {channel_name} :No topic is set"
    network_handler.send(clientsocket, topic_message)

    names_list = " ".join([client.nickname for client in channel.members if client.nickname])  # making sure nickname is not None

    names_message = f":{self.hostname} 353 {client.nickname} = {channel_name} :{names_list}"
    network_handler.send(clientsocket, names_message)

    #end of names list
    end_names_message = f":{self.hostname} 366 {clients[address].nickname} {channel_name} :End of NAMES list"
    network_handler.send(clientsocket, end_names_message)

 # reply to the client issuing a WHO #channel_name
 def who_reply(self, channel_name, address,clientsocket):
    channel = channels[channel_name]
    print(f"nick {clients[address].nickname}, address {address}" )
    for member in channel.members:
        who_message = f":{self.hostname} 352 {clients[address].nickname} {channel.name} {clients[address].username} {address[0]} {self.hostname} {member.nickname} H :0 realname"
        network_handler.send(clientsocket, who_message)  
    end_message = f":{self.hostname} 315 {clients[address].nickname} {channel.name} :End of WHO list"
    network_handler.send(clientsocket, end_message)  


 def leave_channel(self, clientsocket, address, channel_name, reason="Leaving"):
    client = clients.get(address)  #fetch client

    if not client:
        print("Client not found.")
        return

    # check channel exists
    if channel_name in channels:
        channel = channels[channel_name]

        leave_message = f":{client.nickname}!{client.username}@{client.clientAddress[0]} PART {channel.name} :{reason}" 
        if client in channel.members:
            for member in channel.members:
                network_handler.send(member.socket, leave_message) 
            channel.remove_member(client)
            print(f"{client.nickname} has left {channel_name}")
        else:
            error_message = f":{self.hostname} 442 {channel_name} :You're not on that channel"
            network_handler.send(clientsocket, error_message) 
    else:
        error_message = f":{self.hostname} 403 {channel_name} :No such channel"
        network_handler.send(clientsocket, error_message)  # Use network handler to send error message

 # decide how to handle the private message command
 def handle_privmsg(self, line, clientsocket, address):
    parts = line.split(' ', 2)
    if len(parts) < 3:
        # no message was given
        error_message = f":{self.hostname} 412 {clients[address].nickname} :No message to send"
        network_handler.send(clientsocket, error_message)
        return True
            
    receiver = parts[1]
    message = parts[2]
    if receiver.startswith('#'):  # it's a message to a channel
        if receiver in channels:
            clients[address].send_channel_message(receiver, message)  # call the method in Client class
        else:
            error_message = f":{self.hostname} 403 {clients[address].nickname} {receiver} :No such channel"
            network_handler.send(clientsocket, error_message)
    else:  # it's a private message to a user
        final_message = message
          
        clients[address].send_private_message(receiver, final_message)  # call the method in Client class

#CLIENT CLASS
class Client:
    def __init__(self, clientsocket, clientAddress, hostname):  # initialise the client class with socket and address
        self.socket = clientsocket
        self.clientAddress = clientAddress
        self.username = None
        self.nickname = None
        self.hostname = hostname
        self.network_handler = network_handler


    # set username
    def set_username(self, username_line):
        
        split = username_line.split()
        user = split.index('USER')
        username = split[user + 1]  # username will be after USER
        self.username = username
        print("username is changing: ", self.username)

    # handle nickname command
    def handle_nickname(self, clientsocket, address, line):
        parts = line.split()
        current_nickname = self.nickname
        if len(parts) > 1:
            nickname = parts[1]
            if self.check_other_nicknames(clientsocket, address, nickname): # if username is not already in use
                if self.valid_nickname_check(nickname): # if username is valid
                    name_change_message = f":{current_nickname}!{clients[address].username}@{HOST} NICK :{nickname}"
                    network_handler.send(clientsocket, name_change_message)
                    self.nickname = nickname
                else:
                    error_message = f":{self.hostname} 432 * {nickname} :Erroneous Nickname"
                    network_handler.send(clientsocket, error_message)
        else: 
            # line only contained NICK, so no nickname was given  
            error_message = f":{self.hostname} 431 * :No nickname given"
            network_handler.send(clientsocket, error_message)

    # check a nickname to make sure it is valid
    def valid_nickname_check(self, nickname):
        #IRC standard: nick has to start with letter and contain letters, digits, -, and _
        return re.match(r'^[A-Za-z][A-Za-z0-9\-_]*$', nickname) is not None

    def check_other_nicknames(self, clientsocket, address, nickname):
        
        with client_lock:
            #checking if current client is in dictionary
            current_client = self
            if current_client is None:
                print(f"No client found for address {address}. This shouldn't happen right after connection and registration.")
                return False  # Early exit if no client is found to prevent further errors

            #if current client sets nickname to same value, ignore
            if self.nickname == nickname:
                same_nick_message = f":{self.hostname} NOTICE {nickname} :You have already set your nickname to {nickname}"
                network_handler.send(clientsocket, same_nick_message)
                return False
            
            #checking other clients for nickname clashes
            for addr, client_info in clients.items():
                if client_info.nickname == nickname and addr != address:
                    error_message = f":{self.hostname} 433 * {nickname} :Nickname is already in use"
                    network_handler.send(clientsocket, error_message)
                    return False

            return True     #no issues set nickname
    
    def send_private_message(self, receiver, message):
        with client_lock:
            found = False
            for addr, client in clients.items():
                if client.nickname == receiver:
                    found = True
                    sender_nickname = self.nickname
                    private_message = f":{sender_nickname}!{self.username}@{HOST} PRIVMSG {receiver} {message}"
                    network_handler.send(client.socket, private_message)
                    break
            
            if not found:
                error_message = f":{self.hostname} 401 {self.nickname} {receiver} :No such nick"
                network_handler.send(self.socket, error_message)

    def send_channel_message(self, channel_name, message):
        with client_lock:
            if channel_name in channels:  # check if the channel exists
                channel = channels[channel_name]
                if self in channel.members: # check if the client is a member of the channel
                    for member in channel.members:    # send message to all memebers in the channel
                        if member.socket != self.socket:  # don't send the message back to the sender
                            channel_message = f":{self.nickname}!{self.username}@{HOST} PRIVMSG {channel_name} {message}"
                            network_handler.send(member.socket, channel_message)
                else:
                    error_message = f":{self.hostname} 442 {channel_name} :You're not on that channel"
                    network_handler.send(self.socket, error_message)  
            else:
                error_message = f":{self.hostname} 403 {self.nickname} {channel_name} :No such channel"
                network_handler.send(self.socket, error_message)
        
#CHANNEL CLASS

class Channel:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.topic = None
        self.operator = None

    # add member to list of members if not already present
    def add_member(self, client):
        if client not in self.members:
            self.members.append(client)
            return True
        return False

    def remove_member(self, client):
        if client in self.members:
            self.members.remove(client)
            return True
        return False
    
network_handler = Network_Handler()
network_handler.connect()