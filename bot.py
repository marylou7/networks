import socket
import time

botSock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

serverName = 'localHost IPv6'

HOST = '::1' #host name
PORT = 6667 #port number
print(socket.gethostname())
NICK = 'Ludovic' #sets default nickname for bot

botSock.connect((HOST, PORT)) #bot connects to correct server


# VVV now antiquated code from initial attempts to connect bot to hexchat VVV
"""
botSock.send(bytes("USER " + NICK + " " + NICK + " " + NICK + " " + NICK + " :this is my bot.n", "UTF-8"))
time.sleep(0.5)
botSock.send(bytes('NICK ' + NICK + 'n', 'UTF-8')) 
time.sleep(0.5)
botSock.send(bytes('JOIN #testn', 'UTF-8'))
time.sleep(0.5)
"""

def log_in():
    botSock.send(bytes("CAP LS 302\r\n", "UTF-8")) #CAP command used for sign in, idk what this does but its the lynch pin holding the sign in protocol together apparently
    time.sleep(0.01)
    botSock.send(bytes("NICK " + NICK + "\r\n", "UTF-8")) #nickname is requested
    botSock.send(bytes("USER " + NICK + " 0 * :realname\r\n", "UTF-8")) #nickname is given to the bot
    time.sleep(0.1)
    botSock.send(bytes("CAP END\r\n", 'UTF-8')) #close CAP
    time.sleep(0.1)
    botSock.send(bytes("JOIN #test\r\n", "UTF-8")) #test channel is joined
    time.sleep(0.1)

    # ^^^ sleeps used to break commands into seperate lines and wait for a response if neccesary

def getText():
    text = botSock.recv(2040) #reads text sent by server to the bot. This will be expanded to do the pre generated responses to user messages etc.  
    if text.find(bytes('PING', 'UTF-8')) != -1: #if the text is a ping
        botSock.send(bytes('PONG ' + socket.gethostname() + '\r\n', 'UTF-8')) #replies with a pong
        print("PONG sent to server") #check if PONG is sent
    return text

def sendMsg(message, target):
    botSock.send(bytes('PRIVMSG ' + target + ' : ' + message + '\r\n', "UTF-8"))

#def sendIRC(message):
    #botSock.send(bytes(message + '\r\n', 'UTF-8')) functions that either don't work or currently aren't in use

#def joinChannel(channel):
    #botSock.send(bytes('JOIN ' + channel + '\r\n', 'UTF-8'))

#def ping():
    #botSock.send(bytes('PING LAG558571194\r\n', 'UTF-8'))


# Retaining the initial information sent by miniircd about the channel and its users
def storeInitialInfo():
    initialInfo = getText() #initial info is stored in the variable 'initialInfo'

def getInitialInfo():
    return getInitialInfo

def getHostName():
    return socket.gethostname()

def getUsers():
    # use NAMES command to get all nicknames that are visible on the channel 'test'
    botSock.send(bytes("NAMES #test\r\n", "UTF-8"))
    users = getText()
    return users


log_in()
storeInitialInfo()


sendMsg("Obtenez un enfant incendié", "#test") # sends a message to the test channel

#print(getUsers())



while 1: #while loop prevents bot from disconnecting once it runs out of preset commands
    text = getText()
    print(text) #any recieved text is printed for debugging purposes

