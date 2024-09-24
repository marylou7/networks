import socket 

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

    # loop to keep looping until interrupted
    while True:
        
        #accepting incoming connection 
        # client socket is the socket the connection came from
        clientsocket, address = server.accept()
        clientsocket.send("client connected")
            

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