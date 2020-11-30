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
  * anoos
  * [beyondthesea](https://www.youtube.com/watch?v=ptsa21ULFSo) - 'Beyond the Sea' by Bobby Darin.
  * [boom](https://www.youtube.com/watch?v=_vBVGjFdwk4) - Vine boom sound effect.
  * [breakfromads](https://www.youtube.com/watch?v=mtihCM8mzeU) - Spotify 'Wanna Break from the Ads?'.
  * [bruh](https://www.youtube.com/watch?v=2ZIpFytCSVc) - Bruh Sound Effect #2.
  * female
  * [fnaf](https://www.youtube.com/watch?v=zSmEKJ7RIpc) - FNAF Night 1 Phone Call.
  * [fortnite](https://www.youtube.com/watch?v=CjaeNACb5gc) - Fortnite Christmas Music.
  * [minecraftAlpha](https://www.youtube.com/watch?v=6wv84OUmnwg&list=PLHykAyQQdTart3T8wrDjEnAFEmbVstInA) - 'Minecraft: Volume Alpha' by C418.
  * [rl](https://www.youtube.com/watch?v=QHVREB6fdvI) - Rocket League Intro Music / 'All I Need' by Slushii.
  * [wifi](https://www.youtube.com/watch?v=9p0pdiTOlzw) - 'Get WiFi Anywhere You Go' meme.
  * teets
* volume {0-100} - Sets the volume of the currently playing audio.
* stop - Stops the currently playing audio.

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
* spam - Sends all images and GIFs in the Text Responder module (takes some time - rate limited).