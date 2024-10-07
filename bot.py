import socket
import time
import random

import sys


botSock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

serverName = 'localHost IPv6'

def checkNick(nickname):
    # 1 < nickname <= 15
    flag = False
    
    if len(nickname) == 0:
        # name is too short
        flag = False
        print("Le pseudo saisi est trop court")
    elif len(nickname) <= 15:
        # name is good length
        flag = True
    else:
        # name is too long
        flag = False
        print("Le pseudo saisi est trop long")
        
    # while the flag is false, user must enter a new nickname of correct length
    while flag==False:
        nickname = input("entrez un surnom pour vous-même: ")
        if len(nickname) == 0:
            # name is too short
            flag = False
            print("Le pseudo saisi est trop court")
        elif len(nickname) <= 15:
            # name is good length
            flag = True
        else:
            # name is too long
            flag = False
            print("Le pseudo saisi est trop long")
            
    return nickname

def checkChannel(channelName):
    # 1 < channelName <= 15
    flag = False
    
    if len(channelName) == 0:
        # name is too short
        flag = False
        print("le nom de la chaîne est trop court")
    elif len(channelName) <= 15:
        # name is good length
        flag = True
    else:
        # name is too long
        flag = False
        print("le nom de la chaîne est trop court")
    
    # if the flag is false (aka the entered name is invalid), user must enter a new channelName of correct length
    while flag==False:
        channelName = input("Saisissez le nom de la chaîne que vous souhaitez rejoindre: ")
        if len(channelName) == 0:
            # name is too short
            flag = False
            print("le nom de la chaîne est trop court")
        elif len(channelName) <= 15:
            # name is good length
            flag = True
        else:
            # name is too long
            flag = False
            print("le nom de la chaîne est trop long")
    
    channelName = "#"+channelName
    return channelName

HOST = '::1' #host name
PORT = 6667 #port number
#NICK = 'Ludovic' #sets default nickname for bot
#CHANNEL = '#hello'
nickname = input("entrez un surnom pour vous-même: ")
NICK = checkNick(nickname)
channelName = input("Saisissez le nom de la chaîne que vous souhaitez rejoindre: ")
CHANNEL = checkChannel(channelName)

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
    #global NICK
    #NICK = 'Ludovic' #sets default nickname for bot
    
    def __init__(self, nickname, channel):
        self.nickname = nickname
        self.channel = channel
    
    def returnNick(self):
        return str(self.nickname)
    
    def returnChannel(self):
        return str(self.channel)

    def log_in(self):
        nick = self.returnNick()
        botSock.send(bytes("CAP LS 302\r\n", "UTF-8")) #CAP command used for sign in, idk what this does but its the lynch pin holding the sign in protocol together apparently
        time.sleep(0.01)
        botSock.send(bytes("NICK " + nick + "\r\n", "UTF-8")) #nickname is requested
        botSock.send(bytes("USER " + nick + " 0 * :realname\r\n", "UTF-8")) #nickname is given to the bot
        time.sleep(0.1)
        botSock.send(bytes("CAP END\r\n", 'UTF-8')) #close CAP
        time.sleep(0.1)
        botSock.send(bytes("JOIN " + self.returnChannel() + "\r\n", "UTF-8")) #test channel is joined
        time.sleep(0.1)

    # ^^^ sleeps used to break commands into seperate lines and wait for a response if neccesary

    def sendMsg(message, target):
        botSock.send(bytes('PRIVMSG ' + target + ' : ' + message + '\r\n', "UTF-8"))

    def sendIRC(message):
        botSock.send(bytes(message + '\r\n', 'UTF-8'))

    def getText(self):
        channel = self.returnChannel()
        nick = self.returnNick()
        text = botSock.recv(2040) #reads text sent by server to the bot. This will be expanded to do the pre generated responses to user messages etc. 
        text = text.decode() #converts the bytes to string
        if text.find('PING') != -1: #if the text is a ping
            self.sendIRC('PONG ' + socket.gethostname()) #replies with a pong
            print("PONG sent to server") #check if PONG is sent
        elif text.find('PRIVMSG ' + channel + ' :!hello') != -1:
            splitText = text.split(':')
            splitText = splitText[1].split('!') # splits the string to find the user name of the sender
            name = splitText[0]
            if random.choice([0,1]) == 0: # 50/50 chance to respond with one of two greetings
                self.sendMsg('Salut, ' + name + '!', channel)
                print('Salut, ' + name + '!')
            else:
                self.sendMsg('Bonjour, ' + name + '!', channel)
                print('Bonjour, ' + name + '!')
        elif text.find('PRIVMSG ' + channel + ' :!slap') != -1:
            #here we will randomly choose a user
            self.sendMsg("TEMPUSER, tu as été giflé avec une truite !", channel)
        elif text.find('PRIVMSG ' + nick) != -1:
            splitText = text.split(':')
            splitText = splitText[1].split('!') # splits the string to find the user name of the sender
            name = splitText[0]
            self.sendMsg(self.getFact(), name)
        return text

    def sendMsg(message, target):
        botSock.send(bytes('PRIVMSG ' + target + ' :' + message + '\r\n', "UTF-8"))

    def sendIRC(message):
        botSock.send(bytes(message + '\r\n', 'UTF-8'))

    def joinChannel(self):
        channel = self.returnChannel()
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
        initialInfo =self.getText() #initial info is stored in the variable 'initialInfo'
        #print(initialInfo)
        return initialInfo

    # function to return host name
    def getHostName():
        return socket.gethostname()

    # function to get users of the channel 'test'
    def returnUsers(self):
        botSock.send(bytes(f"NAMES {self.returnChannel()} | *\r\n", "UTF-8")) # use the NAME command to return the list of users on the current channel
        #botSock.send(bytes("WHO" + self.returnChannel() + "\r\n", "UTF-8"))
        names = self.getText()
        return names
    
    # function to return a list of users
    def userList(self):
        names = str(self.returnUsers())
        users = str(names[1:])
        index1 = users.find(":")
        users1 = str(users[index1+1:])
        index2 = users1.find(":")
        users2 = users1[:index2-2]
        channelUsers = list(users2.split(" "))
        return channelUsers
        
        '''#channelUsers = [] # list of users
        # use NAMES command to get all nicknames that are visible on the channel 'test'
        botSock.send(bytes("WHO \r\n", "UTF-8"))
        names =self.getText()
        print(names)
        str(names)
        users = names[1:]
        index = str(users).find("#")
        users = users[:index-1]
        channelUsers = list(users.split(" "))
        return channelUsers '''
        
        '''users = names[5:]
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
        return channelUsers'''

    # function to get the current channel name
    '''def returnCurrentChannel(self):
        # use NAMES command to get all nicknames that are visible on the channel 'test' and the channel name
        botSock.send(bytes("WHO" + self.returnChannel() + "\r\n", "UTF-8"))
        names = self.getText()
        index = str(names).find("#")
        channel = str(names)
        index1 = channel[index:]
        index2 = str(index1).find(":")
        channelName = channel[index:(index+index2)]
        return channelName'''


try:
    botSock.connect((HOST, PORT))
    ludovic = Bot(NICK, CHANNEL)
    ludovic.log_in()
    initialInfo = ludovic.storeInitialInfo()
    #print(f'The initial information: {initialInfo}')

    Bot.sendMsg(f"Bonjour, je m'appelle {ludovic.returnNick()} et je suis chatbot sur ce serveur", CHANNEL) # sends a message to the test channel
    
    # testing for returning channel + users:
    print(f'Users: {ludovic.returnUsers()}')
    print(f'User list: {ludovic.userList()}')
    print(f'Channel: {ludovic.returnChannel()}')
    
    while 1: #while loop prevents bot from disconnecting once it runs out of preset commands
        text = ludovic.getText()
        print(text) #any recieved text is printed for debugging purposes
        
except Exception as e:
    raise
    print(f"port indisponible ou n'existe pas: {e}")
finally:
    botSock.close()
    print("Au Revoir")