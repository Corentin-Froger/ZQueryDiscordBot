import os

from lib.ZServer import *


class ZOutput:
    server = ""
    template = ""
    outFile = ""

    # We need the parsed server object, that should have all our data in it
    # Also need a template file to read and apply the server data to it for output
    # Also need the filename we're outputting to, or empty ("") for STDOUT
    def __init__(self, server, template, outFile):
        self.server = server
        self.template = template
        self.outFile = outFile

        if not os.path.exists(self.template):
            print("ERROR!  Template file   " + str(
                self.template) + "does not exist.  A template file must be specified, or the default files must be present.",
                  file=sys.stderr)
            quit(1)

        self.SanitizeServer()
        self.MakeOutput()
        # self.ProcessTemplate()

    # Before doing our string swaps, we must ensure none of our input (server name, player names, etc.) includes the template values!
    # (a player can't have "%serverName%" in their name, for example)
    # Otherwise we get unpredictable results!
    #
    # To get around this, we simply add a space (" ") between the % .  It still makes things readable, but will not be interpreted in the template
    # Only doing this with string values for now, as the numbers and booleans are probably safe
    # ex: a player named "%serverName%" becomes " % serverName % "
    def SanitizeServer(self):

        # Loop through each server attribute
        # If it's a string, then we need to loop through ALL macros and "fix" them if they are present
        # If it's not a string, we can safely assume they don't contain a macro
        for i in ZCommon.Templates:
            if type(self.server.serverDict[i]) is str:
                for j in ZCommon.Templates + ZCommon.PlayerTemplates:
                    fixedStr = j.replace("%", " % ")
                    self.server.serverDict[i] = self.server.serverDict[i].replace(j, fixedStr)

        # Similar loop:
        # For each player, ensure their name value doesn't contain *any* of our template macros - player or server related
        for i in self.server.players:
            for j in ZCommon.Templates + ZCommon.PlayerTemplates:
                fixedStr = j.replace("%", " % ")
                i.playerDict["%playerName%"] = i.playerDict["%playerName%"].replace(j, fixedStr)

    # Read in our template file and produce the output
    def MakeOutput(self):
        finalString = ""

        # Reading the whole thing into memory for now
        # I don't anticipate needing very large template files
        f = open(self.template, 'r')
        tLines = f.readlines()
        f.close()

        # print("DEBUG:: tLines list ==\n" + str(tLines))

        for line in tLines:
            finalString += self.SubMacro(line)
            continue

            # First, determine if this line has any player data in it
            # If it does, we need to make sure the line gets duplicated for each player
            isPlayerLine = False
            for j in ZCommon.PlayerTemplates:

                if line.find(j) >= 0:
                    isPlayerLine = True
                    break

                # print("isPlayerLine == " + str(isPlayerLine))
                # print("now calling for line :: " + line)
                # Get modified line by calling the "swap" method
                finalString = finalString + self.SubMacro(line, isPlayerLine)

        # Actually print the final output - either to stdout (default) or specified "outFile"
        if self.outFile != "":
            f = open(self.outFile, "w", encoding="utf-8")
            f.write(str(finalString))
            f.close()
        else:
            print(str(finalString))

    def __str__(self):
        finalString = ""

        # Reading the whole thing into memory for now
        # I don't anticipate needing very large template files
        f = open(self.template, 'r')
        tLines = f.readlines()
        f.close()

        # print("DEBUG:: tLines list ==\n" + str(tLines))

        for line in tLines:
            finalString += self.SubMacro(line)
            continue

            # First, determine if this line has any player data in it
            # If it does, we need to make sure the line gets duplicated for each player
            isPlayerLine = False
            for j in ZCommon.PlayerTemplates:

                if line.find(j) >= 0:
                    isPlayerLine = True
                    break

                # print("isPlayerLine == " + str(isPlayerLine))
                # print("now calling for line :: " + line)
                # Get modified line by calling the "swap" method
                finalString = finalString + self.SubMacro(line, isPlayerLine)

        # Actually print the final output - either to stdout (default) or specified "outFile"
        if self.outFile != "":
            f = open(self.outFile, "w", encoding="utf-8")
            f.write(str(finalString))
            f.close()
            return None
        else:
            return str(finalString)

    # Method that actually performs the macro swap
    # It takes a string (single line) - and swaps the values
    #
    # if "hasPlayer" is true, then it will copy it for each player available as well
    def SubMacro(self, givenLine):
        isPlayerLine = False

        # First, find out if we have a player value in our line:
        for i in ZCommon.PlayerTemplates:
            if givenLine.find(i) >= 0:
                isPlayerLine = True
                break

        # First substitution: swap all the server variables in the line
        # These need to be swapped, even if the line gets copied later due to player variables
        for i in ZCommon.Templates:
            givenLine = givenLine.replace(i, str(self.server.serverDict[i]))

        # Return if we don't have player variables
        if not isPlayerLine:
            return givenLine

        # If we have player variables, but no players, we need to swap blanks for the player variables (and return!):
        if self.server.serverDict["%clientCount%"] <= 0:
            for i in ZCommon.PlayerTemplates:
                givenLine = givenLine.replace(i, '')
            return givenLine

        # If we make it this far, we have player variables on this line, *and* there are players on the server
        # We need to duplicate the line for each player:
        retString = ""
        for p in self.server.players:
            # print("Player name == " + player.playerDict["%playerName%"])
            newLine = givenLine

            for j in ZCommon.PlayerTemplates:
                newLine = newLine.replace(j, str(p.playerDict[j]))

            # print("Adding player line: "  + str(newLine))
            retString = retString + newLine

        return retString
