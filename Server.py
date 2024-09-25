import socket 
import re
import threading
import time
import select

HOST = "::1" # IPv6 connection 
PORT = 6667 #IRC port

clients = {}


#CLIENT CLASS
class Client:
    def initialise(self, socket, clientAddress):
        
        self.socket = socket
        self.clientAddress = clientAddress
        self.username = None
        self.nickname = None
    
    def set_client_info(self, username, nickname):
        
        self.username
        self.nickname

#CHANNEL CLASS


#server socket

def start_server():

#AF.INET6 sosocket uses IPv6
#SOCK stream so socket uses TCP

    try:
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        print("socket created")
        server.bind((HOST, PORT))
        print ("socket binded to %s" %(PORT)) 
        server.listen(5) #accepting incoming connections
        print("socket listening")
    except socket.err as err:
        print("error creating socket")
        return

   # print("IP: " + socket.gethostbyname(socket.gethostname()))

    # loop to keep looping until interrupted
    while True:
        try: 
            clientsocket, address = server.accept() #accepting incoming connection 
            print("Accepted connection from" , address)

            clients[clientsocket] = {'address': address, 'nickname':None, 'registered': False}         #to store client information

            #instead of breaking loop we have to continue handling for more data/new nicknames, better done now than later.
            handling_client(clientsocket) 
        except Exception as e:
            print(f"error while handling client: {e}")


def handling_client(clientsocket):
        print("handling_client called for:", clientsocket.getpeername())  # checkingwhich client is connected
        last_ping_time = time.time()

        try:
            while True:   

                readable, _, _ = select.select([clientsocket], [], [], 5)
                if readable:
                    try:
                        data = clientsocket.recv(1024).decode().strip()     # read any data from the client socket  # need to parse it to do things with it

                    #print(data.decode())
                        if  data:
         #               print(f"Data received from {clientsocket.getpeername()}: '{data}'")
                            processing_data(clientsocket, data)
                        else:
                            print("no data received, closing connection.")
                            break 
                    except (socket.error, UnicodeDecodeError) as e:
                        print(f"error with getting data: {e}")
                        break
            
                else:
                    print("no readable data from client, checking again...")                 #no data ready to be read

            if time.time() - last_ping_time > 10:
                    PING(clientsocket)  # sending PING to client
                    last_ping_time = time.time()  # updating last ping time
            
        finally:
            clientsocket.close()
            print("closed connection by", clients[clients[clientsocket]['address']])
            del clients[clientsocket]


# to cover k2
def valid_nickname_check(nickname):
    #IRC standard: nick has to start with letter and contain letters, digits, -, and _

    return re.match(r'^[A-Za-z][A-Za-z0-9\-_]*$', nickname) is not None

def invalid_nickname_feedback(clientsocket, nickname):
    error_message = f":{socket.gethostname()} 432 * {nickname} :Erroneous Nickname\r\n"
    clientsocket.send(error_message.encode())


def processing_data(clientsocket, data):
    print("data received:", data)
    lines = data.splitlines()

    for line in lines:  # handle multiple lines
        if 'NICK' in line:
            nickname = line.split()[1]
            
            if not valid_nickname_check(nickname):
                invalid_nickname_feedback(clientsocket, nickname)
                return

        # ignoring initial HexChat nickname and handling manual one
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
                print(f"Nickname changed to {new_nickname}")
 
 #  PONG handling
        if 'PONG' in line:  # comparing strings with strings
            print("PONG received")


# ping every 10 seconds
def PING(client):
    try:
        client.send(bytes('PING ' + socket.gethostname() + '\r\n', 'UTF-8'))
        print("PING sent to", client.getpeername())
    except socket.error as e: 
        print(f"error sending PING: {e}")



# display a welcome message to the user
def welcomeMessage(clientsocket, nickname):
    if nickname:
    # displays welcome message
        server_hostname = socket.gethostname()
        print (f"server hostname: {server_hostname}")
        welcomeMessage = f":{server_hostname} 001 {nickname} :Welcome to our IRC server\r\n"
    #print(welcomeMessage)
        try:
            clientsocket.send(welcomeMessage.encode())
            print (f"sent welcome message to {nickname}")
        except socket.error as e:
            print(f"welcome message error: {e}")

    else:
        print("tried to send welcome message with empty nick")
      
    
    
#client messages

#client join channels 

#client private messages 

# client connection 
    # client choosing username and real name

start_server()




