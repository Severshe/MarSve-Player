# TEST TEST TEST

import os
from os.path import join, getsize

from tkinter import *
from tkinter import ttk

import pyglet
from pyglet.window import key   #Keyboard und Maus Unterstuetzung

#from pytag import Audio

import math

import threading

#path = "K:\Musik"
#path = "F:\Downloads\MarSve-Player\mp3"
path = "/Users/Luftikus/Desktop/mp3"

root = Tk()
root.title("Mp3 Player MarSve")

list_loc =[]                        #Liste fuer die Eigentlichen Item Daten der Playlist
currenttrack_id = 0                 #Welche Track in list_loc spielt gerade
currenttrack_length = StringVar()   #Wie lang ist diese Track
currenttrack_name = StringVar()     #Wie ist der Name des Tracks
playlist_changed = False
curIndex = 0

def build_queue():  #Funktion zum aufbauen der queue aus list_loc
    for i in range(currenttrack_id, len(list_loc)):
        music = pyglet.media.load(list_loc[i])
        player.queue(music)

def addToList():    #Funktion zum Hinzufuegen von Songs zur Playlist
    if os.path.isfile(manlist.focus()):
        global playlist_changed
        playlist.insert(END, os.path.basename(manlist.focus())[:-4])
        list_loc.append(manlist.focus())
        playlist_changed = True
        with open('standard_playlist.lst', 'a') as plfile:
            plfile.write('\n')
            plfile.write(manlist.focus())
        plfile.close()
    
def delFromList():                                      #Funktion zum Loeschen von Songs von der Playlist
    idxs = playlist.curselection()                      #Welcher Eintrag ist angewaehlt
    idx = int(idxs[0])                                  #Nummer des Eintrags
    loc_time = player.time                              #Momentane Abspielzeit wird gespeichert
    global playlist_changed
    global currenttrack_id
    if currenttrack_id > idx:                           #Falls der zu loeschende Eintrag vor dem Spielenden ist
        currenttrack_id = currenttrack_id - 1           #Muss die currenttrack_id verringert werden
        playlist.delete(idx)
        list_loc.pop(idx)
    elif currenttrack_id == idx:
        print("Do not delete current playing track")
    else:
        playlist.delete(idx)
        list_loc.pop(idx)
        playlist_changed = True
        with open('standard_playlist.lst', 'w') as plfile:
            for i in range (0, len(list_loc)):
                if i < len(list_loc)-1:
                    plfile.write(list_loc[i])
                    plfile.write('\n')
                else:
                    plfile.write(list_loc[i])
        plfile.close()
    
def nexttrack():                            #Funktion fuer den naechsten Track
    global currenttrack_id
    global playlist_changed
    currenttrack_id = currenttrack_id + 1
    player.next()
    playlist.selection_clear(0, 'end')
    playlist.selection_set(currenttrack_id)
    if playlist_changed:
        player.delete()
        build_queue()
        playlist_changed = False
    player.play()
    bar["maximum"] = player.source.duration

def prevtrack():                                #Funktion fuer den vorherigen Track
    global currenttrack_id
    currenttrack_id = currenttrack_id - 1
    player.delete()
    playlist.selection_clear(0, 'end')
    playlist.selection_set(currenttrack_id)
    build_queue()
    bar["maximum"] = player.source.duration
    player.play()
    update_clock()
    
def volup():    #Funktion zur Lautstärkeerhöhung
    if math.ceil((player.volume + 0.05)*100) <= 105:
        player.volume = player.volume + 0.05
    print(player.volume)
    
def voldown():  #Funktion zur Lautstärkeverkleinerung
    if math.floor(player.volume - 0.05) >= 0:
        player.volume = player.volume - 0.05
    print(player.volume)
    
player = pyglet.media.Player()
player.volume = 0.5

#############################################################################
#Update
#############################################################################
def update_clock():                                     #Funktion fuer regelmaessige Updates 
    if bar["maximum"] != player.source.duration:        #If Routine, falls der Track sich geaendert hat
        global currenttrack_id                          #ohne Eingreifen (automatischer next Track)
        global playlist_changed
        #playlist_changed = true
        currenttrack_id = currenttrack_id + 1
        if playlist_changed:
            player.delete()
            build_queue()
            player.play()
            playlist_changed = False
        bar["maximum"] = player.source.duration         #Das Maximum der Progressbar wird gesetzt
            
    if player.playing:
        threading.Timer(0.25, update_clock).start()     #Intervall in dem Updates geschehen
        
        tracklength = math.ceil(player.source.duration) #Berechnung der Tracklenge in min und sec
        tracksec = math.fmod (tracklength, 60)
        trackmin = (tracklength-tracksec)/60
            
        playlength = math.ceil(player.time)             #Berechnung der Spiellaenge in min und sec
        playsec = math.fmod (playlength, 60)
        playmin = (playlength-playsec)/60
        currenttrack_length.set('%i:%.2i/%i:%.2i' %(playmin, playsec, trackmin, tracksec))
        
        currenttrack_name.set(playlist.get(currenttrack_id)) #Der Name des aktuellen Tracks wird gesetzt
        
        bar["value"] = player.time                      #Der Fortschritt der Progressbar wird gesetzt
#############################################################################
#Update
#############################################################################

#############################################################################
#Play/Pause
#############################################################################
def play_pause():
    if player.playing:
        player.pause()
    else:
        if player.time >= player.source.duration:
            player.seek(0)
        player.play()
        playlist.selection_clear(0, 'end')
        playlist.selection_set(currenttrack_id)
        update_clock()
#############################################################################
#Play/Pause
#############################################################################

#############################################################################
#Playlist Doubleclick
#############################################################################
def playlist_play(event):
    idxs = playlist.curselection()
    idx = int(idxs[0])
    global currenttrack_id
    currenttrack_id = idx
    player.delete()                             #Queue wird geloescht
    build_queue()
    bar["maximum"] = player.source.duration
    player.play()
    update_clock()
#############################################################################
#Playlist Doubleclick
#############################################################################

#############################################################################
#Playlist Click Noetig?
#############################################################################
def setCurrent(event):
    global curIndex
    curIndex = playlist.nearest(event.y)
#############################################################################
#Playlist Click Noetig?
#############################################################################

#############################################################################
#Playlist Drag
#############################################################################
def shiftSelection(event):
    global curIndex
    i = playlist.nearest(event.y)
    if i < curIndex:
        x = playlist.get(i)
        x_list = list_loc[i]      
        playlist.delete(i)
        list_loc.pop(i)
        playlist.insert(i+1, x)
        list_loc.insert(i+1, x_list)
        curIndex = i
    elif i > curIndex:
        x = playlist.get(i)
        x_list = list_loc[i]
        playlist.delete(i)
        list_loc.pop(i)
        playlist.insert(i-1, x)
        list_loc.insert(i-1, x_list)
        curIndex = i
#############################################################################
#Playlist Drag
#############################################################################

#############################################################################
#Layout Elemente
#############################################################################
mainframe = ttk.Frame(root, padding="3 3 3 3")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

manager = ttk.Frame(mainframe, padding="3 3 3 3")
manager.grid(column=1, row=1, sticky=(N, W, S))

playframe = ttk.Frame(mainframe, padding="3 3 3 3")
playframe.grid(column=2, row=1, sticky=(N, E, S))

datmanbutton =ttk.Button(manager, text='Dateimanager')
datmanbutton.grid(column=1, row=1, sticky=(N, W))

playlistbutton =ttk.Button(manager, text='Playlists')
playlistbutton.grid(column=2, row=1, columnspan=2, sticky=(N, E))

manlist = ttk.Treeview(manager)
manlist.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))

manlistscroll = ttk.Scrollbar( manager, orient=VERTICAL, command=manlist.yview)
manlistscroll.grid(column=3, row=2, sticky=(N, E, S))
manlist.configure(yscrollcommand=manlistscroll.set)

songtext = ttk.Label(playframe, textvariable=currenttrack_name)
songtext.grid(column=1, row=1, columnspan=4, sticky=(N, W))

songlength = ttk.Label(playframe, textvariable=currenttrack_length)
songlength.grid(column=3, row=1, sticky=(N, E))

prevbutton = ttk.Button(playframe, text='Prev', command=prevtrack)
prevbutton.grid(column=1, row=2, sticky=(N, W, E, S))

playbutton = ttk.Button(playframe, text='Play', command=play_pause)
playbutton.grid(column=2, row=2, sticky=(N, W, E, S))

bar =ttk.Progressbar(playframe, orient=HORIZONTAL, length=200, mode='determinate')
bar.grid(column=1, row=3, columnspan=3, sticky=(N, W, E, S))

nextbutton = ttk.Button(playframe, text='Next', command=nexttrack)
nextbutton.grid(column=3, row=2, sticky=(N, W, E, S))

playlist = Listbox(playframe)
playlist.grid(column=1, row=4, columnspan=3, sticky=(N, W, E, S))
playlist.bind('<Double-Button-1>', playlist_play)
playlist.bind('<Button-1>', setCurrent)
playlist.bind('<B1-Motion>', shiftSelection)

#############################################################################
#Standard Playlist wird aus standard_playlist.lst geladen
#############################################################################
with open('standard_playlist.lst', 'r') as plfile: #standard Playlist wird geladen
    standard_playlist = plfile.readlines()
for i in range (0, len(standard_playlist)):     #standard Playlist wird uebertragen
    if i < len(standard_playlist)-1:
        playlist.insert(END, os.path.basename(standard_playlist[i])[:-5])
        list_loc.append(standard_playlist[i][:-1])
    elif i == len(standard_playlist)-1:
        playlist.insert(END, os.path.basename(standard_playlist[i])[:-4])
        list_loc.append(standard_playlist[i])
plfile.close()
#############################################################################
#Standard Playlist wird aus standard_playlist.lst geladen
#############################################################################

manlistscroll = ttk.Scrollbar( playframe, orient=VERTICAL, command=playlist.yview)
manlistscroll.grid(column=3, row=4, sticky=(N, E, S))
playlist.configure(yscrollcommand=manlistscroll.set)

hinbutton = ttk.Button(playframe, text='Hinzufuegen', command=addToList)
hinbutton.grid(column=1, row=5, sticky=(W, S))

entbutton = ttk.Button(playframe, text='Entfernen', command=delFromList)
entbutton.grid(column=3, row=5, sticky=(E, S))

plusbutton = ttk.Button(playframe, width= 2, text='+', command=volup)
plusbutton.grid(column=2, row=5, sticky=(E, S))

minusbutton = ttk.Button(playframe, width= 2, text='-', command=voldown)
minusbutton.grid(column=2, row=5, sticky=(W, S))
#############################################################################
#Layout Elemente
#############################################################################

#############################################################################
#Direct Play
#############################################################################
def direkt_play(event):
    if os.path.isfile(manlist.focus()):
        player.delete()
        music = pyglet.media.load(manlist.focus())
        player.queue(music)
        player.play()
        source = player.source
        update_clock()
#############################################################################
#Direct Play
#############################################################################

#############################################################################
#Dateimanager
#############################################################################
def scanPath(verz):
    i = 0
    #for Schleife zum erstellen der Dateiliste "path" mit Listenstruktur (aktueller Pfad, unter Pfade, Dateien)
    for path in os.walk(verz):
        j = 1
        #for Schleife zum Auslesen von unter Pfaden und Dateien
        for j in range(1, 3):
            #for Schleife zum Auslesen der eigentlichen Items
            k = 0
            for k in range(0,len(path[j])):
                if i==0:
                    manlist.insert("", 'end', os.path.join(path[0], path[j][k]), text=path[j][k], tags='Play')
                    manlist.tag_bind('Play', '<Double-Button-1>', direkt_play)
                else:
                    manlist.insert(path[0], 'end', os.path.join(path[0], path[j][k]), text=path[j][k], tags='Play')
                    manlist.tag_bind('Play', '<Double-Button-1>', direkt_play)
                k += 1
            j += 1
        i += 1
#############################################################################
#Dateimanager
#############################################################################

scanPath(path)

for child in mainframe.winfo_children(): child.grid_configure(padx=2, pady=2)
root.mainloop()
