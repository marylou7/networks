import socket 
import re
import threading
import time

HOST = "::1" # IPv6 connection 
PORT = 6667 #IRC port

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
   
    clients = {} # store clients in dictinary

    # loop to keep looping until interrupted
    while True:
        
        #accepting incoming connection 
        # client socket is the socket the connection came from
        clientsocket, address = server.accept()
        client = Client(clientsocket, address)  # Create a new client instance
        clients[address] = client  # store client info
         
        print("Accepted connection from" , address)
        break

    # read any data from the client socket
    # need to parse it to do things with it
    while 1:
        data = clientsocket.recv(1024)
        #print(data.decode())
        
        message = parse_message(data)
        #print(f"Received: {message}") # to check the data received

        # getting the nickname 
        if data.find(bytes('NICK', 'UTF-8')) != -1: #if the text contains a nickname
            
            split = data.decode().split()
            nick = split.index('NICK')
            nickname = split[nick+1] # nickname will be after NICK
            welcomeMessage(clientsocket, nickname) # call function to display welcome message
            client.nickname = nickname
            #print(client.nickname)
        
        if data.find(bytes('USER', 'UTF-8')) != -1 :# if the text contains a username
            split = data.decode().split()
            user = split.index('USER')
            username = split[user+1] # username will be the one after USER command
            client.username = username
            #print(client.username)

        # PING
        #PING(clientsocket)
        if message.startswith("PING"):
          # get the lag value from the ping message
          lagvalue = message.split()[1]  # lag value after PING
          # create a PONG response using the lag value
          response = f":{client.hostname} PONG {client.hostname} :{lagvalue}"
          clientsocket.sendall(f"{response}\r\n".encode('utf-8'))
          print(f"Sent: {response}")

        # check for a response
        if data.find(bytes('PONG', 'UTF-8')) != -1: #if the text is a ping
           pass

        if not data: break

# ping every 10 seconds
def PING(client):
    client.send(bytes('PING ' + socket.gethostname() + '\r\n', 'UTF-8'))
    time.sleep(10)

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
        #f":{hostname} 251 {nickname} :There are 1 users and 0 services on 1 server",
        #f":{hostname} 422 {nickname} :MOTD File is missing"
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