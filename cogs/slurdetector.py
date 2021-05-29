import discord, asyncio, os, json
from discord.ext import commands
from async_timeout import timeout
from modules.embedvars import setembedvar
from modules.emoji import yep,nope,blob_ban
from modules.getjson import loadServerJson, updateServerJson

cases = [] # [case number,user id]
warnings = [] # [user id,number of warnings]

class modMessage(object):
    id = 0

with open("cogs/blocklist.txt","r") as slurfile:
    blockedwords = slurfile.readlines()
    for i in range(len(blockedwords)):
        blockedwords[i] = blockedwords[i].strip("\n").split(",")

def reactionCheck(r):
    print("")

def loadCases():
    with open('cases.json', 'r') as f:
        cases = json.load(f)
        return cases

def updateCases(cases):
    with open('cases.json', 'w') as f:
        json.dump(cases, f, indent=4)

def calcCaseID(cases):

    if len(cases) == 0:
        cases["caseTotal"] = 1
    else:
        cases["caseTotal"] += 1
    
    updateCases(cases)
    return cases["caseTotal"]

async def caseSetup(self, message, channel, i):

    global foundInChannel, modMessage, modChannel

    detectedMsg = f"""Slur `{blockedwords[i][1]}` was detected in your message.
    It has been forwarded to the server moderation team.
    Action will be taken depending on whether it is a false positive or not.
    Remember: slurs are *strictly prohibited here* and are not okay.
    <@{message.author.id}>"""

    await message.delete()

    cases = loadCases()
    caseID = calcCaseID(cases)

    detectedVar = setembedvar("R","Slur Detected",detectedMsg)
    detectedVar.set_footer(text=f"Case #{caseID}. Note: this may be a false positive. Do not panic, it will be reviewed.")

    foundIn = message.channel.id
    foundInChannel = self.bot.get_channel(foundIn)
    await foundInChannel.send(embed=detectedVar)

    modMsg = f"""Slur `{blockedwords[i][1]}` was detected in a message by {message.author.mention} in channel <#{foundIn}>.
    It read:

    `{message.content}`

    React with:
    - {yep} if you believe this was correct and a warning should be given,
    - {blob_ban} if you believe the message author should be banned, or
    - {nope} if you think it was a false positive."""

    modVar = setembedvar("R","Slur Detected",modMsg)
    modVar.set_footer(text=f"Case #{caseID}")
    modChannel = self.bot.get_channel(channel)

    modMessage = await modChannel.send(embed=modVar)
    await modMessage.add_reaction(yep)
    await modMessage.add_reaction(blob_ban)
    await modMessage.add_reaction(nope)

    case = {
        "criminal":message.author.id,
        "modMessage":modMessage.id,
        "modChannel":channel
    }

    cases[str(caseID)] = case
    updateCases(cases)

class SlurDetector(commands.Cog, name="slurdetector"):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):

        global incidentguild, detectedSlur
        incidentguild = message.guild
        guildid = incidentguild.id
        
        servers = loadServerJson()
        server = servers[str(guildid)]
        enabled = server["slurdetector"]["enabled"]

        if enabled == 1:

            for i in range(len(blockedwords)):
                if blockedwords[i][0] in message.content:
                    detectedSlur = blockedwords[i][1]
                    await caseSetup(self, message, int(server["slurdetector"]["channel"]), i)
        
        else:

            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        match = False

        if payload.member.bot != True:
            cases = loadCases()
            tempCases = cases
            caseTotal = tempCases["caseTotal"]
            tempCases.pop("caseTotal")
            for item in range(1,caseTotal+1):
                if tempCases[str(item)]["modMessage"] == payload.message_id:
                    match = True

        if match == True:

            print("Mod message matched")

            for key, value in cases.items():
                if payload.message_id == value["modMessage"]:
                    caseID = key
                    
            case = cases[caseID]
            criminal = foundInChannel.guild.get_member(case["criminal"])
            modChannel = self.bot.get_channel(case["modChannel"])
            modMessage = await modChannel.fetch_message(case["modMessage"])

            servers = loadServerJson()
            server = servers[str(payload.guild_id)]

            ## Correct and Warnworthy Case

            if str(payload.emoji) == yep:

                print("Reacted with yes")
                await modMessage.clear_reactions()

                if "warnings" in server:
                    warnings = server["warnings"]
                else:
                    server["warnings"] = {}
                    warnings = server["warnings"]
                    servers[str(payload.guild_id)] = server
                    updateServerJson(servers)

                found = False

                for warning in warnings:

                    print(warning,case)

                    if int(warning) == case["criminal"]: # if user id found in warnings file

                        found = True
                        banned = False

                        if int(warning) >= 3:

                            banned = True

                            print("User in warnings file has exceeded 3 warnings, banning...")

                            banMsg = f"""{criminal.mention} exceeded their warnings and was banned for their use of the `{detectedSlur}` slur.
                            Remember, slurs are strictly forbidden, and you will be punished for using them.
                            Thank you!"""

                            await foundInChannel.send(embed=setembedvar("R",f"{blob_ban} Member banned",banMsg,False))
                            await criminal.send(f"You were banned from the `{incidentguild.name}` server for exceeding your warnings regarding use of slurs. Do better.")
                            
                            cases.pop(caseID)
                            cases["caseTotal"] = caseTotal-1
                            updateCases(cases)

                        try:
                            await foundInChannel.guild.ban(criminal)
                        except:
                            banFailEmbed = setembedvar("R",f"Couldn't ban {criminal.name}",f"{nope} User {criminal.mention} couldn't be banned. Make sure the bot has sufficient permissions to do so, or do it manually.")
                            banFailEmbed.set_footer(text=f"Case #{caseID} · Handled by {payload.member.name} // {payload.member.id}")
                            await modChannel.send(embed=banFailEmbed)

                        else:

                            print("Adding one warning to user already in warnings file.")
                            currentWarnings = server["warnings"][str(criminal.id)]
                            server["warnings"][str(criminal.id)] += 1
                            server[str(payload.guild_id)] = server
                            updateServerJson(servers)

                        remainingWarnings = 3 - currentWarnings

                        if banned != True:

                            warnMsg = f"""Hey, {criminal.mention}, we need to talk.
                            Your case, `#{case[0]}`, for saying the `{detectedSlur}` slur, was reviewed, and it was found to be true.
                            You have {remainingWarnings} warning(s) remaining, before, well, the ban hammer strikes.
                            Do better. You know slurs aren't allowed here. So, so, not cool."""

                            reactedVar = setembedvar("G",f"Case #{caseID} Closed",f"{payload.member.mention} reacted with {yep} and so {criminal.mention} was given a warning.",False)
                            warnEmbed = setembedvar("R","Case Reviewed",warnMsg,False).set_embed(text=f"Case #{caseID} · Handled by {payload.member.name} // {payload.member.id}")
                            await foundInChannel.send(embed=warnEmbed)
                            await modChannel.send(embed=reactedVar)

                        else:

                            reactedMsg = f"""{payload.member.mention} reacted with {yep} and so {criminal.mention} was given a warning.
                            However, they exceeded their warnings and so were banned."""
                            await modChannel.send(embed=setembedvar("G",f"Case #{caseID} Closed",reactedMsg,False))

                if found == False:

                    print("User ID not found in warnings, adding...")

                    servers[str(payload.guild_id)]["warnings"][str(criminal.id)] = 1
                    updateServerJson(servers)

                    warnMsg = f"""Hey, {criminal.mention}, we need to talk.
                    Your case, `#{caseID}`, for saying the `{detectedSlur}` slur, was reviewed, and it was found to be true.
                    This is your first infraction, so you have 2 more warnings.
                    Really, you shouldn't need any. You know slurs aren't allowed here.
                    Do better."""

                    warnEmbed = setembedvar("R","Case reviewed",warnMsg)
                    warnEmbed.set_footer(text=f"Case #{caseID} · Handled by {payload.member.name} // {payload.member.id}")

                    await foundInChannel.send(embed=warnEmbed)

                    cases["caseTotal"] = caseTotal-1
                    cases.pop(caseID)
                    updateCases(cases)


            ## Correct and Banworthy Case

            elif str(payload.emoji) == blob_ban:

                        print("Reacted with ban")
                        await modMessage.clear_reactions()
                        await criminal.send(f"You were banned from the `{incidentguild.name}` server for your use of the `{detectedSlur}` slur. Do better.")

                        try:
                            
                            await foundInChannel.guild.ban(criminal)

                            reactedVar = setembedvar("G",f"Case #{caseID} Closed",f"{payload.member.mention} reacted with {blob_ban} and so {criminal.mention} was banned.")
                            await modChannel.send(embed=reactedVar)

                            banMsg = f"""{criminal.mention} was banned for their use of the `{detectedSlur}` slur.
                            Remember, slurs are strictly forbidden, and you will be punished for using them.
                            Thank you!"""

                            banVar = setembedvar("R",f"{blob_ban} Member banned",banMsg)
                            banVar.set_footer(text=f"Case #{caseID} · Handled by {payload.member.name} // {payload.member.id}")
                            await foundInChannel.send(embed=banVar)

                        except:

                            banFailEmbed = setembedvar("R",f"Couldn't ban {criminal.name}",f"{nope} User {criminal.mention} couldn't be banned. Make sure the bot has sufficient permissions to do so, or do it manually.")
                            banFailEmbed.set_footer(text=f"Case #{caseID} · Handled by {payload.member.name} // {payload.member.id}")
                            await modChannel.send(embed=banFailEmbed)

                        cases["caseTotal"] = caseTotal-1
                        cases.pop(caseID)
                        updateCases(cases)

            ## False Positive Case

            elif str(payload.emoji) == nope:

                print("Reacted with no")

                await modMessage.clear_reactions()
                reactedVar = setembedvar("G",f"Case #{caseID} Closed",f"{payload.member.mention} reacted with {nope} and so the case against {criminal.mention} was closed.",False)
                await modChannel.send(embed=reactedVar)                
                falsePositiveMsg = f"""Sorry about that, {criminal.mention}!
                The slur detected was determined to be a false positive by the moderation team.
                Have a wonderful day :)"""
                falsePositiveVar = setembedvar("G","False Positive!",falsePositiveMsg,False)
                falsePositiveVar.set_footer(text=f"Case #{caseID} · Handled by {payload.member.name} // {payload.member.id}")
                await foundInChannel.send(embed=falsePositiveVar)

                cases["caseTotal"] = caseTotal-1
                cases.pop(caseID)
                updateCases(cases)
                    

def setup(bot):
    bot.add_cog(SlurDetector(bot))