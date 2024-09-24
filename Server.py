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

    # loop to keep looping until interrupted
    while True:
        
        #accepting incoming connection 
        # client socket is the socket the connection came from
        clientsocket, address = server.accept()
        print("Accepted connection from" , address)
        break

    # read any data from the client socket
    # need to parse it to do things with it
    while 1:
        data = clientsocket.recv(1024)
        #print(data.decode())

        # getting the nickname - i know we do it other places but just for now to use it here
        if data.find(bytes('NICK', 'UTF-8')) != -1: #if the text contains a nickname
            
            split = data.decode().split()
            nickname = split[1]
            welcomeMessage(clientsocket, nickname) # call function to display welcome message

        # PING
        PING(clientsocket)
        
        # check for a response
        if data.find(bytes('PONG', 'UTF-8')) != -1: #if the text is a ping
           pass

        if not data: break

# ping every 10 seconds
def PING(client):
    client.send(bytes('PING ' + socket.gethostname() + '\r\n', 'UTF-8'))
    time.sleep(10)

# display a welcome message to the user
def welcomeMessage(clientsocket, nickname):
    # displays welcome message
    welcomeMessage =  ":" + socket.gethostname() + " 001 " + nickname + " :Welcome to our IRC server\r\n"
    #print(welcomeMessage)
    clientsocket.send(welcomeMessage.encode())
      
      
        
# client connection 
    # client choosing username and real name



#client join channels 


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

#client messages


#client private messages 

start_server()