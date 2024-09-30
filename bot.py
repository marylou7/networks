import socket
import time
import random

botSock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

serverName = 'localHost IPv6'

HOST = '::1' #host name
PORT = 6667 #port number
print(socket.gethostname())
NICK = 'Ludovic' #sets default nickname for bot
#global CHANNEL
CHANNEL = ""

botSock.connect((HOST, PORT)) #bot connects to correct server


def log_in():
    sendIRC("CAP LS 302") #CAP command used for sign in, idk what this does but its the lynch pin holding the sign in protocol together apparently
    time.sleep(0.01)
    sendIRC("NICK " + NICK) #nickname is requested
    sendIRC("USER " + NICK + " 0 * :realname") #nickname is given to the bot
    time.sleep(0.1)
    sendIRC("CAP END") #close CAP
    time.sleep(0.1)
    joinChannel('#test')
    time.sleep(0.1)

    # ^^^ sleeps used to break commands into seperate lines and wait for a response if neccesary


def sendMsg(message, target):
    sendIRC('PRIVMSG ' + target + ' :' + message)

def getText():
    text = botSock.recv(2040) #reads text sent by server to the bot. This will be expanded to do the pre generated responses to user messages etc. 
    text = text.decode() #converts the bytes to string
    if text.find('PING') != -1: #if the text is a ping
        sendIRC('PONG ' + socket.gethostname()) #replies with a pong
        print("PONG sent to server") #check if PONG is sent
    elif text.find('PRIVMSG ' + CHANNEL + ' :!hello') != -1:
        splitText = text.split(':')
        splitText = splitText[1].split('!') # splits the string to find the user name of the sender
        name = splitText[0]
        if random.choice([0,1]) == 0: # 50/50 chance to respond with one of two greetings
            sendMsg('Salut, ' + name + '!', CHANNEL)
            print('Salut, ' + name + '!')
        else:
            sendMsg('Bonjour, ' + name + '!', CHANNEL)
            print('Bonjour, ' + name + '!')
    elif text.find('PRIVMSG ' + CHANNEL + ' :!slap') != -1:
        #here we will randomly choose a user
        sendMsg("TEMPUSER, tu as été giflé avec une truite !", CHANNEL)
    elif text.find('PRIVMSG ' + NICK) != -1:
        splitText = text.split(':')
        splitText = splitText[1].split('!') # splits the string to find the user name of the sender
        name = splitText[0]
        sendMsg(getFact(), name)
    return text

def setChannel(channel):
    global CHANNEL
    CHANNEL = channel

def sendIRC(message):
    botSock.send(bytes(message + '\r\n', 'UTF-8'))

def joinChannel(channel):
    sendIRC('JOIN ' + channel) #functions that either don't work or currently aren't in use
    setChannel(channel)

#def ping():
    #botSock.send(bytes('PING LAG558571194\r\n', 'UTF-8'))

def getFact():
    line = random.choice([0,49])
    with open('facts.txt', 'r') as file:
        fact = file.readline(line)
    return fact

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


log_in()
storeInitialInfo()

sendMsg("Obtenez un enfant incendié", "#test") # sends a message to the test channel

while 1: #while loop prevents bot from disconnecting once it runs out of preset commands
    text = getText()
    print(text) #any recieved text is printed for debugging purposes

