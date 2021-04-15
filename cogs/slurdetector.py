import discord, asyncio, os
from discord.ext import commands
from async_timeout import timeout
from modules.embedvars import setembedvar
from modules.emoji import yep,nope,blob_ban
import sqlite3

cases = [] # [case number,user id]
warnings = [] # [user id,number of warnings]

with open("cogs/servers.txt","r") as serversfile: # guildid,modchannelid
    servers = serversfile.readlines()
    for i in range(len(servers)):
        servers[i] = servers[i].strip("\n").split(",")
        print(f"Server: {servers[i][0]}, Mod Channel: {servers[i][1]}")

with open("cogs/blocklist.txt","r") as slurfile:
    blockedwords = slurfile.readlines()
    for i in range(len(blockedwords)):
        blockedwords[i] = blockedwords[i].strip("\n").split(",")

class SlurDetector(commands.Cog, name="slurdetector"):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):
        global incidentguild, detectedSlur, case, criminal, foundInChannel, modMessage, modChannel
        incidentguild = message.guild
        guildid = incidentguild.id
        for s in range(len(servers)):
            if int(servers[s][0]) == guildid:
                channel = int(servers[s][1])
                for i in range(len(blockedwords)):
                    if blockedwords[i][0] in message.content:
                        detectedMsg = f"""Slur `{blockedwords[i][1]}` was detected in your message.
                        It has been forwarded to the server moderation team.
                        Action will be taken depending on whether it is a false positive or not.
                        <@{message.author.id}>
                        """
                        detectedSlur = blockedwords[i][1]
                        case = [] # case number, user id
                        criminal = message.author
                        case.append(len(cases) + 1)
                        case.append(message.author.id)
                        cases.append(case)
                        print("\n--- NEW CASE ---\n" + str(case) + "\n" + str(cases) + "\n------\n")
                        await message.delete()
                        detectedVar = setembedvar("R","Slur Detected",detectedMsg,False)
                        detectedVar.set_footer(text="Note: this may be a false positive. Do not panic, it will be reviewed.")
                        foundIn = message.channel.id
                        foundInChannel = self.bot.get_channel(foundIn)
                        await foundInChannel.send(embed=detectedVar)

                        modMsg = f"""Slur `{blockedwords[i][1]}` was detected in a message by <@{case[1]}> in channel <#{foundIn}>.
                        It read:

                        `{message.content}`

                        React with:
                        - {yep} if you believe this was correct and a warning should be given,
                        - {blob_ban} if you believe the message author should be banned, or
                        - {nope} if you think it was a false positive."""

                        modVar = setembedvar("R","Slur Detected",modMsg,False)
                        modVar.set_footer(text=f"Case #{case[0]}")
                        modChannel = self.bot.get_channel(channel)
                        modMessage = await modChannel.send(embed=modVar)
                        await modMessage.add_reaction(yep)
                        await modMessage.add_reaction(blob_ban)
                        await modMessage.add_reaction(nope)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji = ['blob_ban','yep','nope']
        for i in range(len(emoji)):
            if payload.emoji == emoji[i]:
                if (payload.message_id == modMessage.id) and (payload.member.bot != True):

                    ## Correct and Warnworthy Case

                    if str(payload.emoji) == yep:
                        print("Reacted with yes")
                        await modMessage.clear_reactions()
                        warningfile = open("cogs/warnings.txt","r")
                        warnings = warningfile.readlines()
                        warningfile.close()
                        for i in range(len(warnings)):
                            warnings[i] = warnings[i].strip("\n").split(",") # [userid,warnings]
                        print(warnings)
                        found = False
                        for record in range(len(warnings)):
                            if int(warnings[record][0]) == int(case[1]): # if user id found in warnings file
                                found = True
                                banned = False
                                if int(warnings[record][1]) >= 3:
                                    banned = True
                                    print("User in warnings file has exceeded 3 warnings, banning...")
                                    banMsg = f"""{criminal.mention} exceeded their warnings and was banned for their use of the `{detectedSlur}` slur.
                                    Remember, slurs are strictly forbidden, and you will be punished for using them.
                                    Thank you!"""
                                    banVar = setembedvar("R",f"{blob_ban} Member banned",banMsg,False)
                                    await foundInChannel.send(embed=banVar)
                                    await criminal.send(f"You were banned from the `{incidentguild.name}` server for exceeding your warnings regarding use of slurs. Do better.")
                                    await foundInChannel.guild.ban(criminal)
                                else:
                                    print("Adding one warning to user already in warnings file.")
                                    warningNumber = (int(warnings[record][1]) + 1) # add one warning to user in database
                                    warnings[record][1] = warningNumber
                                    with open("cogs/warnings.txt","w") as warningfile:
                                        for record in range(len(warnings)):
                                            warningfile.write(f"{warnings[record][0]},{warnings[record][1]}"+"\n")
                                        warningfile.close()

                                remainingWarnings = 3 - int(warnings[record][1])
                                if banned != True:
                                    warnMsg = f"""Hey, {criminal.mention}, we need to talk.
                                    Your case, `#{case[0]}`, for saying the `{detectedSlur}` slur, was reviewed, and it was found to be true.
                                    You have {remainingWarnings} warning(s) remaining, before, well, the ban hammer strikes.
                                    Do better. You know slurs aren't allowed here. So, so, not cool."""
                                    warnVar = setembedvar("R","Case Reviewed",warnMsg,False)
                                    await foundInChannel.send(embed=warnVar)
                                    reactedVar = setembedvar("G","Case Closed",f"{payload.member.mention} reacted with {yep} and so {criminal.mention} was given a warning.",False)
                                    await modChannel.send(embed=reactedVar)
                                else:
                                    reactedMsg = f"""{payload.member.mention} reacted with {yep} and so {criminal.mention} was given a warning.
                                    However, they exceeded their warnings and so were banned."""
                                    reactedVar = setembedvar("G","Case Closed",reactedMsg,False)
                                    await modChannel.send(embed=reactedVar)


                        if found == False:
                            print("User ID not found in warnings file, adding...")
                            with open("cogs/warnings.txt","a") as warningfile:
                                warningfile.write(f"{case[1]},1"+"\n")
                                warningfile.close()
                            warnMsg = f"""Hey, {criminal.mention}, we need to talk.
                            Your case, `#{case[0]}`, for saying the `{detectedSlur}` slur, was reviewed, and it was found to be true.
                            This is your first infraction, so you have 2 more warnings.
                            Really, you shouldn't need any. You know slurs aren't allowed here.
                            Do better."""
                            warnVar = setembedvar("R","Case reviewed",warnMsg,False)
                            await foundInChannel.send(embed=warnVar)

                        for record in range(len(cases)):
                            if cases[record][0] == case[0]:
                                print("\n--- Removing case from caselist. Before: ---\n")
                                print(cases)
                                cases.pop(record)
                                print("\n--- Updated caselist: ---\n")
                                print(cases)
                
                        with open("cogs/warnings.txt","r") as warningfile:
                            warnings = warningfile.readlines()
                            warningfile.close()
                            print("\n--- Updated warnings file: ---\n")
                            print(warnings)

                    ## Correct and Banworthy Case

                    elif str(payload.emoji) == blob_ban:
                        print("Reacted with ban")
                        await modMessage.clear_reactions()
                        reactedVar = setembedvar("G","Case Closed",f"{payload.member.mention} reacted with {blob_ban} and so {criminal.mention} was banned.",False)
                        await modChannel.send(embed=reactedVar)
                        banMsg = f"""{criminal.mention} was banned for their use of the `{detectedSlur}` slur.
                        Remember, slurs are strictly forbidden, and you will be punished for using them.
                        Thank you!"""
                        banVar = setembedvar("R",f"{blob_ban} Member banned",banMsg,False)
                        await foundInChannel.send(embed=banVar)
                        await criminal.send(f"You were banned from the `{incidentguild.name}` server for your use of the `{detectedSlur}` slur. Do better.")
                        await foundInChannel.guild.ban(criminal)
                        for record in range(len(cases)):
                            if cases[record][0] == case[0]:
                                print("Removing case. Before:")
                                print(cases)
                                cases.pop(record)
                                print("Updated caselist:")
                                print(cases)

                    ## False Positive Case

                    elif str(payload.emoji) == nope:
                        print("Reacted with no")
                        await modMessage.clear_reactions()
                        reactedVar = setembedvar("G","Case Closed",f"{payload.member.mention} reacted with {nope} and so the case against {criminal.mention} was closed.",False)
                        await modChannel.send(embed=reactedVar)                
                        falsePositiveMsg = f"""Sorry about that, <@{case[1]}>!
                        The slur detected was determined to be a false positive by the moderation team.
                        Have a wonderful day :)"""
                        falsePositiveVar = setembedvar("G","False Positive!",falsePositiveMsg,False)
                        falsePositiveVar.set_footer(text=f"Case #{case[0]}")
                        await foundInChannel.send(embed=falsePositiveVar)
                        for record in range(len(cases)):
                            if cases[record][0] == case[0]:
                                print("Removing case. Before:")
                                print(cases)
                                cases.pop(record)
                                print("Updated caselist:")
                                print(cases)

def setup(bot):
    bot.add_cog(SlurDetector(bot))