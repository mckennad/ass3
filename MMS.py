import re, sys, argparse, random, socket


MAX_BYTES = 65535

#---------------------------------------------------

def server(interface, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((interface, port))
    print ('Listening at ', sock.getsockname())

    messToBeSent = []

    
    while True:


        data, address = sock.recvfrom(MAX_BYTES);
        print(address)          #debuggin with print

        text = data.decode('ascii')
        words = text.split(" ")



        if(words[0] == "help"):                     #help
            message = MMShelp()

        elif (words[0] == "signin"):                #signin
            if(len(words)>1):
                message = MMSsignin(words, address[1])
            else:
                message = ">> You need to enter a username.\n"

        elif (words[0] == "whoIson"):               #whoIson
            message = MMSwhoIson(words)

        elif (words[0] == "send"):                  #send
            if(len(words)>1):
                messToBeSent = MMSsend(words, address)
                if(len(messToBeSent)>1):
                    message = "Message sent"
                else:
                    message = messToBeSent[0]
            else:
                message = ">> You need to specify target user.\n"

        elif (words[0] == "signout"):               #signout
            message = MMSsignout(address[1])

        elif (words[0] == "exit"):                  #exit
            garbage = MMSsignout(address[1])
            message = ">>  Goodbye\n\n--\n"

        elif (text == "This is another message"):   #startmessage
            message = ">> Welcome to MMS. \n"
        else:
            message = ">> Not a command.  Try entering \"help\" for assistance\n"


        if (len(messToBeSent)>1):
            if(str(address[1]) == messToBeSent[0]):
                message += messToBeSent[1]
                messToBeSent = []
        
        sock.sendto(message.encode('ascii'), address)



#---------------------------------------------------

def client(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = sys.argv[2]
    sock.connect((hostname, port))

    delay = 0.1 # seconds
    text = 'This is another message'
    data = text.encode('ascii')


    while True:
        sock.send(data)
        sock.settimeout(delay)
        try:
            data = sock.recv(MAX_BYTES)
        except socket.timeout as exc:
            if delay > 2.0:
                raise RuntimeError('I think the server is down') from exc
        else:
            print(data.decode('ascii'))
            break # we are done, and can stop looping



    while True:
        text = input()
        print()
        data = text.encode('ascii')

        sock.send(data)
        sock.settimeout(delay)
        try:
            data = sock.recv(MAX_BYTES)
        except socket.timeout as exc:
            delay *= 2 # wait even longer for the next request
            if delay > 2.0:
                raise RuntimeError('I think the server is down') from exc
        else:
            response = data.decode('ascii')
            print(response)
            if (response == ">>  You have signed off\n\n--\n"):
                break # we are done, and can stop looping
            elif (response == ">>  Goodbye\n\n--\n"):
                break


#---------------------------------------------------

def MMShelp():
#send back help information to server to be printed to the user

    return "\n>>The following commands are supported: \n>> \n>>  signin <username> \n>>  whoIson \n>>  send <username> <message> \n>>  signout \n>>  exit \n \n"


#---------------------------------------------------

def MMSsignin(words, address):
#checks if user exists and if so, whether they are already online.  If not online, modifies them to be online in file and adds current address they are using

    users = {}
    stor = {}
    mess = ""
    mcount = 0
    infile = open("UserList.txt","r")

    for line in infile:                             #grabs copy of UserList and seperates usernames
        name, info = line.split(":",1)
        users[name] = info
    infile.close()


    for name in users:                                #Checks if user exists and if so, their state
        if (name == words[1]):
            state, storedAddress = users[name].split(";",1)
            if (state == "offline"):
                state = "online"

                users[name] = state + ";" + str(address) + "\n"       #updates UserList if needed
                infile = open("UserList.txt","w")

                for name in users:
                    newLine = [name,":",users[name]]
                    infile.writelines(newLine)
                infile.close()


                infile = open("Storage.txt","r")                #grabs copy of message Storage
                for line in infile:
                    name, messDetails = line.split(":",1)
                    stor[name] = messDetails
                    if (name == words[1]):                      #Checks if user has any messages waiting
                        mess = mess + ">>       " + stor[name]
                        mcount = mcount + 1
                infile.close()


                infile = open("Storage.txt", "w")       #updates Storage after taking out appropriate messages
                for name in stor:
                    if (name != words[1]):
                        newLine = [name,":",stor[name]]
                        infile.writelines(newLine)
                infile.close()

                mess = ">>Welcome " + words[1] + ", you have " + str(mcount) + " message(s) waiting : \n" + mess

                return mess

            else:
                mess = ">> " + words[1] + " is already signed in"
                return mess


    mess = ">> user " + words[1] + " is not authorized to use MMS \n"
    return mess



#---------------------------------------------------

def MMSwhoIson(words):
    #checks which users are online nad offline and returns that information to the user
    
    users = {}
    online = []  
    offline = []

    infile = open("UserList.txt", "r")

    for line in infile:
        name, info = line.split(":",1)
        users[name] = info
    infile.close()


    for name in users:
        print(name + "--> ", end= "")
        print(users[name])
        state, storedAdd = users[name].split(";")
        if(state == "online"):
            online.append(name)
        else:
            offline.append(name)


    mess1 = ", ".join(online)
    mess2 = ", ".join(offline)

    mess = ">> User(s) online :\n>>    " + mess1 + "\n>> User(s) offline :\n>>    " + mess2 + "\n"


    return mess


#---------------------------------------------------

def MMSsend(words, address):
    #Checks if sender exists, then if target user exists, then whether target user is online or offline.  It then delivers message in 2 different ways depedning on the status of the target user.  NOTE: current model has no problems with storing messages for offline target users, but can only store the most recent message for online target users (not worth fixing atm, this ain't professional)


    users = {}
    users2 = {}
    senderExists = False
    toBeSent = words[2:]
    messToBeSent = []



    infile = open("UserList.txt", "r")
    for line in infile:
        garbage, storedAdd = line.split(";",1)
        storedAdd = storedAdd.rstrip("\n")
        users[storedAdd] = garbage
    infile.close()

    for storedAdd in users:             #makes sure user is signed in
        if (str(address[1]) == storedAdd):
            senderExists = True
            senderName, meh = users[storedAdd].split(":")

    if not(senderExists):
        messToBeSent.append(">> You are not signed in.  Please use \"signin <username>\" to sign in.\n")
        return messToBeSent



    infile = open("UserList.txt", "r")          #Recopied due to concerns in following search
    for line in infile:
        name, info = line.split(":",1)
        users2[name] = info
    infile.close()

    for name in users2:
        if (words[1] == name):
            state, storedAdd = users2[name].split(";")
            storedAdd = storedAdd.rstrip("\n")

            mess = ">>  " + senderName + " : "
            mess1 = (" ").join(toBeSent)
            mess += mess1 + "\n"

            if (state == "online"):     #will send data back to server to store until next interaction with target (this could lead to problems [target closes client without interacting with server for example]) that would need to be addressed if every error is to be accounted for [NOT DOING THAT!].  I imagine running a server-like operation on the client side that would always listen for messages would be a solution to this issue.  As noted above, currently my approach has issues when more than one message is Waiting on Delivery.

                messToBeSent.append(storedAdd)
                messToBeSent.append(mess)

                return messToBeSent
                
            else:
                mess = name + ":" + senderName + ";"
                mess1 = (" ").join(toBeSent)
                mess += mess1 + "\n"

                infile = open("Storage.txt","a")
                infile.writelines(mess)

                messToBeSent.append(">> " + name + " is offline.  Message will be saved for future delivery.\n")
                return messToBeSent
        
    messToBeSent.append(">> Target user does not exist. Please consider using \"whoIson\" to see all users.\n")
    return messToBeSent
                



#---------------------------------------------------

def MMSsignout(address):
    #checks if user address (port only since all our clients share IP) matches a user currently marked as "online", if so, modify data and notify of logout.  Otherwise, notify user they have signed in yet (and therefore cannot log out) and give instructions on what to do if this is false.

    users = {}

    #print("=======")
    infile = open("UserList.txt", "r")
    for line in infile:
        garbage, storedAdd = line.split(";",1)
        storedAdd = storedAdd.rstrip("\n")
        users[storedAdd] = garbage
        #print(line.rstrip("\n"))
    infile.close()
    #print("=======\n")


    for storedAdd in users:

        """print("\nNEXT!!!")   #debuggin with print
        print(address)
        print(type(address))
        print("---")
        print(storedAdd)
        print(type(storedAdd))
        print("+++")
        print(users[storedAdd])"""

        if(str(address) == storedAdd):
            name, state = users[storedAdd].split(":",1)
            state = "offline"
            users[storedAdd] = name + ":" + state

            infile = open("UserList.txt","w")

            for storedAdd in users:
                newLine = [users[storedAdd],";",storedAdd,"\n"]
                infile.writelines(newLine)
            infile.close()

            return ">>  You have signed off\n\n--\n"

    return ">> You were not signed in.  Consider using \"Control + C\" to excape the program if this is incorrect.\n"



#---------------------------------------------------
#copy-pasted from "udp_remote.py" and makes me a little dizzy looking at it.  O.o


if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send and receive UDP,' ' pretending packets are often dropped')
    parser.add_argument('role', choices=choices, help='which role to take')
    parser.add_argument('host', help='interface the server listens at;' ' host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='UDP port (default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)

