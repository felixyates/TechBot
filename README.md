# TechBot

Just a simple Discord bot that I'm trying to build :) I only intend for it to be used for 3 servers - two are mine (the first for solo testing, the second for chilling) and the third is my friend's (also for chilling).

## Features
- [x] Text responder. The bot responds to certain messages with an image.
- [x] Audio player. So many sound effects and songs.
- [ ] YouTube support for the audio player.

## Available commands *(prefix: >)*
*Note, you can view these at any time with the command >help*

### Moderation
* kick {mention-user} - Simple kick command.
* ban {mention-user} - Simple ban command.
* purge {no-of-messages} - Deletes the specified number of messages (up to 100 messages up to 14 days old).

### Voice
* play {file} - Plays the specified sound file. The currently available list is below:
  * fnaf - Plays the FNAF phone call.
  * fortnite - Plays the old Fortnite Christmas music.
  * boom - Plays the Vine boom sound effect.
  * breakfromads - Plays the Spotify 'Wanna break from the ads?' clip.
  * bruh - Plays the bruh sound effect.
  * wifi - Plays the 'Get WiFi anywhere you go' clip.
  * beyondthesea - Plays 'Beyond the Sea' by Bobby Darin.
  * minecraftAlpha - Plays 'Minecraft: Volume Alpha' by C418.
* stop - Stops the currently playing audio in the voice channel.
* volume {0-100} - Sets the volume of the currently playing audio.

### Other
* add {x} {y} - Adds two numbers together
* ping - Returns 'pong' if the bot is active
* servers - Lists some cool beans servers you should join
* hello - Says 'world'
* help - Shows a list of all commands.

### Owner
* shutdown - Shuts the bot down.
* reload {extension} - Reloads the specified extension.
* load {extension} - Loads the specified extension.
* unload {extension} - Unloads the specified extension.
