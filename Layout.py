import os
from os.path import join, getsize

from tkinter import *
from tkinter import ttk

import pyglet
from pyglet.window import key   #Keyboard und Maus Unterstuetzung

#from pytag import Audio

import math

import threading

#Verzeichnis der zu scannenden Musik und Name der Standardplaylist im Layout.py Ordner
#path = "K:\Musik"
path = "F:\Downloads\MarSve-Player\mp3"
#path = "/Users/Luftikus/Desktop/mp3"
akt_pl = "standard_playlist.lst"
path_pl = "F:\Downloads\MarSve-Player\playlists"

root = Tk()
root.title("Mp3 Player MarSve")

list_loc =[]                        #Liste fuer die Eigentlichen Item Daten der Playlist
currenttrack_id = 0                 #Welche Track in list_loc spielt gerade
currenttrack_length = StringVar()   #Wie lang ist diese Track
currenttrack_name = StringVar()     #Wie ist der Name des Tracks
playlist_changed = False
curIndex = 0

def write_akt_pl():
    with open(akt_pl, 'w') as plfile:
        for i in range (0, len(list_loc)):
            if i < len(list_loc)-1:
                plfile.write(list_loc[i])
                plfile.write('\n')
            else:
                plfile.write(list_loc[i])
    plfile.close()

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
        write_akt_pl()
    
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
        write_akt_pl()
    elif currenttrack_id == idx:
        print("Do not delete current playing track")
    else:
        playlist.delete(idx)
        list_loc.pop(idx)
        playlist_changed = True
        write_akt_pl()
    
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
    
def volup():    #Funktion zur Lautstaerkeerhoehung
    if math.ceil((player.volume + 0.05)*100) <= 105:
        player.volume = player.volume + 0.05
    print(player.volume)
    
def voldown():  #Funktion zur Lautstaerkeverkleinerung
    if math.floor(player.volume - 0.05) >= 0:
        player.volume = player.volume - 0.05
    print(player.volume)
    
def switchToPlaylist():
    manlist.grid_forget()
    manlistscroll.grid_forget()
    pl_ls_list.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))
    pl_ls_listscroll.grid(column=3, row=2, sticky=(N, E, S))
    
def switchToDatMan():
    pl_ls_list.grid_forget()
    pl_ls_listscroll.grid_forget()
    manlist.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))
    manlistscroll.grid(column=3, row=2, sticky=(N, E, S))
    
player = pyglet.media.Player()
player.volume = 0.5

#############################################################################
#Update
#############################################################################
def update_clock():                                     #Funktion fuer regelmaessige Updates 
    if bar["maximum"] != player.source.duration:        #If Routine, falls der Track sich geaendert hat
        global currenttrack_id                          #ohne Eingreifen (automatischer next Track)
        global playlist_changed
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
#Playlistload
#############################################################################
def playlist_load(event):
    global akt_pl
    playlist.delete(0, 'end')
    list_loc.clear()
    if os.path.isfile(pl_ls_list.focus()):
        akt_pl = pl_ls_list.focus()
        with open(pl_ls_list.focus(), 'r') as plfile: #standard Playlist wird geladen
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
#Playlistload
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

datmanbutton =ttk.Button(manager, text='Dateimanager', command=switchToDatMan)
datmanbutton.grid(column=1, row=1, sticky=(N, W))

playlistbutton =ttk.Button(manager, text='Playlists', command=switchToPlaylist)
playlistbutton.grid(column=2, row=1, columnspan=2, sticky=(N, E))

manlist = ttk.Treeview(manager)
manlist.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))
manlist.tag_bind('Play', '<Double-Button-1>', direkt_play)

manlistscroll = ttk.Scrollbar( manager, orient=VERTICAL, command=manlist.yview)
manlistscroll.grid(column=3, row=2, sticky=(N, E, S))
manlist.configure(yscrollcommand=manlistscroll.set)

pl_ls_list = ttk.Treeview(manager)
pl_ls_list.tag_bind('Play', '<Double-Button-1>', playlist_load)

pl_ls_listscroll = ttk.Scrollbar( manager, orient=VERTICAL, command=pl_ls_list.yview)
pl_ls_list.configure(yscrollcommand=pl_ls_listscroll.set)

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
with open(akt_pl, 'r') as plfile: #standard Playlist wird geladen
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

playlistscroll = ttk.Scrollbar( playframe, orient=VERTICAL, command=playlist.yview)
playlistscroll.grid(column=3, row=4, sticky=(N, E, S))
playlist.configure(yscrollcommand=playlistscroll.set)

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
#Dateimanager
#############################################################################
def scanPath(verz, list):
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
                    if os.path.isfile(os.path.join(path[0], path[j][k])):
                        list.insert("", 'end', os.path.join(path[0], path[j][k]), text=path[j][k][:-4], tags='Play')
                    else:
                        list.insert("", 'end', os.path.join(path[0], path[j][k]), text=path[j][k], tags='Play')
                else:
                    if os.path.isfile(os.path.join(path[0], path[j][k])):
                        list.insert(path[0], 'end', os.path.join(path[0], path[j][k]), text=path[j][k][:-4], tags='Play')
                    else:
                        list.insert(path[0], 'end', os.path.join(path[0], path[j][k]), text=path[j][k], tags='Play')
                k += 1
            j += 1
        i += 1
#############################################################################
#Dateimanager
#############################################################################

scanPath(path, manlist)
scanPath(path_pl, pl_ls_list)

for child in mainframe.winfo_children(): child.grid_configure(padx=2, pady=2)
root.mainloop()
