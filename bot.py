import socket
import time
import random

import sys


botSock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

serverName = 'localHost IPv6'

HOST = '::1' #host name
PORT = 6667 #port number
NICK = 'Ludovic' #sets default nickname for bot
CHANNEL = '#hello'

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

#print(NICK)
#print(PORT)
#print(CHANNEL)

#print(socket.gethostname())

class Bot:
    
    botSock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    global NICK
    NICK = 'Ludovic' #sets default nickname for bot
    
    def __init__(self):
        pass
    
    def getNick():
        global NICK
        return NICK

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

    def sendMsg(message, target):
        botSock.send(bytes('PRIVMSG ' + target + ' : ' + message + '\r\n', "UTF-8"))

    def sendIRC(message):
        botSock.send(bytes(message + '\r\n', 'UTF-8'))

    def getText(self):
        text = botSock.recv(2040) #reads text sent by server to the bot. This will be expanded to do the pre generated responses to user messages etc. 
        text = text.decode() #converts the bytes to string
        if text.find('PING') != -1: #if the text is a ping
            self.sendIRC('PONG ' + socket.gethostname()) #replies with a pong
            print("PONG sent to server") #check if PONG is sent
        elif text.find('PRIVMSG ' + CHANNEL + ' :!hello') != -1:
            splitText = text.split(':')
            splitText = splitText[1].split('!') # splits the string to find the user name of the sender
            name = splitText[0]
            if random.choice([0,1]) == 0: # 50/50 chance to respond with one of two greetings
                self.sendMsg('Salut, ' + name + '!', CHANNEL)
                print('Salut, ' + name + '!')
            else:
                self.sendMsg('Bonjour, ' + name + '!', CHANNEL)
                print('Bonjour, ' + name + '!')
        elif text.find('PRIVMSG ' + CHANNEL + ' :!slap') != -1:
            #here we will randomly choose a user
            self.sendMsg("TEMPUSER, tu as été giflé avec une truite !", CHANNEL)
        elif text.find('PRIVMSG ' + NICK) != -1:
            splitText = text.split(':')
            splitText = splitText[1].split('!') # splits the string to find the user name of the sender
            name = splitText[0]
            self.sendMsg(Bot.getFact(), name)
        return text

    def sendMsg(message, target):
        botSock.send(bytes('PRIVMSG ' + target + ' :' + message + '\r\n', "UTF-8"))

    def sendIRC(message):
        botSock.send(bytes(message + '\r\n', 'UTF-8'))

    def joinChannel(self, channel):
        self.sendIRC('JOIN ' + channel) #functions that either don't work or currently aren't in use
        self.setChannel(channel)

    #def ping():
        #botSock.send(bytes('PING LAG558571194\r\n', 'UTF-8'))

    def getFact():
        lines = open('facts.txt').read().splitlines()
        fact = random.choice(lines)
        print(fact)
        return fact


    # Retaining the initial information sent by miniircd about the channel and its users
    def storeInitialInfo(self):
        initialInfo =self.getText(self) #initial info is stored in the variable 'initialInfo'
        #print(initialInfo)
        return initialInfo

    # function to return host name
    def getHostName():
        return socket.gethostname()

    # function to get users of the channel 'test'
    def returnUsers(self):
        #channelUsers = [] # list of users
        # use NAMES command to get all nicknames that are visible on the channel 'test'
        botSock.send(bytes("WHO #test\r\n", "UTF-8"))
        names =self.getText(self)
        #print(names)
        str(names)
        users = names[3:]
        #print(users)
        index = str(users).find(":")
        #print(index)
        index2 = str(users).find(chr(92))
        #print(chr(92))
        #print(index2)
        users = str(users[index-1:index2-2])
        #print(users)
        users = users[2:-1]
        #print(users)
        channelUsers = list(users.split(" "))
        return channelUsers

    # function to get the channel name
    def getChannel(self):
        # use NAMES command to get all nicknames that are visible on the channel 'test' and the channel name
        botSock.send(bytes("WHO #test\r\n", "UTF-8"))
        names =self.getText(self)
        index = str(names).find("#")
        channel = str(names)
        index1 = channel[index:]
        index2 = str(index1).find(":")
        channelName = channel[index:(index+index2)]
        return channelName
    
    # function to return the channel name
    def returnChannelName(self):
        currentChannel = self.getChannel()
        return currentChannel

try:
    botSock.connect((HOST, PORT))
    Bot.log_in()
    print(Bot.storeInitialInfo(Bot))
    #print(Bot.returnUsers(Bot))

    Bot.sendMsg(f"Bonjour, je m'appelle {Bot.getNick()} et je suis chatbot sur ce serveur", CHANNEL) # sends a message to the test channel
    
    # testing for returning channel + users:
    print(f'Channel name: {Bot.getChannel(Bot)}')
    print(f'Users : {Bot.returnUsers(Bot)}')
    
    while 1: #while loop prevents bot from disconnecting once it runs out of preset commands
        text = Bot.getText(Bot)
        print(text) #any recieved text is printed for debugging purposes
        
except Exception as e:
    print(f"port indisponible ou n'existe pas: {e}")
finally:
    botSock.close()
    print("Au Revoir")