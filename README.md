# SpotifyOSC
Syncs spotify with VRChat using OSC.
Synching is done via pinging the Spotify API and requesting the song name, author, album name and the currrent position in the song.
The script pushes out the Author, album name & artist, the current position and a random float value based on the album name. 
Text is handled through [KAT](https://github.com/killfrenzy96/KatOscApp "KAT's Github page") and I use the random float value to generate a pseudorandom cover art for each album. 
The minimum required memory to run this and still have all the functionality is 35 bits but I recommend using 51 bits in order to have faster synching on the text, the text will appear sluggishly with 35 bits.

# Setting up
By default, the script is set up to run on Linux, I have not tested it on windows but it should run fine.
Acquire your Spotify secret and tokens, there are tutorials for getting them online, I will not be explaining the process in this repo.
1. Clone this repo
2. Clone KATOSC in the same directory
3. Install pythonosc using pip
4. Add your spotify secret and tokens to the secrets.py

As as a sidenote, I have not included unity files in this Github repo, everything you need is available in [Kat's repo](https://github.com/killfrenzy96/KatOscApp "KAT's Github page") or is otherwise easily reproducable. 

# Known issues
I've noticed an issue where the get requests being sent to spotify will start failing, It's not Spotify sending 429s, but something else, I don't think it's from Spotify's side, I'm unsure what it is. The "fix" for this is to idle for 30 seconds. Sometimes this fails, if it does, you'll need to restart the script. 
