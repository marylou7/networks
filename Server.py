import socket 


HOST = "::" # IPv6 connection 
PORT = "6667" #IRC port


#server socket

    

def start_server():

#AF.INET6 sosocket uses IPv6
#SOCK stream so socket uses TCP

    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5) #accepting incoming connections

    while True:
        #accepting incoming connection
        client_socket, address = server.accept()
        #threading?

# client connection 
    # client choosing username and real name



#client join channels 

#client messages


#client private messages 
