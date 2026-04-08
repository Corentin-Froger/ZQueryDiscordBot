import sys
import lib.ZCommon as ZCommon


class ZPlayer:
    teamGame = False

    startByte = 0
    currentByte = 0
    endByte = 0

    playerDict = {}

    # We receive a copy of the rawData bytes from ZServer when it calls this, as well as a starting position
    # Then proceed similarly to ParseData() in ZServer - returning the byte position we ended on, and having the player variables assigned
    #
    # Probably not the best use of memory, as I think it copies the rawData for every player
    # The data amounts are small though, and this seemed like the easiest way to handle it
    # (most rawData from servers will be less than 1000 bytes)
    def __init__(self, byteStream, startPos, teamGame):
        # Assign current + startBytes based on our start position in the data,
        # Also assign rawData from this object to our byteStream
        self.startByte = startPos
        self.currentByte = startPos
        self.rawData = byteStream
        self.teamGame = teamGame

        self.playerDict = {"%playerName%": self.NextPlayerString(), "%playerScore%": self.NextBytes(2),
                           "%playerPing%": self.NextBytes(2)}

        # 1: Player name (string)

        # 2: Player score (short int)

        # 3: Player ping (short int)

        # 4: Is player spectating?
        tmp = self.NextBytes(1)
        if tmp != 0:
            self.playerDict["%playerSpectate%"] = True
        else:
            self.playerDict["%playerSpectate%"] = False

        # 5: Is player a bot?
        tmp = self.NextBytes(1)
        if tmp != 0:
            self.playerDict["%playerIsBot%"] = True
        else:
            self.playerDict["%playerIsBot%"] = False

        # 6: If we are playing a team game, grab player's team number
        if self.teamGame:
            self.playerDict["%playerTeamNumber%"] = self.NextBytes(1)
        else:
            self.playerDict["%playerTeamNumber%"] = 0

        # 7: Player's time (in minutes) on server
        self.playerDict["%playerMinutes%"] = self.NextBytes(1)

        # Set our "endByte" marker
        # The calling method can pull this value to find out where it should read from next
        # in the rawData
        self.endByte = self.currentByte

        # Debug info about player:
        if ZCommon.debug:
            print("\nDEBUG :: playerDict == " + str(self.playerDict), file=sys.stderr)

    # Finds and returns the next string in our rawData bytes (terminated with null)
    # This is more complicated than the "NextString" in the ZServer class, as we have to contend with special player color codes here
    def NextPlayerString(self):
        retString = ""

        # Debug loop to show player's raw data:
        if ZCommon.debug:
            print("DEBUG :: Raw Player name (ASCII):", file=sys.stderr, end="  ")
            x = self.currentByte
            while self.rawData[x] != 0:
                print(str(int(self.rawData[x])), file=sys.stderr, end=" ")
                x += 1
            # print("\n", end='', file=sys.stderr)

        # Read characters until we hit a null, and add them to our string

        # print("===========")
        # print(self.currentByte)
        # print(len(self.rawData))

        if self.currentByte >= len(self.rawData):
            return "currentByte >= len problem to fix"

        while int(self.rawData[self.currentByte]) != 0:
            tmpChar = ''

            # byteInt = int(self.rawData[self.currentByte])

            # Option 1: a normal letter (ASCII between 32 - 254)
            # This is easy, we just assign tmpChar and proceed
            if 31 < int(self.rawData[self.currentByte]) < 255 and int(
                    self.rawData[self.currentByte]) != 28:
                tmpChar = chr(int(self.rawData[self.currentByte]))

            # Option 2: color code in brackets
            # This consists of a color character (ASCII 28, hex 1c) followed by a color code in brackets "[]" (ASCII 91 / 93)
            # ex: \x1c[b1]
            #
            # We have another loop that reads until the end of the last bracket "]"
            # We don't process colors yet, so just skip them
            if int(self.rawData[self.currentByte]) == 28 and int(self.rawData[self.currentByte + 1]) == 91:
                abortParse = False

                while int(self.rawData[self.currentByte]) != 93:

                    # Check to see if the string ends inside the color value ('\x00')
                    # This should never happen!
                    if int(self.rawData[self.currentByte]) == 0:
                        abortParse = True
                        break

                    self.currentByte += 1

                if abortParse:
                    break

            # Option 3: color code followed by single byte
            # This is the color character (ASCII 28, hex 1c), followed by a single color code byte instead of brackets
            # ex: \x1cA
            #
            # This is simple, we just skip the color coder and the byte, and move on with the string
            if int(self.rawData[self.currentByte]) == 28 and int(self.rawData[self.currentByte + 1]) != 91:
                self.currentByte += 2
                continue

            retString = retString + tmpChar
            self.currentByte += 1

        # Advance our byte counter 1 more, to get past our null byte:
        self.currentByte += 1

        # retString = retString.encode("ascii", "ignore")
        # retString = retString.decode()
        return retString

    # Retrieve the next X bytes from the raw byte strream, and advance the counter accordingly
    # (This is a copy of the method from ZServer, and is bad practice, should probably be merged at some point)
    def NextBytes(self, byteLen):
        retInt = int.from_bytes(self.rawData[self.currentByte: self.currentByte + byteLen], byteorder='little',
                                signed=False)

        self.currentByte += byteLen

        return retInt
