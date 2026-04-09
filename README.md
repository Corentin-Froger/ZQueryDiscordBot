# ZQueryDiscordBot

## Credits
Code base by Caboose / SkipGrub<br>
(https://zandronum.com/forum/viewtopic.php?t=9992)<br>
(https://gitlab.com/SkipGrube/zquery)

Huffman compression library provided by Alex Mayfield and Teemu Piipo<br>
(https://bitbucket.org/crimsondusk/pyskull)

## Description
This is a discord bot that displays the state of a specific set of servers,<br>
such as which players are connected, their score, ping, time...

## Setup
You need to create a discord bot first, and give it the proper intents permissions:
https://discord.com/developers/applications

You'll need to create a `.env` file containing these variables :
```
BOT_TOKEN=                         # The token of your discord bot
EUROBOROS_IP="142.132.155.163"     # Not necessarily Euroboros !
SERVERS_CATEGORY_NAME="Servers"    # The channel category where the new channels will be created
SERVER_BRAND=                      # The motif that the bot will search in the server name
```

You also need to install the requirements :

``pip install -r .\requirements.txt``

Then simply run the program

``python main.py``