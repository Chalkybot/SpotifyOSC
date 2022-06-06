#!/usr/bin/python3
from urllib import response
from pythonosc.udp_client import SimpleUDPClient
from refresh import Refresh
from random import seed, randint
from datetime import datetime
import time
import logging
import requests
import katosc
import re
import os
import sys
from pythonosc.udp_client import SimpleUDPClient

URL = "https://api.spotify.com/v1/me/player/currently-playing"
refreshCaller = Refresh()
Headers = { # Headers used for sending API calls
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': ''
        }
if sys.platform == "win32": Clear='cls' 
else: Clear='clear'
#Initializing:
kat =  katosc.KatOsc()
IP, PORT = "127.0.0.1", 9000
SPINNY=['-','\\','|','/']
client = SimpleUDPClient(IP, PORT) 
OldSong=''
#Spotify errors which can be used later on
Spotify_Errors={
     202:'The request has been accepted for processing, but the processing has not been completed.',
     204:'Nothing is playing.',
     400:'Bad request.',
     401:'Authorization failure.',
     403:'Forbidden request.',
     404:'Not found.',
     429:'Rate limited.',
     500:'Internal server error.',
     502:'Bad gateway.',
     504:'Service unavailable.',
    9001:'Error acquiring songJSON.',
    9002:'Error acquiring time'
}

# Refreshing spotify API token:
def error_handling(error):
     with open(os.path.dirname(os.path.realpath(__file__))+'/error.log',"a") as errorLog:
          errorTime=datetime.now()
          if isinstance(error,int): 
               try:
                    print("At {} an error was faced: {}: {}\n".format(errorTime,error,Spotify_Errors[error]))
                    errorLog.write("At {} an error was faced: {}: {}\n".format(errorTime,error,Spotify_Errors[error]))
               except:
                    print("At {} an error was faced: {}\n".format(errorTime,error))
                    errorLog.write("At {} an error was faced: {}\n".format(errorTime,error))
          errorLog.close()

def token_refresh():
     global Headers
     #Binding new token to the Headers
     Headers['Authorization'] = f"Bearer {refreshCaller.refresh()}"

def GetTime(ID):
     url = f"https://api.spotify.com/v1/tracks/{ID}"
     Response=''
     time.sleep(2)
     while Response=='':
          try:
               Response = requests.get(url=url,headers=Headers)
               Time = int(Response.json()['duration_ms'])
          except:
               error_handling(9002)
               time.sleep(30)
               Response=''
               continue
     return Time
     
def Sanitize(text):
       
     for variableName, info in text.items(): # Iterates through the text dictionary
          if isinstance(info,str) and len(info)>32: # If the length of any dictionary is over 31,
               text[variableName] = re.sub("[\(\[].*?[\)\]]", "", text[variableName]) # Or inside of brackets gets cut to reduce the length.
               text[variableName],_,_ =  text[variableName].partition('Remix') # Everything after the word 'Remix',
     return text     

def customColours(name):
     # Initializing a list with 2 spaces to store later generated random floats: 
     ranFloat=[0,0] 
     for i in range(2):
          # Generates a custom seed for random numbers and utilizes running number i
          seed(name+'.'*i)
          # Generating random digits and then turning them into floats 
          ranFloat[i]=randint(0,100)/100
     # Returns random numbers which are stored in a list
     return ranFloat
          
def CurrentSong():
     Response=''
     while Response=='':
          # Calls the Spotify API and stores it in the 'Response' variable.
          try:
               Response = requests.get(URL, headers=Headers)
               # If the response status code is an error code is bigger than 202, indicating an error or no music playing, the status code is returned.
               if Response.status_code > 201 and Response.status_code !=204: 
                    error_handling(Response.status_code)
                    return Response.status_code
               elif Response.status_code > 202 : return Response.status_code
          # If the response status code is not over 202, the response is returned in a json format.
          except:
               error_handling(9001)
               time.sleep(5)
               Response=''
               continue
     return Response.json()
    
def PlayingOSC(Playing, CurrentPosition, Colour, NewSong):
     # Sends the inverse of 'is playing' boolean to VRChat, indicating whether or not music is playing. 
     client.send_message("/avatar/parameters/playing", not Playing)
     if NewSong==True:
          client.send_message("/avatar/parameters/ColourLock", True)
          client.send_message("/avatar/parameters/colour0", Colour[0])
     else:
          client.send_message("/avatar/parameters/ColourLock", False)
          client.send_message("/avatar/parameters/colour0", CurrentPosition)

def GetSongInfo(OldSong):
     # Calls CurrentSong to load the JSON response from spotify.
     songJSON = CurrentSong()
     # Checks if songJSON is an integer, if it is, the number gets returned.
     if isinstance(songJSON,int) : return songJSON
     if songJSON['item']==None: return 901
     SongInfo = { # Deciphers the returned JSON and stores values in SongInfo
          'Name':songJSON['item']['name'],
          'Album':songJSON['item']['album']['name'],
          'Author':songJSON['item']['artists'][0]['name'],
          'Length':GetTime(songJSON['item']['id']),
          'Colours':customColours(songJSON['item']['album']['name']), # Generates custom colours based on the album name.
     }
     Sanitize(SongInfo)
     CurrentPosition=(songJSON['progress_ms']/SongInfo['Length'])
     PlayingOSC(songJSON['is_playing'],CurrentPosition,SongInfo['Colours'],not OldSong==SongInfo) # Updates 'is playing' if music is playing and pushes the lenth of the current song and True to symbolize that it is the previously playing song.
     if OldSong == SongInfo : return 1 # If the Old Song is the same as the current song, the function returns a 1, indicating that no change has occurred
     # Otherwise, the function changes the variable OldSong to be the current song and returns the songinfo variable.
     return SongInfo 

def PushToOSC(text):

     os.system(Clear) # Clears screen
     print(f"\033[32mPushing to OSC \n\033[37mSong name: {text['Name']} \nAlbum: {text['Album']} \nAuthor: {text['Author']}") # Prints the 'Pushing to OSC' text
     
     # Sends the data to KAT which will display it in game
     kat.set_text(f"{text['Name']}\n{text['Album']}\n{text['Author']}")
     #for RunningNumber in range(2): # Sends the colour Floats to VRchat parameters colour0 and colour1.
               #time.sleep(0.25)

def main():
     # Generates a new token
     token_refresh()
     # Updates the Currently Playing
     CurrentlyPlaying = GetSongInfo('')
     if not isinstance(CurrentlyPlaying,int):PushToOSC(CurrentlyPlaying)
     # Loops while no song is playing 
     while True: # Infinite loop 
          for i in range(4):
               time.sleep(2) # Waits a second
               
               _ = GetSongInfo(CurrentlyPlaying)
               if isinstance(_,int):
                    if _ ==401:
                         logging.warning("Refreshing API token...")
                         token_refresh()
                         continue
                    elif _ == 1:
                         print(f"Waiting for change {SPINNY[i]}",end="\r") # If the old and current song are the same, states that music has not changed
                         continue
                    elif _ == 204: 
                         print(f"Nothing is playing {SPINNY[i]}",end="\r")
                         continue
                    elif _>204:
                         error_handling(_)
                         continue
               CurrentlyPlaying = _ # Establishes current song that is playing
               PushToOSC(CurrentlyPlaying) # If the song has changed, calls to push the through OSC
               # 2 seconds


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            print("\r\033[31mKilling KAT and exiting..") # Prints death message
            kat.stop() # Stops KAT
            sys.exit(0) # Exits.
        except SystemExit:
            kat.stop() # Stops KAT
            os._exit(0) # Exits.
     
    
