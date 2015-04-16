Devon McKenna
#4330241
CS3130 - Ass3

To Run Server:     python3 MMS.py server ''
To Run Client:     ptyhon3 MMS.py client ''
---------------------------------------------------------------------------------------

Ass 3 is a (multi)client-(single)server messaging application.

Once the server has been started, multiple clients may connect and communicate with it through select commands.

Commands:
    help:                   lists accepted commands
    whoIson:                lists users divided by their status as online or offline
    signin <username> :     sign in under an accepted user
    send <username> :       send a message to another user
    signout:                sign out of current session


As noted in various comments, this program is not perfect and can result in lost messages or users locked into "online" and unable to re-signin until "UserList.txt" updated manually.



The code handles basic exceptions. Does not have "try:" or "except:" when attemtping to open up text files.  Need to get on to Lab 4 as this lab ate a lot of time, so not bothering to add them (basically copy-paste since same scenario each time).



----------------------------------------------------------------------------------------


On GitHub:

    https://github.com/mckennad/ass3.git
