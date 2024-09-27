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
                    print(f"Error with getting data: {e}")
                    break 
    finally:
        clientsocket.close()
        with client_lock:
            del clients[clientsocket]
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
        #handling pong command
        elif 'PONG' in line:  # respond to PONG
            print(f"PONG received from {address}")
            last_pong_time = time.time()  # reset the pong time when PONG received
        #handling quit 
        elif line.startswith('QUIT'):
            # close the server
            
            if len(line.split(":")) > 1: # if there is a quit message
                quitmessage = "Disconnected connection from " + address[0]+ ":" + str(address[1]) +" (" + line.split(":")[1] + ")"
            else:
                quitmessage = "Disconnected connection from " + address[0] + ":" + str(address[1]) + " (" + clients[address].username + ")"
            print(quitmessage)
            return False
            
        else:
            # Unknown command if it is not in the list of known ones
            error_message = f":{socket.gethostname()} 421 * {line} :Unknown command\r\n"
            clientsocket.send(error_message.encode())
    return True 

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

Server.start_server()