import socket
import time
import random
import threading

import sys

botSock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

serverName = 'localHost IPv6'

#recieves text from server and returns it
def returnServerText():
    text = botSock.recv(2040)
    text = text.decode() #converts the bytes it recieves from the server to a string
    print("text: " + text)
    return text

#checks the text recieved from the server
def getText(bot, channel):
        channelName = channel.returnName()
        nick = bot.returnNick()
        text = returnServerText()
        lines = text.splitlines()
        for line in lines:
            print(line)
            if text.find('PING') != -1: #if the text is a ping
                sendPong()
                print("PONG sent to server") #check if PONG is sent
            elif text.find('PRIVMSG ' + channelName + ' :!hello') != -1:
                bot.helloCommand(text)
            elif text.find('PRIVMSG ' + channelName + ' :!help') != -1:
                bot.helpCommand(text)
            elif text.find('PRIVMSG ' + channelName + ' :!slap') != -1:
                bot.slapCommand(text)
            elif text.find('PRIVMSG ' + nick) != -1:
                bot.sendFact(text)
            elif text.find('PRIVMSG ' + channelName + ' :!names') != -1:
                bot.namesCommand()
            #elif text.find('PRIVMSG ' + channelName + ' :!kick') != -1:
                #bot.kickCommand(text)
            
            elif "352" in line: # 352 is the WHO reply command
                name = line.split()[7]
                channel.checkUser(name)
            elif "QUIT" in line or "PART" in line:
                name = bot.getSender(text)
                channel.removeUser(name)
        return text

def sendPong():
    sendIRC("PONG " + socket.gethostname())

def sendMsg(message, target):
    sendIRC('PRIVMSG ' + target + ' :' + message)

def sendIRC(message):
    botSock.send(bytes(message + '\r\n', 'UTF-8'))

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


HOST = 'fc00:1337::17' #host name
PORT = 6667 #port number
NICK = 'Ludovic' #sets default nickname for bot
CHANNEL = '#test'

'''
nickname = input("entrez un surnom pour vous-même: ")
NICK = checkNick(nickname)
channelName = input("Saisissez le nom de la chaîne que vous souhaitez rejoindre: ")
CHANNEL = checkChannel(channelName)
'''

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
    
    userlist = [] # store users in list
    
    def __init__(self, nickname, channel):
        self.nickname = nickname
        self.channel = Channel(channel)
    
    def returnNick(self):
        return str(self.nickname)
    
    def returnChannel(self):
        return self.channel

    def log_in(self):
        NICK = self.returnNick()
        sendIRC("CAP LS 302") #CAP command used for sign in, idk what this does but its the lynch pin holding the sign in protocol together apparently
        time.sleep(0.01)
        sendIRC("NICK " + NICK) #nickname is requested
        sendIRC("USER " + NICK + " 0 * :realname") #nickname is given to the bot
        time.sleep(0.1)
        sendIRC("CAP END") #close CAP
        time.sleep(0.1)
        sendIRC("JOIN " + self.channel.returnName()) #test channel is joined
        time.sleep(0.1)

    # ^^^ sleeps used to break commands into seperate lines and wait for a response if neccesary

    def joinChannel(self):
        channel = self.channel
        sendIRC('JOIN ' + channel.returnName()) #functions that either don't work or currently aren't in use

    def getFact(self):
        lines = open('facts.txt').read().splitlines()
        fact = random.choice(lines)
        print(fact)
        return fact
    
    def sendFact(self, text):
        splitText = text.split(':')
        splitText = splitText[1].split('!') # splits the string to find the user name of the sender
        name = splitText[0]
        sendMsg(self.getFact(), name)

    # function to return host name
    def getHostName(self):
        return socket.gethostname()

    # function to get users of the channel the bot is on
    def returnUsers(self):
        sendIRC("WHO " + self.channel.returnName()) # use the NAME command to return the list of users on the current channel
        print(self.userlist)
        threading.Timer(10.0, self.returnUsers).start() # update the list of users every 20 seconds

    def helloCommand(self, text):
        name = self.getSender(text)
        if random.choice([0,1]) == 0: # 50/50 chance to respond with one of two greetings
            sendMsg('Salut, ' + name + '!', self.channel.name)
            print('Salut, ' + name + '!')
        else:
            sendMsg('Bonjour, ' + name + '!', self.channel.name)
            print('Bonjour, ' + name + '!')
    
    def slapCommand(self, text):
        validTarget = False
        userList = self.channel.userList
        name = self.getSender(text)
        splitText = text.split("!")
        print(f"Split Text : ", splitText)
        index = len(splitText) - 1
        if splitText[index] == "slap\r\n":
            if len(userList) == 2:
                sendMsg(name + " la commande nécessite plus d'utilisateurs", self.channel.name)
            else:
                while validTarget is False:
                    target = random.choice(userList)
                    if target != self.nickname and target != name:
                        validTarget = True
                        sendMsg(target + ", tu as été giflé avec une truite !", self.channel.name)
        else:
            splitText = text.split("!slap ")
            target = (splitText[1])[:-2]
            print("target: " + target)
            if target != self.nickname and target != name and target in userList:
                sendMsg(target + ", tu as été giflé avec une truite !", self.channel.name)
            elif target in userList:
                sendMsg(name + " cible invalide", self.channel.name)
            else:
                sendMsg(name + ", Cet utilisateur n'est pas là, goûtez au punk à la truite", self.channel.name)
                
    # Additional IRC command
    def namesCommand(self):
        # shows the users in the irc chat
        userList = self.channel.userList
        userString = ', '.join(userList)
        sendMsg("Active users on the channel are: " + userString, self.channel.name)
        print(userString)
    
    
    '''# Additional IRC command: kick
    def kickCommand(self, text):
        # The KICK command can be used to forcibly removes a user from a channel
        # Parameters: <channel> <user>
        targetUser = False
        userList = self.channel.userList
        name = self.getSender(text)
        splitText = text.split("!")
        if splitText[2] == "kick\r\n":
            if len(userList) == 2:
                sendMsg(name + " la commande nécessite plus d'utilisateurs", self.channel.name)
            else:
                # choose a random user to then kick out of the channel
                while targetUser==False:
                    validUser = random.choice(userList)
                    if validUser != self.nickname and validUser != name:
                        targetUser = True
                        sendIRC("KICK " + self.returnChannel() + " " + validUser)
        
        # if there is a specified user
        else:
            splitText = text.split("!kick ")
            user = (splitText[1])[:-2]
            print("target: " + user)
            if user != self.nickname and user != name and user in userList:
                sendIRC("KICK " + self.returnChannel() + " " + user)
            elif user in userList:
                sendMsg(name + "error with this command", self.channel.name)
            else:
                sendMsg(name + ",specified user is not in channel", self.channel.name)
        '''
    
    # Additional IRC command: !help
    def helpCommand(self):
        # provides a basic help to the hexchat
        sendMsg('A list of commands to use in the channel include: ', self.channel.name)
        sendMsg('!hello command ouputs a hello message to the user ', self.channel.name)
        sendMsg('!slap command is to slap someone in the channel ', self.channel.name)
        sendMsg('!names command outputs the list of active users on the channel ', self.channel.name)
        #sendMsg('!kick command forcibly removes a user from a channel, !kick <user> forcibly removes the specified user from the channel ', self.channel.name)
        sendMsg('!help command returns this list of commands available to the user ', self.channel.name)
        print(f'Basic help!')
    
    def getSender(self, text):
        splitText = text.split(':')
        splitText = splitText[1].split('!') # splits the string to find the user name of the sender
        name = splitText[0]
        return name

        
class Channel:
    
    userList = []

    def __init__(self, name):
        print("channel.__innit__")
        self.name = name

    def returnName(self):
        return self.name
    
    def setName(self, name):
        self.name = name

    def returnUserList(self):
        return self.userList
    
    # Retaining the initial information sent by miniircd about the channel and its users
    '''
    def storeInitialInfo(self):
        print("channel.storeInitialInfo")
        initialInfo = getText() #initial info is stored in the variable 'initialInfo'
        #print(initialInfo)
        return initialInfo
    '''
    
    def getText(self):
        print("channel.getText")
        text = returnServerText()
        lines = text.splitlines()
        for line in lines:
            if '352' in line:
                name = line.split()[7]
                if name not in self.userList:
                    self.userList.append(name)
        return text
    
    def updateUserList(self):
        print("channel.updateUserList")
        try:
            sendIRC("WHO " + self.returnName()) # use the NAME command to return the list of users on the current channel


            print('::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
            print(self.userList)
        except:
            raise
        threading.Timer(10.0, self.updateUserList).start() # update the list of users every 20 seconds
    
    def checkUser(self, name):
        if name not in self.userList:
            self.userList.append(name) # store list of users globally, so we dont have to keep calling fucntions to get them

    def removeUser(self, name):
        if name in self.userList:
            self.userList.remove(name)
            print("Removed: " + name)

try:
    botSock.connect((HOST, PORT))
    ludovic = Bot(NICK, CHANNEL)
    ludovic.log_in()
    #initialInfo = ludovic.storeInitialInfo()
    #print(f'The initial information: {initialInfo}')

    sendMsg(f"Bonjour, je m'appelle {ludovic.returnNick()} et je suis chatbot sur ce serveur. ", CHANNEL) # sends a message to the test channel
    sendMsg(f"utilisez la commande !help pour afficher une liste des commandes disponibles ", CHANNEL)
    
    # call the WHO message every twetnty seconds
    #threading.Timer(10.0, ludovic.returnUsers, {}).start()

    # testing for returning channel + users:
    print(f'Users: {ludovic.returnChannel().updateUserList()}')
    #print(f'User list: {ludovic.userlist}')
    print(f'Channel: {ludovic.returnChannel().returnName()}')
    while 1: #while loop prevents bot from disconnecting once it runs out of preset commands
        text = getText(ludovic, ludovic.returnChannel())
        print(text) #any recieved text is printed for debugging purposes

except Exception as e:
    print(f"port indisponible ou n'existe pas: {e}")
    raise
finally:
    botSock.close()
    print("Au Revoir")

