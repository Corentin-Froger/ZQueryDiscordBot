import socket
import time
from time import strftime

import lib.huffman as huffman
from lib.ZPlayer import *


class ZServer:
    responseHeader = 0
    timeStamp = 0

    currentByte = 0
    rawString = ""

    address = "localhost"
    port = 10666
    flags = 0
    flags2 = 0
    debug = False

    players = []

    serverDict = {}

    # address = string (IP or FQDN)
    # port = integer
    # flags = bytes object, length 4, little-endian.  A bitwise OR of base-16 query flags (equivalent to unsigned long int in C/C++)
    def __init__(self, address, port, flags):
        self.rawData = None
        self.address = address
        self.port = port
        self.flags = flags
        self.responseHeader = 0
        self.currentByte = 0
        self.serverDict = {"%serverIP%": self.address, "%serverPort%": self.port}
        self.players = []

    # Actually run the UDP network communication
    # This should be called first, so we can set our class variable "self.rawData"
    def QueryServer(self, timeout: int):
        h = huffman.HuffmanObject(huffman.SKULLTAG_FREQS)

        # Our request packet is 3 32-bit integers in a row, for a total of 12 bytes (32 bit = 4 bytes)
        # They must be converted to the "byte" type, with appropriate length and encoded little-endian
        # The numbers are: 199 + bitwise OR hex flags + epoch time stamp  (concatenated, not added)
        request = int(199).to_bytes(4, "little") + self.flags + int(time.time()).to_bytes(4, "little")

        # Compress request with the huffman algorithm
        requestEncoded = h.encode(request)

        # Open internet (AF_INET) socket, for UDP (SOCK.DGRAM) communication
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # Send the compressed request, and wait up to timeout seconds for a response
            sock.sendto(requestEncoded, (self.address, self.port))
            sock.settimeout(timeout)
            data, server = sock.recvfrom(8192)
            self.rawData = h.decode(data)

        finally:
            sock.close()

        if ZCommon.debug:
            print('DEBUG :: Network/UDP received ' + str(len(self.rawData)) + ' bytes', file=sys.stderr)
            print('DEBUG :: {!r}'.format(self.rawData), file=sys.stderr)

    # Main control method that controls our parsing of the rawData byte string
    def ParseData(self):
        # We start at position 0, beginning of our raw data stream
        self.currentByte = 0

        # 0: Get server response header and time stamp (both 4 byte long ints)
        self.responseHeader = self.NextBytes(4)
        self.timeStamp = self.NextBytes(4)

        # Bail out of whole program if header response doesn't match the magic accepted number:
        if self.responseHeader != 5660023:
            # print("Error!  Client has been banned or has queried this server too recently.", file=sys.stderr)
            raise Exception("Error!  Client has been banned or has queried this server.")

        # 1: String with the server version
        self.serverDict["%ZVersion%"] = self.NextString()

        # 2: Our flags are repeated back to us (long int)
        self.flags2 = self.NextBytes(4)
        # Todo: maybe check this flag against the "flags" we started with?  Abort if they don't match?

        # 3: Server Name, URL, E-mail, Mapname (4 strings)
        self.serverDict["%serverName%"] = self.NextString()
        self.serverDict["%serverURL%"] = self.NextString()
        self.serverDict["%serverEmail%"] = self.NextString()
        self.serverDict["%serverMap%"] = self.NextString()

        # 4: Server Max Players and PWAD count (both single bytes)
        self.serverDict["%maxPlayers%"] = self.NextBytes(1)
        self.serverDict["%pwadCount%"] = self.NextBytes(1)

        # 5: PWad strings list
        self.serverDict["%pwadList%"] = ""
        if int(self.serverDict["%pwadCount%"]) > 0:
            for i in range(0, self.serverDict["%pwadCount%"]):
                self.serverDict["%pwadList%"] = self.serverDict["%pwadList%"] + self.NextString() + " "

        # 6: Gametype, instagib/buckshot settings
        self.serverDict["%serverType%"] = self.NextBytes(1)
        self.serverDict["%instaGib%"] = self.NextBytes(1)
        self.serverDict["%buckShot%"] = self.NextBytes(1)

        if self.serverDict["%serverType%"] == 4 or self.serverDict["%serverType%"] == 8 or self.serverDict[
            "%serverType%"] >= 10:
            self.serverDict["%teamGame%"] = True
        else:
            self.serverDict["%teamGame%"] = False

        # Set game type to a string instead of number:
        self.serverDict["%serverType%"] = ZCommon.GAMEMODE[self.serverDict["%serverType%"]]

        # 7: Server game name (doom, doom2, hexen, etc.), IWAD, and Skill value
        self.serverDict["%serverGame%"] = self.NextString()
        self.serverDict["%serverIwad%"] = self.NextString()
        self.serverDict["%serverSkill%"] = self.NextBytes(1)

        # Set skill to string instead of number:
        if self.serverDict["%serverSkill%"] > 4:
            # Some servers use mods with custom skills !
            self.serverDict["%serverSkill%"] = "skill " + str(self.serverDict["%serverSkill%"])
        else:
            self.serverDict["%serverSkill%"] = ZCommon.SKILL[self.serverDict["%serverSkill%"]]

        # 8: Get server score/time limits and player count
        self.serverDict["%fragLimit%"] = self.NextBytes(2)
        self.serverDict["%timeLimit%"] = self.NextBytes(2)

        self.serverDict["%timeLeft%"] = 0
        if self.serverDict["%timeLimit%"] != 0:
            self.serverDict["%timeLeft%"] = self.NextBytes(2)

        self.serverDict["%duelLimit%"] = self.NextBytes(2)
        self.serverDict["%pointLimit%"] = self.NextBytes(2)
        self.serverDict["%winLimit%"] = self.NextBytes(2)
        self.serverDict["%clientCount%"] = self.NextBytes(1)

        # 8.5: Assign current time (ISO format):
        self.serverDict["%currentTime%"] = strftime("%Y-%m-%d %H:%M:%S")

        if ZCommon.debug:
            print("\nDEBUG :: serverDict == \n" + str(self.serverDict) + "\n", file=sys.stderr)

        # 9: Get players and their information
        if self.serverDict["%clientCount%"] > 0:
            for i in range(0, int(self.serverDict["%clientCount%"])):
                self.players.append(ZPlayer(self.rawData, self.currentByte, self.serverDict["%teamGame%"]))
                self.currentByte = self.players[i].endByte

    # Finds and returns the next string in the rawData
    # Starting with our current byte and proceeding until we hit a null ('\x00')
    def NextString(self):

        retString = ""

        # Read characters until we hit a null, and add them to our string
        while int(self.rawData[self.currentByte]) != 0:
            retString = retString + chr(int(self.rawData[self.currentByte]))
            self.currentByte += 1

        # Advance our byte counter 1 more, to get past our null byte:
        self.currentByte += 1

        return retString

    # Retrieve the next X bytes from the raw byte strream, and advance the counter accordingly
    # This is used to retrieve numeric values in the byte stream, whose length is static
    # (1 byte = 0-255 , 2 bytes = short int, 4 bytes = long int)
    def NextBytes(self, byteLen):
        retInt = int.from_bytes(self.rawData[self.currentByte: self.currentByte + byteLen], byteorder='little',
                                signed=False)

        self.currentByte += byteLen

        return retInt
