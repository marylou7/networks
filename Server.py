import socket 
import re
import threading
import time
import select


'''Pings - server sends pings at regular intervals
    Server should not repsond to pings but rely on pings coming from the other end to ensure connection is alive
    if it doesn't get a response, it should then disconnect'''

# create global variables
HOST = "::1" # IPv6 connection 
PORT = 6667 #IRC port
clients = {} # store clients in dictinary

#server socket
def start_server():

#AF.INET6 sosocket uses IPv6
#SOCK stream so socket uses TCP

    try:
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        print("socket created")
    except socket.err as err:
        print("error creating socket")

    server.bind((HOST, PORT))
    print ("socket binded to %s" %(PORT)) 
    server.listen(5) #accepting incoming connections
    print("socket listening")
   # print("IP: " + socket.gethostbyname(socket.gethostname()))

    # loop to keep looping until interrupted
    while True:
        try: 
            clientsocket, address = server.accept() #accepting incoming connection 
            print("Accepted connection from" , address)

            client = Client(clientsocket, address)  # Create a new client instance
            clients[address] = client  # store client info
            #clients[clientsocket] = {'address': address, 'nickname':None, 'registered': False}  #?
            #instead of breaking loop we have to continue handling for more connections, better done now than later.
            handling_client(clientsocket, address) 
        except Exception as e:
            print(f"error while handling client: {e}")
    

def handling_client(clientsocket, address):
    print("handling_client called for:", clientsocket.getpeername())  # checking which client is connected
    
    last_activity_time = time.time()  # trracks the last time we received anything from client
    ping_interval = 20  # time for sending PING if no activity from the client
    pong_timeout = 60  # timeout for waiting for PONG or anything else
    
    try:
        while True:
            # first check if we need to send a PING because there's been no activity
            if time.time() - last_activity_time > ping_interval:
                PING(clientsocket)  # send PING to client
                last_activity_time = time.time()  # reset last activity time

            # check for timeout
            if time.time() - last_activity_time > pong_timeout:
                print(f"No activity from {address} for {pong_timeout} seconds, disconnecting...")
                break  # disconnect the client
            
            readable, _, _ = select.select([clientsocket], [], [], 5)
            if readable:
                try:
                    data = clientsocket.recv(1024)
                    if data:
                        message = parse_message(data)
                        print(f"Received message from {address}: {message}")

                        # reset last activity time
                        last_activity_time = time.time()
                        
                        # Process other data
                        processing_data(clientsocket, message, address)
                    else:
                        print("No data received, closing connection.")
                        break 
                except (socket.error, UnicodeDecodeError) as e:
                    print(f"Error with getting data: {e}")
                    break 
    finally:
        clientsocket.close()
        print("Closed connection by", address)
        del clients[address]

def processing_data(clientsocket, data, address):
    print("data received:", data)
    lines = data.splitlines()
    
    for line in lines:  # handle multiple lines
        if 'USER' in line:
            split = line.split()
            user = split.index('USER')
            username = split[user + 1]  # nickname will be after USER
            clients[address].username = username
        
        elif 'CAP' in line:
            pass  # Handle CAP if needed
        
        elif 'PING' in line:
            response = f":{socket.gethostname()} PONG {socket.gethostname()} :{line.split()[1]}"
            clientsocket.sendall(f"{response}\r\n".encode('utf-8'))
            print(f"Sent: {response}")

        elif 'NICK' in line:
            split = line.split()
            nick = split.index('NICK')
            nickname = split[nick + 1]  # nickname will be after NICK
            if not check_other_nicknames(clientsocket, nickname):
                return
            if not valid_nickname_check(nickname):
                invalid_nickname_feedback(clientsocket, nickname)
                return
             # if it is a valid nickname, change it, checking first whether it is a setting up nickname, or a change later
            if clients[address].nickname is None:  # if nickname has not already been set
                welcomeMessage(clientsocket, nickname)  # call function to display welcome message
                clients[address].nickname = nickname
            else:
                namechange = f":{clients[address].nickname}!{clients[address].username}@{HOST} NICK {nickname}"
                clientsocket.send(f"{namechange}\r\n".encode('utf-8'))
                clients[address].nickname = nickname
        
        elif 'PONG' in line:  # respond to PONG
            print(f"PONG received from {address}")
            last_pong_time = time.time()  # reset the pong time when PONG received
            
        else:
            # Unknown command if it is not in the list of known ones
            error_message = f":{socket.gethostname()} 421 * {line} :Unknown command\r\n"
            clientsocket.send(error_message.encode())

        # idk what this is and whether we need it? commenting it out for now
        ''' # ignoring initial HexChat nickname and handling manual one
            if not clients[clientsocket].get('initial_nick_set'):

                clients[clientsocket]['initial_nick_set'] = True
                print(f"ignoring nickname '{nickname}' ignored")
            else:
        # setting manually changed nickname
                clients[clientsocket]['nickname'] = nickname
                print(f"Manual nickname set to {nickname}")

                # sending welcome message after manual nickname is set
                if clients[clientsocket].get('registered') is False: 

                    welcomeMessage(clientsocket, clients[clientsocket]['nickname'])
                    clients[clientsocket]['registered'] = True  
                    print(f"Client {clients[clientsocket]['nickname']} is now registered.")

        # changing manual nickname after registration
        if clients[clientsocket].get('registered') and 'NICK' in line:
            new_nickname = line.split()[1]

            if new_nickname != clients[clientsocket]['nickname']:  # if new nickname
                clients[clientsocket]['nickname'] = new_nickname
                print(f"Nickname changed to {new_nickname}")'''
 
     

# check a nickname to make sure it is valid
def valid_nickname_check(nickname):
    #IRC standard: nick has to start with letter and contain letters, digits, -, and _
    return re.match(r'^[A-Za-z][A-Za-z0-9\-_]*$', nickname) is not None

# check nickname against other nicknames on the server
def check_other_nicknames(clientsocket, nickname):
    # loop through all nicknames of clients in the dictionary
    if bool(clients):
        for x in clients.values():
            #print(x.nickname)
            # if given nickname matches an already given nickanme
            if nickname == x.nickname:
                error_message = f":{socket.gethostname()} 433 * {nickname} :Nickname is already in use\r\n"
                clientsocket.send(error_message.encode())
                return False
    return True
    

# erroneous nickname error
def invalid_nickname_feedback(clientsocket, nickname):
    error_message = f":{socket.gethostname()} 432 * {nickname} :Erroneous Nickname\r\n"
    clientsocket.send(error_message.encode())

def PING(client):
    try:
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
        f":{hostname} 004 {nickname} {hostname} version 1",
        f":{hostname} 251 {nickname} :There are 1 users and 0 services on 1 server",
        f":{hostname} 422 {nickname} :MOTD File is missing"
    ]
    
     # send each welcome message to the client
    for message in welcomeMessages:
        clientsocket.sendall(f"{message}\r\n".encode('utf-8'))
      
      
        
# client connection 
# client choosing username and real name
#client join channels 


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
        
#CHANNEL CLASS

#client messages
#client private messages 

start_server()