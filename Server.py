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

class Server:

 #server socket
 def start_server():
     
 # loop to keep looping until interrupted
     try:
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)   #AF.INET6 sosocket uses IPv6  #SOCK stream so socket uses TCP
        print("socket created")
        server.bind((HOST, PORT)) # binding  socket to specified HOST & PORT
        print ("socket binded to %s" %(PORT)) 
        server.listen(5) #accepting incoming connections
        print("socket listening")
        # print("IP: " + socket.gethostbyname(socket.gethostname()))
        while True:
            try: 
                clientsocket, address = server.accept() #accepting incoming connection 
                print("Accepted connection from" , address)

                client = Client(clientsocket, address)  # Create a new client instance

                # use of client_lock to making sure the thread is safe to access to clients dictionary
                with client_lock:
                    clients[address] = client  # store client info
                #making a new thread to handle client, to allow for multiple concurrent clients
                newthread = threading.Thread(target=handling_client, args=(clientsocket,address))
                newthread.daemon = True #making sure thread exits when main program does
                newthread.start() #new thread to handle clients

                #clients[clientsocket] = {'address': address, 'nickname':None, 'registered': False}  #?
                #handling_client(clientsocket, address) 

            except Exception as e:
                print(f"Error while handling client: {e}")   

     except Exception as e:
        print("Error creating socket:", e)
        
     finally:
            server.close()
            print("Server closed")      

def handling_client(clientsocket, address):
    print("handling_client called for:", clientsocket.getpeername())  # checking which client is connected
    
    last_activity_time = time.time()  # tracks the last time we received anything from client
    ping_interval = 20  # time for sending PING if no activity from the client
    pong_timeout = 60  # timeout for waiting for PONG or anything else
    
    try:
        dataBool = True
        while dataBool == True:
            # first check if we need to send a PING because there's been no activity
            if time.time() - last_activity_time > ping_interval:
                PING(clientsocket)  # send PING to client
                last_activity_time = time.time()  # reset last activity time

            # check for timeout
            if time.time() - last_activity_time > pong_timeout:
                print(f"No activity from {address} for {pong_timeout} seconds, disconnecting...")
                break  # disconnect the client
            
            #select to check if there is data available to read on the client socket
            readable, _, _ = select.select([clientsocket], [], [], 5)
            if readable:
                try:
                    data = clientsocket.recv(1024) #data up to 1024
                    if data:
                        message = parse_message(data)
                        print(f"Received message from {address}: {message}")

                        # reset last activity time
                        last_activity_time = time.time()
                        
                        # Process other data
                        dataBool = processing_data(clientsocket, message, address)
                    else:
                        print("No data received, closing connection.")
                        break 
                except (socket.error, UnicodeDecodeError) as e:
                    print(data)
                    print(f"Error with getting data: {e}")
                    break 
    finally:
        with client_lock:
            #if client in clients:
            del clients[address]
        print(clients)
        clientsocket.close()
        print("Closed connection by", address)

def processing_data(clientsocket, data, address):
    print("data received:", data)
    lines = data.splitlines()
    
    for line in lines:  # handle multiple lines
        #handling user command
        if 'USER' in line:
            split = line.split()
            user = split.index('USER')
            username = split[user + 1]  # nickname will be after USER
            clients[address].username = username

        elif 'CAP' in line:
            pass  # Handle CAP if needed
        
        #handling ping command 
        elif 'PING' in line:
            response = f":{socket.gethostname()} PONG {socket.gethostname()} :{line.split()[1]}"
            clientsocket.sendall(f"{response}\r\n".encode('utf-8'))
            print(f"Sent: {response}")

        #handling nick command 
        elif 'NICK' in line:
            parts = line.split()
            if len(parts) > 1:
                nickname = parts[1]
                if check_other_nicknames(clientsocket, address, nickname):
                    if valid_nickname_check(nickname):
                        update_nickname(clientsocket, address, nickname)
                    else:

                        invalid_nickname_feedback(clientsocket, nickname)
            else:   
                error_message = f":{socket.gethostname()} 431 * :No nickname given\r\n"
                clientsocket.sendall(error_message.encode())


        #handling pong command
        elif 'PONG' in line:  # respond to PONG
            print(f"PONG received from {address}")
            last_pong_time = time.time()  # reset the pong time when PONG received

        #handling channel joining
        elif line.startswith('JOIN'):
            channel_name = line.split()[1]
            # if there are multiple channel names, split on commas
            if len(channel_name.split(",")) > 1:
                all_channel_names = channel_name.split(",")
                for channel_name in all_channel_names:
                    join_channel(clientsocket, address, channel_name)
            else:
                join_channel(clientsocket, address, channel_name)

        elif line.startswith('PART'):
            channel_name = line.split()[1]
            leave_channel(clientsocket, address, channel_name)
        
        #handling messages
        elif line.startswith('PRIVMSG'):
             parts = line.split(' ', 2)
             if len(parts) < 3:
                  error_message = f":{socket.gethostname()} 412 {clients[address].nickname} :No message to send\r\n"
                  clientsocket.send(error_message.encode())
                  return True
              
             receiver = parts[1]
             message = parts[2].lstrip(':')  # remove ':' from the message
             if receiver.startswith('#'):  # it's a message to a channel
                 if receiver in channels:
                     clients[address].send_channel_message(receiver, message)  # call the method in Client class
                 else:
                    error_message = f":{socket.gethostname()} 403 {clients[address].nickname} {receiver} :No such channel\r\n"
                    clientsocket.send(error_message.encode())
             else:  # it's a private message to a user
                clients[address].send_private_message(receiver, message)  # call the method in Client class

        #handling quit 
        elif line.startswith('QUIT'):
            # close the server
            quit(clientsocket, address, line)
            return False
        elif line.startswith('MODE'):
            # channel mode message
             # channel mode
            channel_name = line.split()[1]
            channel_mode_message = f":{socket.gethostname()} 324 {clients[clientsocket.getpeername()].nickname} {channel_name} :+"
            clientsocket.send(channel_mode_message.encode('utf-8') + b'\r\n')
            pass
        elif line.startswith('WHO'):
            channel_name = line.split()[1]
            who_reply(channel_name, address,clientsocket)       
        else:
            # Unknown command if it is not in the list of known ones
            error_message = f":{socket.gethostname()} 421 * {line} :Unknown command\r\n"
            clientsocket.send(error_message.encode())
    return True 


def update_nickname(clientsocket, address, nickname):

    current_nickname = clients[address].nickname

    if current_nickname and current_nickname != nickname:
        name_change_message = f":{current_nickname}!{clients[address].username}@{HOST} NICK :{nickname}\r\n"
        clientsocket.send(name_change_message.encode('utf-8'))
    elif not current_nickname:
        welcomeMessage(clientsocket, nickname)
    clients[address].nickname = nickname



 # check a nickname to make sure it is valid
def valid_nickname_check(nickname):
    #IRC standard: nick has to start with letter and contain letters, digits, -, and _
    return re.match(r'^[A-Za-z][A-Za-z0-9\-_]*$', nickname) is not None

def check_other_nicknames(clientsocket, address, nickname):
    
    with client_lock:
        #checking if current client is in dictionary
        current_client = clients.get(address)
        if current_client is None:
            print(f"No client found for address {address}. This shouldn't happen right after connection and registration.")
            return False  # Early exit if no client is found to prevent further errors

        #if current client sets nickname to same value, ignore
        if current_client.nickname == nickname:
            same_nick_message = f":{socket.gethostname()} NOTICE {nickname} :You have already set your nickname to {nickname}\r\n"
            clientsocket.send(same_nick_message.encode())
            return False
        
        #checking other clients for nickname clashes
        for addr, client_info in clients.items():
            if client_info.nickname == nickname and addr != address:
                error_message = f":{socket.gethostname()} 433 * {nickname} :Nickname is already in use\r\n"
                clientsocket.send(error_message.encode())
                return False

        return True     #no issues set nickname

    
 # erroneous nickname error
def invalid_nickname_feedback(clientsocket, nickname):
    error_message = f":{socket.gethostname()} 432 * {nickname} :Erroneous Nickname\r\n"
    clientsocket.send(error_message.encode())

def PING(client):
    try:
        print("PING")
        client.send(bytes('PING ' + socket.gethostname() + '\r\n', 'UTF-8'))
        time.sleep(10)
        #print("PING sent to", client.getpeername())
    except socket.error as e: 
        print(f"error sending PING: {e}")

 #helper function to parse messages received from socket to strings
def parse_message(data):
    return data.decode('utf-8').strip()

 # display a welcome message to the user
 # created a list of all the messages that show at the start of the connection
def welcomeMessage(clientsocket, nickname):
    
    hostname = socket.gethostname()  # get the server hostname
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
        if is_valid_message(message): # use the validation function before sending
            print(f"Sending valid message: {message}")
            clientsocket.sendall(f"{message}\r\n".encode('utf-8'))
        else:
            print(f"Garbage message detected: {message}")
            continue


def is_valid_message(message):
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

def quit(clientsocket, address, line):

    if len(line.split(":")) > 1: # if there is a quit message
        quitmessage = "Disconnected connection from " + address[0]+ ":" + str(address[1]) +" (" + line.split(":")[1] + ")\r\n"
    else:
        quitmessage = "Disconnected connection from " + address[0] + ":" + str(address[1]) + " (" + clients[address].username + ")\r\n"
    print(quitmessage)
    # send quit message to others on the server

def join_channel(clientsocket, address, channel_name):
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
        join_channel_messages(clientsocket, channel_name, channel, address)

    else:
        print(f"Failed to add {clients[address].nickname} to {channel_name}")  
    

#for local client channel messages
def join_channel_messages(clientsocket, channel_name, channel, address):

    # actually join the channel
    client = clients[address]
    join_message = f":{client.nickname}!{client.username}@{client.clientAddress[0]} JOIN {channel.name}\r\n"

    # send join channel message to all members in the channel to notify them 
    for member in channel.members:
        member.socket.send(join_message.encode('utf-8'))

    #channel topic
    topic_message = f":{socket.gethostname()} 331 {clients[clientsocket.getpeername()].nickname} {channel_name} :No topic is set"
    clientsocket.send(topic_message.encode('utf-8') + b'\r\n')

    names_list = " ".join([client.nickname for client in channel.members if client.nickname])  # making sure nickname is not None

    names_message = f":{socket.gethostname()} 353 {client.nickname} = {channel_name} :{names_list}"
    clientsocket.send(names_message.encode('utf-8') + b'\r\n')

    #end of names list
    end_names_message = f":{socket.gethostname()} 366 {clients[clientsocket.getpeername()].nickname} {channel_name} :End of NAMES list"
    clientsocket.send(end_names_message.encode('utf-8') + b'\r\n')

# for global client channel messages - dont need this - it happens in the function above automatically
'''def notify_members_on_channel(channel,clientsocket, messages):
    for member in channel.members:
        if member.socket != clientsocket:
            member.socket.sendall(f":{socket.gethostname()} NOTICE {channel.name} :{messages}\r\n".encode('utf-8'))'''

# reply to the client issuing a WHO #channel_name
def who_reply(channel_name, address,clientsocket):
    channel = channels[channel_name]
    print(f"nick {clients[address].nickname}, address {address}" )
    for member in channel.members:
        clientsocket.send(f":{socket.gethostname()} 352 {clients[address].nickname} {channel.name} {clients[address].username} {address[0]} {socket.gethostname()} {member.nickname} H :0 realname\r\n".encode('utf-8'))
    clientsocket.send(f":{socket.gethostname()} 315 {clients[address].nickname} {channel.name} :End of WHO list\r\n".encode("utf-8"))


def leave_channel(clientsocket, address, channel_name, reason="Leaving"):
    client = clients.get(address)  #fetch client

    if not client:
        print("Client not found.")
        return

    # check channel exists
    if channel_name in channels:
        channel = channels[channel_name]

        leave_message = f":{client.nickname}!{client.username}@{client.clientAddress[0]} PART {channel.name} :{reason}\r\n" 
        if client in channel.members:
            for member in channel.members:
                member.socket.send(leave_message.encode('utf-8'))
            channel.remove_member(client)
            print(f"{client.nickname} has left {channel_name}")

        else:
            error_message = f":{socket.gethostname()} 442 {channel_name} :You're not on that channel\r\n"
            clientsocket.send(error_message.encode())
    else:
        error_message = f":{socket.gethostname()} 403 {channel_name} :No such channel\r\n"
        clientsocket.send(error_message.encode())









#CLIENT CLASS
class Client:
    def __init__(self, clientsocket, clientAddress):  # initialise the client class with socket and address
        self.socket = clientsocket
        self.clientAddress = clientAddress
        self.username = None
        self.nickname = None
        self.hostname = socket.gethostname()
    
    def set_client_info(self, username, nickname):
        
        self.username
        self.nickname
    
    def send_private_message(self, receiver, message):
        with client_lock:
            found = False
            for addr, client in clients.items():
                if client.nickname == receiver:
                    found = True
                    sender_nickname = self.nickname
                    private_message = f":{sender_nickname} PRIVMSG {receiver} :{message}\r\n"
                    client.socket.send(private_message.encode('utf-8'))
                    break
            
            if not found:
                error_message = f":{socket.gethostname()} 401 {self.nickname} {receiver} :No such nick\r\n"
                self.socket.send(error_message.encode())

    def send_channel_message(self, channel_name, message):
        with client_lock:
            if channel_name in channels:  # check if the channel exists
                channel = channels[channel_name]
                if self in channel.members: # check if the client is a member of the channel
                    for member in channel.members:    # send message to all memebers in the channel
                        if member.socket != self.socket:  # don't send the message back to the sender
                            channel_message = f":{self.nickname} PRIVMSG {channel_name} :{message}\r\n"
                            member.socket.send(channel_message.encode('utf-8'))
                else:
                    error_message = f":{socket.gethostname()} 442 {channel_name} :You're not on that channel\r\n"
                    self.socket.send(error_message.encode())
            else:
                error_message = f":{socket.gethostname()} 403 {self.nickname} {channel_name} :No such channel\r\n"
                self.socket.send(error_message.encode())
        
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
    

Server.start_server()