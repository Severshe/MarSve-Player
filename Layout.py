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
path = "F:\Downloads\MarSve-Player\mp3"
#path = "/Users/Luftikus/Desktop/mp3"
 
root = Tk()
root.title("Mp3 Player MarSve")

list_loc =[] #Liste fuer die Eigentlichen Item Daten der Playlist
currenttrack_id = 0

def addToList():
    playlist.insert(END, os.path.basename(manlist.focus()))
    list_loc.append(manlist.focus())
    
def delFromList():
    idxs = playlist.curselection()
    idx = int(idxs[0])
    playlist.delete(idx)
    list_loc.pop(idx)
    
def nexttrack():
    global currenttrack_id
    currenttrack_id = currenttrack_id + 1
    player.next()
    bar["maximum"] = player.source.duration

def prevtrack():
    global currenttrack_id
    currenttrack_id = currenttrack_id - 1
    idx = currenttrack_id
    player.delete()
    for i in range(idx, len(list_loc)):
        music = pyglet.media.load(list_loc[i])
        player.queue(music)
    bar["maximum"] = player.source.duration
    player.play()
    update_clock()
    
player = pyglet.media.Player()

#############################################################################
#Progressbar Update
#############################################################################
def update_clock():
    if bar["maximum"] != player.source.duration:
        global currenttrack_id
        currenttrack_id = currenttrack_id + 1
        bar["maximum"] = player.source.duration
        print('New ID',currenttrack_id)
    if player.playing:
        threading.Timer(0.25, update_clock).start()
        bar["value"] = player.time
#############################################################################
#Progressbar Update
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
    player.delete()
    for i in range(idx, len(list_loc)):
        music = pyglet.media.load(list_loc[i])
        player.queue(music)
    bar["maximum"] = player.source.duration
    player.play()
    update_clock()
#############################################################################
#Playlist Doubleclick
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

songtext = ttk.Label(playframe, text="Artist - Song")
songtext.grid(column=1, row=1, columnspan=6, sticky=(N, W, E))

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

manlistscroll = ttk.Scrollbar( playframe, orient=VERTICAL, command=playlist.yview)
manlistscroll.grid(column=3, row=4, sticky=(N, E, S))
playlist.configure(yscrollcommand=manlistscroll.set)

hinbutton = ttk.Button(playframe, text='Hinzufuegen', command=addToList)
hinbutton.grid(column=1, row=5, sticky=(W, S))

entbutton = ttk.Button(playframe, text='Entfernen', command=delFromList)
entbutton.grid(column=3, row=5, sticky=(E, S))
#############################################################################
#Layout Elemente
#############################################################################

#############################################################################
#Direct Play
#############################################################################
def direkt_play(event):
    player.delete()
    music = pyglet.media.load(manlist.focus())
    player.queue(music)
    player.play()
    source = player.source
    update_clock()
    return music
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
