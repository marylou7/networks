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

# function to check the text recieved from the server, parses in the bot object and channel
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
            elif text.find('PRIVMSG ' + channelName + ' :!hello') != -1: # used for hello command
                bot.helloCommand(text)
            elif text.find('PRIVMSG ' + channelName + ' :!help') != -1: # used for help command
                bot.helpCommand(text)
            elif text.find('PRIVMSG ' + channelName + ' :!slap') != -1: # used for slap command
                bot.slapCommand(text)
            elif text.find('PRIVMSG ' + nick) != -1: # used for sending a fact
                bot.sendFact(text)
            elif text.find('PRIVMSG ' + channelName + ' :!names') != -1: # used for name command
                bot.namesCommand()
            #elif text.find('PRIVMSG ' + channelName + ' :!kick') != -1:
                #bot.kickCommand(text)
            
            elif "352" in line: # 352 is the WHO reply command
                name = line.split()[7]
                channel.checkUser(name)
        return text

# function so send a pong
def sendPong():
    sendIRC("PONG " + socket.gethostname())

# function to send a message on the channel
def sendMsg(message, target):
    sendIRC('PRIVMSG ' + target + ' :' + message)

# function to send irc message
def sendIRC(message):
    botSock.send(bytes(message + '\r\n', 'UTF-8'))

# function to check that the user inputted nickname is valid
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

# function to check that the user inputted channel name is valid
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
#CHANNEL = '#test'


# user inputs
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

# Bot class
class Bot:
    
    userlist = [] # store users in list
    
    # initialisation of the bot
    def __init__(self, nickname, channel):
        self.nickname = nickname
        self.channel = Channel(channel)
    
    # function to return the nickname
    def returnNick(self):
        return str(self.nickname)
    
    # function to return the channel
    def returnChannel(self):
        return self.channel

    # function to log the user into the channel
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

    # function to join a channel
    def joinChannel(self):
        channel = self.channel
        sendIRC('JOIN ' + channel.returnName()) #functions that either don't work or currently aren't in use

    # function to get a fact
    def getFact(self):
        lines = open('facts.txt').read().splitlines()
        fact = random.choice(lines)
        print(fact)
        return fact
    
    # function to send a fact to the channel chat
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

    # function for the hello command - says hello to the user when !hello is typed to the channel
    def helloCommand(self, text):
        name = self.getSender(text)
        if random.choice([0,1]) == 0: # 50/50 chance to respond with one of two greetings
            sendMsg('Salut, ' + name + '!', self.channel.name)
            print('Salut, ' + name + '!')
        else:
            sendMsg('Bonjour, ' + name + '!', self.channel.name)
            print('Bonjour, ' + name + '!')
    
    # function for the slap command - slaps a user, !slap
    def slapCommand(self, text):
        validTarget = False # is there a valid user to slap?
        userList = self.channel.userList
        name = self.getSender(text)
        splitText = text.split("!")
        print(f"Split Text : ", splitText)
        index = len(splitText) - 1
        if splitText[index] == "slap\r\n":
            if len(userList) == 2:
                # must have more than 2 users - can't slap the bot, can't slap yourself
                sendMsg(name + " la commande nécessite plus d'utilisateurs", self.channel.name)
            else:
                while validTarget is False:
                    target = random.choice(userList) # chooses a random user to slap
                    if target != self.nickname and target != name:
                        validTarget = True
                        sendMsg(target + ", tu as été giflé avec une truite !", self.channel.name)
        else:
            # when the slap victim is specified
            splitText = text.split("!slap ")
            target = (splitText[1])[:-2] # specified user to slap
            print("target: " + target)
            if target != self.nickname and target != name and target in userList:
                sendMsg(target + ", tu as été giflé avec une truite !", self.channel.name)
            elif target in userList:
                sendMsg(name + " cible invalide", self.channel.name)
            else:
                sendMsg(name + ", Cet utilisateur n'est pas là, goûtez au punk à la truite", self.channel.name)
                
    # Additional IRC command: names
    def namesCommand(self):
        # shows the users in the irc chat
        userList = self.channel.userList
        userString = ', '.join(userList)
        sendMsg("Les utilisateurs actifs sur la chaîne sont: " + userString, self.channel.name)
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
        # provides a basic help output to the hexchat for users to refer to when they aren't sure which commands to use
        sendMsg('Une liste de commandes à utiliser dans le canal comprend :', self.channel.name)
        sendMsg('La commande !hello envoie un message bonjour à l utilisateur', self.channel.name)
        sendMsg('La commande !slap consiste à gifler quelqu un dans le canal', self.channel.name)
        sendMsg('La commande !names affiche la liste des utilisateurs actifs sur le canal ', self.channel.name)
        #sendMsg('!kick command forcibly removes a user from a channel, !kick <user> forcibly removes the specified user from the channel ', self.channel.name)
        sendMsg('La commande !help renvoie cette liste de commandes disponibles pour lutilisateur ', self.channel.name)
        print(f'Basic help!')
    
    # Function to get the sender
    def getSender(self, text):
        splitText = text.split(':')
        splitText = splitText[1].split('!') # splits the string to find the user name of the sender
        name = splitText[0]
        return name

# Channel class:
class Channel:
    
    userList = []

    # class initialisation
    def __init__(self, name):
        print("channel.__innit__")
        self.name = name

    # function to return the channel name
    def returnName(self):
        return self.name
    
    # function to set the channel name
    def setName(self, name):
        self.name = name

    # function to return the a list of users in the channel
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
    
    # function to get test from hexchat
    def getText(self):
        print("channel.getText")
        text = returnServerText()
        lines = text.splitlines()
        for line in lines:
            if '352' in line:
                name = line.split()[7]
                if name not in self.userList:
                    self.userList.append(name) # update the user list
        return text
    
    # function to update te user list to make sure it is accurate
    def updateUserList(self):
        print("channel.updateUserList")
        try:
            sendIRC("WHO " + self.returnName()) # use the NAME command to return the list of users on the current channel
            print('::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
            print(self.userList)
        except:
            raise
        threading.Timer(10.0, self.updateUserList).start() # update the list of users every 20 seconds
    
    # function to check if a name is in the list of users
    def checkUser(self, name):
        if name not in self.userList:
            self.userList.append(name) # store list of users globally, so we dont have to keep calling fucntions to get them

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
    raise
    print(f"port indisponible ou n'existe pas: {e}")
finally:
    botSock.close()
    print("Au Revoir")

