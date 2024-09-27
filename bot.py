import socket
import time
import sys

botSock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

serverName = 'localHost IPv6'

HOST = '::1' #host name
PORT = 6667 #port number
NICK = 'Ludovic' #sets default nickname for bot

if len(sys.argv) > 0:
    for i in range(1, len(sys.argv)):
        splitText = sys.argv[i].split(" ")
        print(splitText)
        if sys.argv[i].find('port') != -1:
            i += 1
            PORT = int(sys.argv[i])
        elif sys.argv[i].find('name') != -1:
            i += 1
            NICK = str(sys.argv[i])
        elif sys.argv[i].find('channel') != -1:
            i += 1
            CHANNEL = str(sys.argv[i])
        elif sys.argv[i].find('host') != -1:
            i += 1
            HOST = str(sys.argv[i])

print(NICK)
print(PORT)
print(CHANNEL)

print(socket.gethostname())


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
    botSock.send((f":{NICK}001{NICK} :Hi, welcome to IRC server\r\n").encode())
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
    
    initialFile = open("initialInfo.txt","w") # open 'initialInfo.txt' <- this file will store the initial info
    initial = getText()
    initialText = f'Initial information send by miniircd about the channel: {initial} \n'
    #print(f'Initial information send by miniircd about the channel: {initial}')
    initialFile.write(initialText + '\n')
    
    # summarise the initial information (host, channel name, running version, users + services)
    initialFile.write('Summary of the initial information sent by miniircd: \n')
    
    # host:
    host = f'The host is: {socket.gethostname()} \n'
    #print(host)
    initialFile.write(host)
    
    # channel name:
    splitText = initialText.split('#')
    #print(splitText)
    channelSplit = splitText[3]
    slicePlace = channelSplit.find(":")
    channelName = channelSplit[:slicePlace]
    #print(channelName)
    initialFile.write(f'Channel name: {channelName} \n')
    
    # running version:
    splitText = initialText.split(',')
    split2 = splitText[2]
    runSplit = split2.find(":")
    runningVerison = split2[1:runSplit]
    initialFile.write(runningVerison + '\n')
    
    # users + services:
    splitText = initialText.split(':')
    #print(splitText)
    usersServices = splitText[12] + ' ' + splitText[13]
    initialFile.write(usersServices + '\n')
    
    initialFile.close() # closes the initial file

try:
    botSock.connect((HOST, PORT)) #bot connects to correct server

    log_in()
    #storeInitialInfo()

    sendMsg("Obtenez un enfant incendié", "#test") # sends a message to the test channel

    while 1: #while loop prevents bot from disconnecting once it runs out of preset commands
        text = getText()
        print(text) #any recieved text is printed for debugging purposes
except Exception as e:
    print("port indisponible ou n'existe pas")
finally:
    botSock.close()
    print("Au Revoir")