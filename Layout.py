#!/usr/bin/env python3

import os

from tkinter import *
from tkinter import ttk

import pyglet

#from pytag import Audio

import math

import threading

#Verzeichnis der zu scannenden Musik und Name der Standardplaylist im Layout.py Ordner
#path Pi:
#path = 
#path_usb = /media
#akt_pl = 
#path_pl = 
#path Martin:
#path = "/Users/Luftikus/Desktop/mp3"
#path_usb =
#akt_pl = 
#path_pl = 
#path Sven:
path = "F:\Downloads\MarSve-Player\mp3"
path_usb = "K:\Musik\Alben"
akt_pl = "standard_playlist.lst"
path_pl = "F:\Downloads\MarSve-Player\playlists"

root = Tk()
root.title("Mp3 Player MarSve")
#root.wm_overrideredirect(True)     #Option fuer randloses Fenster
root.minsize(480, 320)              #Groesse wird auf PiTFT festgelegt
root.maxsize(480, 320)

#Definitionen
list_loc =[]                        #Liste fuer die Eigentlichen Item Daten der Playlist
currenttrack_id = 0                 #Welche Track in list_loc spielt gerade
currenttrack_length = StringVar()   #Wie lang ist diese Track
currenttrack_name = StringVar()     #Wie ist der Name des Tracks
currenttrack_fullname = None
currentplaylist = StringVar()       #Wie ist der Name der aktuellen Playlist
currentplaylist.set(os.path.basename(akt_pl)[:-4])  #Setzt die Playlist auf den Standard
playlist_changed = False            #Globalvar die bei Hinzufuegen und Loeschen von Songs auf True gesetzt wird
curIndex = 0
search_string = StringVar()
search_loc =[]
manager_mode = 0                    #Globalvar in welchem Mode das linke Fenster ist
overlength = 0                      #Globalvar ob currenttrack_name zu lang fuer die Anzeige ist
left_right = 0                      #Globalvar ob der Name nach links oder rechts laeuft
update_runs = 0

player = pyglet.media.Player()
player.volume = 0.5

#Images
#https://www.dropbox.com/s/p27zh500msqtaws/Icon%20Gifs.zip?dl=0
previmg = PhotoImage(file="previmg.gif")
nextimg = PhotoImage(file="nextimg.gif")
playimg = PhotoImage(file="playimg.gif")
pauseimg = PhotoImage(file="pauseimg.gif")
hinimg = PhotoImage(file="Hinzu.gif")
entimg = PhotoImage(file="Entf.gif")
plusimg = PhotoImage(file="Plus.gif")
minusimg = PhotoImage(file="Minus.gif")
USBimg = PhotoImage(file="USB.gif")
searchimg = PhotoImage(file="search.gif")
pllstimg = PhotoImage(file="pllst.gif")
datmanimg = PhotoImage(file="datman.gif")
enterimg = PhotoImage(file="enter.gif")

#############################################################################
#Playlist Funktionen
#############################################################################
#Funktion zum aufbauen der queue aus list_loc
def build_queue():
    for i in range(currenttrack_id, len(list_loc)):
        music = pyglet.media.load(list_loc[i])
        player.queue(music)

#Funktion zum Sichern der aktuellen Playlist
def write_akt_pl():
    with open(akt_pl, 'w') as plfile:
        for i in range (0, len(list_loc)):
            if i < len(list_loc)-1:
                plfile.write(list_loc[i])
                plfile.write('\n')
            else:
                plfile.write(list_loc[i])
    plfile.close()

#Funktion zum laden von Playlists
def playlist_load(event):
    global akt_pl
    playlist.delete(0, 'end')
    list_loc.clear()
    if os.path.isfile(pl_ls_list.focus()):
        akt_pl = pl_ls_list.focus()
        currentplaylist.set(os.path.basename(akt_pl)[:-4])
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

#Funktion zum Hinzufuegen von Songs zur Playlist
def addToList():
    global manager_mode
    global playlist_changed
    if manager_mode == 0:
        if os.path.isfile(manlist.focus()):
            playlist.insert(END, os.path.basename(manlist.focus())[:-4])
            list_loc.append(manlist.focus())
        elif os.path.isdir(manlist.focus()):
            #for Schleife zum erstellen der Dateiliste "path" mit Listenstruktur (aktueller Pfad, unter Pfade, Dateien)
            for path in os.walk(manlist.focus()):
                j = 1
                #for Schleife zum Auslesen von unter Pfaden und Dateien
                for j in range(1, 3):
                    #for Schleife zum Auslesen der eigentlichen Items
                    k = 0
                    for k in range(0,len(path[j])):
                        if os.path.isfile(os.path.join(path[0], path[j][k])):
                            playlist.insert(END, path[j][k][:-4])
                            list_loc.append(os.path.join(path[0], path[j][k]))
                    k += 1
                j += 1
    elif manager_mode == 2:
        idxs = searchlist.curselection()
        idx = int(idxs[0])
        playlist.insert(END, os.path.basename(search_loc[idx])[:-4])
        list_loc.append(search_loc[idx])
    playlist_changed = True
    write_akt_pl()
    
#Funktion zum Loeschen von Songs von der Playlist
def delFromList():
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
    if idx == len(list_loc):
        playlist.selection_set(idx-1)
    else:
        playlist.selection_set(idx)

#############################################################################
#Steuerfunktionen
#############################################################################
#Funktion fuer den naechsten Track
def nexttrack():
    global currenttrack_id
    global playlist_changed
    global currenttrack_fullname
    currenttrack_id = currenttrack_id + 1
    player.next()
    playlist.selection_clear(0, 'end')
    playlist.selection_set(currenttrack_id)
    if playlist_changed:
        player.delete()
        build_queue()
        playlist_changed = False
    currenttrack_fullname = playlist.get(currenttrack_id)
    standard_play()

#Funktion fuer den vorherigen Track
def prevtrack():
    global currenttrack_id
    global currenttrack_fullname
    currenttrack_id = currenttrack_id - 1
    player.delete()
    playlist.selection_clear(0, 'end')
    playlist.selection_set(currenttrack_id)
    build_queue()
    currenttrack_fullname = playlist.get(currenttrack_id)
    standard_play()

#Funktion zur Lautstaerkeerhoehung
def volup():
    if math.ceil((player.volume + 0.05)*100) <= 105:
        player.volume = player.volume + 0.05
        volbar["value"] = player.volume

#Funktion zur Lautstaerkeverkleinerung
def voldown():
    if math.floor(player.volume - 0.05) >= 0:
        player.volume = player.volume - 0.05
        volbar["value"] = player.volume
        
#Funktion zum Durchsuchen der Dateien
def start_search(event):
    global manager_mode
    global path
    global path_usb
    if manager_mode == 0:
        verz = path
    else:
        verz = path_usb
    search_loc.clear()
    searchlist.delete(0, 'end')
    #for Schleife zum Erstellen der Dateiliste "path_i" mit Listenstruktur (aktueller Pfad, unter Pfade, Dateien)
    for path_i in os.walk(verz):
        j = 1
        #for Schleife zum Auslesen von unter Pfaden und Dateien
        for j in range(1, 3):
            #for Schleife zum Auslesen der eigentlichen Items
            k = 0
            for k in range(0,len(path_i[j])):
                if os.path.isfile(os.path.join(path_i[0], path_i[j][k])):
                    if str.casefold(search_string.get()) in str.casefold(path_i[j][k]):
                        search_loc.append(os.path.join(path_i[0], path_i[j][k]))
                        searchlist.insert(END, path_i[j][k][:-4])
                k += 1
            j += 1

#############################################################################
#Wechselfunktionen der Linken Seite
#############################################################################
    
def switchToUSB():                   #Zu USBlist 1
    global manager_mode
    manager_mode = 1
    USBbutton.grid_forget()
    pl_ls_list.grid_forget()
    pl_ls_listscroll.grid_forget()
    manlist.grid_forget()
    manlistscroll.grid_forget()
    searchlist.grid_forget()
    searchcanvas.grid_forget()
    searchlistscroll.grid_forget()
    searchbox.grid_forget()
    searchbutton.grid_forget()
    searchlistbutton.grid_forget()
    searchlistbutton.grid(column=1, row=1, sticky=(N, E))
    datmanbutton.grid(column=1, row=1, sticky=(N, W))
    USBlist.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))
    USBlistscroll.grid(column=3, row=2, sticky=(N, E, S))
    USBlist.delete(*USBlist.get_children())
    scanPath(path_usb, USBlist)         #mp3liste wird erstellt
    
def switchTosearchlist():               #Von zu Searchlist
    global manager_mode
    searchlistbutton.grid_forget()
    pl_ls_list.grid_forget()
    pl_ls_listscroll.grid_forget()
    manlist.grid_forget()
    manlistscroll.grid_forget()
    USBlist.grid_forget()
    USBlistscroll.grid_forget()
    if manager_mode == 0:
        datmanbutton.grid(column=1, row=1, sticky=(N, E))
    else:
        USBbutton.grid(column=1, row=1, sticky=(N, E))
    searchlist.grid(column=1, row=1, columnspan=1, sticky=(N, W, E, S))
    searchcanvas.grid(column=1, row=3, columnspan=3, sticky=(N, W, E, S))
    searchlistscroll.grid(column=1, row=1, sticky=(N, E, S))
    searchbox.grid(column=1, row=2,columnspan=2, sticky=(N, W))
    searchbutton.grid(column=3, row=2, sticky=(N, E))
    searchbox.focus_set()

def switchToPlaylist():                 #Von Dateimanager 0 zu Playlists_lists
    playlistbutton.grid_forget()
    manlist.grid_forget()
    manlistscroll.grid_forget()
    searchlist.grid_forget()
    searchcanvas.grid_forget()
    searchlistscroll.grid_forget()
    searchbox.grid_forget()
    searchbutton.grid_forget()
    searchlistbutton.grid_forget()
    USBlist.grid_forget()
    USBlistscroll.grid_forget()
    datmanbutton.grid(column=1, row=1, sticky=(N, E))
    USBbutton.grid(column=1, row=1, sticky=(N, W))
    pl_ls_list.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))
    pl_ls_listscroll.grid(column=3, row=2, sticky=(N, E, S))
    
def switchToDatMan():                   #Von zu Dateimanager 0
    global manager_mode
    manager_mode = 0
    datmanbutton.grid_forget()
    USBlist.grid_forget()
    USBlistscroll.grid_forget()
    pl_ls_list.grid_forget()
    pl_ls_listscroll.grid_forget()
    searchlist.grid_forget()
    searchcanvas.grid_forget()
    searchlistscroll.grid_forget()
    searchbox.grid_forget()
    searchbutton.grid_forget()
    searchlistbutton.grid_forget()
    playlistbutton.grid(column=1, row=1, sticky=(N, W))
    searchlistbutton.grid(column=1, row=1, sticky=(N, E))
    manlist.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))
    manlistscroll.grid(column=3, row=2, sticky=(N, E, S))


#############################################################################
#Keyboardfunktionen
#############################################################################

def show_keyboard(event):
    keyboardcanvas.grid(column=1, row=1, columnspan=2, sticky=(W, E, S))
    
def hide_keyboard(event):
    keyboardcanvas.grid_forget()
    
def ins_q():
    searchbox.insert(END, 'q')
    
def ins_w():
    searchbox.insert(END, 'w')
    
def ins_e():
    searchbox.insert(END, 'e')
    
def ins_r():
    searchbox.insert(END, 'r')
    
def ins_t():
    searchbox.insert(END, 't')
    
def ins_z():
    searchbox.insert(END, 'z')
    
def ins_u():
    searchbox.insert(END, 'u')
    
def ins_i():
    searchbox.insert(END, 'i')
    
def ins_o():
    searchbox.insert(END, 'o')
    
def ins_p():
    searchbox.insert(END, 'p')
    
def ins_bs():
    if searchbox.selection_present():
        searchbox.delete("sel.first", "sel.last")
    else:
        searchbox.delete(len(searchbox.get())-1)
    
def ins_a():
    searchbox.insert(END, 'a')
    
def ins_s():
    searchbox.insert(END, 's')
    
def ins_d():
    searchbox.insert(END, 'd')
    
def ins_f():
    searchbox.insert(END, 'f')
    
def ins_g():
    searchbox.insert(END, 'g')
    
def ins_h():
    searchbox.insert(END, 'h')
    
def ins_j():
    searchbox.insert(END, 'j')
    
def ins_k():
    searchbox.insert(END, 'k')
    
def ins_l():
    searchbox.insert(END, 'l')
    
def ins_ent():
    start_search('<Return>')
    
def ins_y():
    searchbox.insert(END, 'y')
    
def ins_x():
    searchbox.insert(END, 'x')
    
def ins_c():
    searchbox.insert(END, 'c')
    
def ins_v():
    searchbox.insert(END, 'v')
    
def ins_b():
    searchbox.insert(END, 'b')
    
def ins_n():
    searchbox.insert(END, 'n')
    
def ins_m():
    searchbox.insert(END, 'm')
    
def ins_spc():
    searchbox.insert(END, ' ')

#############################################################################
#Update
#############################################################################
def update_clock():                                     #Funktion fuer regelmaessige Updates 
    global overlength
    global left_right
    global update_runs
    global currenttrack_fullname
    if probar["maximum"] != player.source.duration:        #If Routine, falls der Track sich geaendert hat
        global currenttrack_id                          #ohne Eingreifen (automatischer next Track)
        global playlist_changed
        currenttrack_id = currenttrack_id + 1
        if playlist_changed:
            player.delete()
            build_queue()
            player.play()
            playlist_changed = False
        probar["maximum"] = player.source.duration         #Das Maximum der Progressbar wird gesetzt
        overlength=0
            
    if player.playing:
        update_runs = 1
        threading.Timer(0.25, update_clock).start()     #Intervall in dem Updates geschehen
        
        tracklength = math.ceil(player.source.duration) #Berechnung der Tracklenge in min und sec
        tracksec = math.fmod (tracklength, 60)
        trackmin = (tracklength-tracksec)/60
            
        playlength = math.ceil(player.time)             #Berechnung der Spiellaenge in min und sec
        playsec = math.fmod (playlength, 60)
        playmin = (playlength-playsec)/60
        currenttrack_length.set('%i:%.2i/%i:%.2i' %(playmin, playsec, trackmin, tracksec))
        probar["value"] = player.time                      #Der Fortschritt der Progressbar wird gesetzt
        if len(currenttrack_fullname) > 36:
            if left_right == 0:
                currenttrack_name.set(currenttrack_fullname[overlength:(36+overlength)])
                overlength += 1
            if left_right == 1:
                currenttrack_name.set(currenttrack_fullname[overlength:(36+overlength)])
                overlength -= 1
            if overlength == 0:
                left_right = 0
            elif overlength == len(playlist.get(currenttrack_id))-36:
                left_right = 1
        else:
            currenttrack_name.set(currenttrack_fullname)

#############################################################################
#Play Funktionen
#############################################################################

def standard_play():
    global update_runs
    global left_right
    global overlength
    left_right = 0
    overlength = 0
    playbutton["image"]=pauseimg
    player.play()
    probar["maximum"] = player.source.duration
    if update_runs == 0:
        update_clock()

#Play/Pause
def play_pause():
    global currenttrack_id
    global update_runs
    if player.playing:
        player.pause()
        playbutton["image"]=playimg
        update_runs = 0
    else:
        if not player.source:
            build_queue()
            currenttrack_id = currenttrack_id - 1
        if player.time >= player.source.duration:
            player.seek(0)
        playlist.selection_clear(0, 'end')
        playlist.selection_set(currenttrack_id)
        standard_play()
        update_clock()

#Direct Play der Searchlist
def searchlist_play(event):
    global currenttrack_fullname
    idxs = searchlist.curselection()
    idx = int(idxs[0])
    player.delete()                             #Queue wird geloescht
    music = pyglet.media.load(search_loc[idx])
    player.queue(music)
    #currenttrack_name.set(searchlist.get(idx)[:-4][:36]) #Der Name des aktuellen Tracks wird gesetzt
    currenttrack_fullname = searchlist.get(idx)
    standard_play()

#Direct Play des Dateitrees
def direkt_play(event):
    global currenttrack_fullname
    if os.path.isfile(manlist.focus()):
        player.delete()
        music = pyglet.media.load(manlist.focus())
        player.queue(music)
        source = player.source
        #currenttrack_name.set(os.path.basename(manlist.focus())[:-4]) #Der Name des aktuellen Tracks wird gesetzt
        currenttrack_fullname = os.path.basename(manlist.focus())[:-4]
        standard_play()

#Track aus Playlist wird gestartet
def playlist_play(event):
    global currenttrack_fullname
    global currenttrack_id
    idxs = playlist.curselection()
    idx = int(idxs[0])
    currenttrack_id = idx
    player.delete() #Queue wird geloescht
    build_queue()
    #currenttrack_name.set(playlist.get(currenttrack_id)[:36]) #Der Name des aktuellen Tracks wird gesetzt
    currenttrack_fullname = playlist.get(currenttrack_id)
    standard_play()

#############################################################################
#Playlist Drag and Drop Funktionen
#############################################################################
def setCurrent(event):
    global curIndex
    curIndex = playlist.nearest(event.y)

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
    write_akt_pl()

#############################################################################
#Layout Elemente
#############################################################################
#Frames
mainframe = ttk.Frame(root, padding="3 3 3 3")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

manager = ttk.Frame(mainframe, padding="3 3 3 3", width =210)
manager.grid_propagate(False)
manager.grid(column=1, row=1, sticky=(N, W, S))

playframe = ttk.Frame(mainframe, padding="3 3 3 3")
playframe.grid(column=2, row=1, sticky=(N, E, S))

#Search Window
searchlistbutton = ttk.Button(manager, width=2, image=searchimg, command=switchTosearchlist)
searchlistbutton.grid(column=1, row=1, sticky=(N, E))

searchcanvas = Canvas(manager, height = 350, width = 200)
searchcanvas.grid_propagate(False)

searchlist = Listbox(searchcanvas, width = 34, height =15)
searchlist.bind('<Double-Button-1>', searchlist_play)

searchlistscroll = ttk.Scrollbar(searchcanvas, orient=VERTICAL, command=searchlist.yview)
searchlist.configure(yscrollcommand=searchlistscroll.set)

searchbox = ttk.Entry(manager, width=27, textvariable=search_string)
searchbox.bind('<Return>', start_search('<Return>'))
searchbox.bind('<FocusIn>', show_keyboard)
searchbox.bind('<FocusOut>', hide_keyboard)

searchbutton = ttk.Button(manager, width=2, image=searchimg, command=lambda: start_search('<Return>'))

#Datei Manager Window
datmanbutton = ttk.Button(manager, width=2, image=datmanimg, command=switchToDatMan)

manlist = ttk.Treeview(manager, height = 12)
manlist.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))
manlist.tag_bind('Play', '<Double-Button-1>', direkt_play)

manlistscroll = ttk.Scrollbar( manager, orient=VERTICAL, command=manlist.yview)
manlistscroll.grid(column=3, row=2, sticky=(N, E, S))
manlist.configure(yscrollcommand=manlistscroll.set)

#USB Window
USBbutton = ttk.Button(manager, width=2, image=USBimg, command=switchToUSB)

USBlist = ttk.Treeview(manager, height = 12)
USBlist.tag_bind('Play', '<Double-Button-1>', direkt_play)

USBlistscroll = ttk.Scrollbar( manager, orient=VERTICAL, command=USBlist.yview)
USBlist.configure(yscrollcommand=USBlistscroll.set)

#Playlist Window
playlistbutton = ttk.Button(manager, width=2, image=pllstimg, command=switchToPlaylist)
playlistbutton.grid(column=1, row=1, sticky=(N, W))

akt_pl_txt = ttk.Label(manager, textvariable=currentplaylist)
akt_pl_txt.grid(column=2, row=1, columnspan=2, sticky=(N, W))

pl_ls_list = ttk.Treeview(manager, height = 12)
pl_ls_list.tag_bind('Play', '<Double-Button-1>', playlist_load)

pl_ls_listscroll = ttk.Scrollbar( manager, orient=VERTICAL, command=pl_ls_list.yview)
pl_ls_list.configure(yscrollcommand=pl_ls_listscroll.set)

#Rechte Frame
textcanvas = Canvas(playframe, height = 10, width = 200)
textcanvas.grid(column=1, row=1, columnspan=6, sticky=(N, E, S))
textcanvas.grid_propagate(False)

songtext = ttk.Label(textcanvas, textvariable=currenttrack_name)
songtext.grid(column=1, row=1, columnspan=1, sticky=(N, W))

songlength = ttk.Label(playframe, textvariable=currenttrack_length)
songlength.grid(column=7, row=1, sticky=(N, E))

#Buttons
prevbutton = ttk.Button(playframe, width=2, image=previmg, command=prevtrack)
prevbutton.grid(column=3, row=2, sticky=(N, E, S))

nextbutton = ttk.Button(playframe, width=2, image=nextimg,  command=nexttrack)
nextbutton.grid(column=5, row=2, sticky=(N, W, S))

playbutton = ttk.Button(playframe, width=2, image=playimg,  command=play_pause)
playbutton.grid(column=4, row=2)

hinbutton = ttk.Button(playframe, width=2, image=hinimg, command=addToList)
hinbutton.grid(column=1, row=2, sticky=(E, S))

entbutton = ttk.Button(playframe, width=2, image=entimg, command=delFromList)
entbutton.grid(column=2, row=2, sticky=(W, S))

plusbutton = ttk.Button(playframe, width=2, image=plusimg, command=volup)
plusbutton.grid(column=7, row=2, sticky=(W, S))

minusbutton = ttk.Button(playframe, width=2, image=minusimg, command=voldown)
minusbutton.grid(column=6, row=2, sticky=(E, S))

volbar = ttk.Progressbar(playframe, orient=VERTICAL, length=10, mode='determinate', value=0.5, maximum=1)
volbar.grid(column=7, row=2, columnspan=1, sticky=(N, E, S))

#Progressbar
barcanvas = Canvas(playframe, height = 5, width = 250)
barcanvas.grid(column=1, row=3, columnspan=7, sticky=(N, W, E, S))
barcanvas.grid_propagate(False)

probar = ttk.Progressbar(barcanvas, orient=HORIZONTAL, length=250, mode='determinate')
probar.grid(column=1, row=1, columnspan=1, sticky=(N, W, E, S))

#Playlist
playlist = Listbox(playframe, height = 15)
playlist.grid(column=1, row=4, columnspan=7, sticky=(N, W, E, S))
playlist.bind('<Double-Button-1>', playlist_play)
playlist.bind('<Button-1>', setCurrent)
playlist.bind('<B1-Motion>', shiftSelection)

playlistscroll = ttk.Scrollbar( playframe, orient=VERTICAL, command=playlist.yview)
playlistscroll.grid(column=7, row=4, sticky=(N, E, S))
playlist.configure(yscrollcommand=playlistscroll.set)

#Standard Playlist wird aus standard_playlist.lst geladen
with open(akt_pl, 'r') as plfile: #standard Playlist wird in plfile geladen
    standard_playlist = plfile.readlines()
for i in range (0, len(standard_playlist)):
    if i < len(standard_playlist)-1:
        playlist.insert(END, os.path.basename(standard_playlist[i])[:-5])
        list_loc.append(standard_playlist[i][:-1])
    elif i == len(standard_playlist)-1:
        playlist.insert(END, os.path.basename(standard_playlist[i])[:-4])
        list_loc.append(standard_playlist[i])
plfile.close()

#############################################################################
#Display Keyboard
#############################################################################
keystyle = ttk.Style()
keystyle.configure('Key.TButton', font="Helvetica 20 bold")

keyboardcanvas = Canvas(mainframe, height = 150, width = 320)
keyboardcanvas.bind('<FocusOut>', hide_keyboard)
keyboardcanvas.bind('<FocusIn>', show_keyboard)

qbutton = ttk.Button(keyboardcanvas, width=2, text='q', style = "Key.TButton", command=ins_q)
qbutton.grid(column=1, row=1)

wbutton = ttk.Button(keyboardcanvas, width=2, text='w', style = "Key.TButton", command=ins_w)
wbutton.grid(column=2, row=1)

ebutton = ttk.Button(keyboardcanvas, width=2, text='e', style = "Key.TButton", command=ins_e)
ebutton.grid(column=3, row=1)

rbutton = ttk.Button(keyboardcanvas, width=2, text='r', style = "Key.TButton", command=ins_r)
rbutton.grid(column=4, row=1)

tbutton = ttk.Button(keyboardcanvas, width=2, text='t', style = "Key.TButton", command=ins_t)
tbutton.grid(column=5, row=1)

zbutton = ttk.Button(keyboardcanvas, width=2, text='z', style = "Key.TButton", command=ins_z)
zbutton.grid(column=6, row=1)

ubutton = ttk.Button(keyboardcanvas, width=2, text='u', style = "Key.TButton", command=ins_u)
ubutton.grid(column=7, row=1)

ibutton = ttk.Button(keyboardcanvas, width=2, text='i', style = "Key.TButton", command=ins_i)
ibutton.grid(column=8, row=1)

obutton = ttk.Button(keyboardcanvas, width=2, text='o', style = "Key.TButton", command=ins_o)
obutton.grid(column=9, row=1)

pbutton = ttk.Button(keyboardcanvas, width=2, text='p', style = "Key.TButton",command=ins_p)
pbutton.grid(column=10, row=1)

bsbutton = ttk.Button(keyboardcanvas, width=3, text='del', style = "Key.TButton", command=ins_bs)
bsbutton.grid(column=11, row=1)

abutton = ttk.Button(keyboardcanvas, width=2, text='a', style = "Key.TButton", command=ins_a)
abutton.grid(column=1, row=2)

sbutton = ttk.Button(keyboardcanvas, width=2, text='s', style = "Key.TButton", command=ins_s)
sbutton.grid(column=2, row=2)

dbutton = ttk.Button(keyboardcanvas, width=2, text='d', style = "Key.TButton", command=ins_d)
dbutton.grid(column=3, row=2)

fbutton = ttk.Button(keyboardcanvas, width=2, text='f', style = "Key.TButton", command=ins_f)
fbutton.grid(column=4, row=2)

gbutton = ttk.Button(keyboardcanvas, width=2, text='g', style = "Key.TButton", command=ins_g)
gbutton.grid(column=5, row=2)

hbutton = ttk.Button(keyboardcanvas, width=2, text='h', style = "Key.TButton", command=ins_h)
hbutton.grid(column=6, row=2)

jbutton = ttk.Button(keyboardcanvas, width=2, text='j', style = "Key.TButton", command=ins_j)
jbutton.grid(column=7, row=2)

kbutton = ttk.Button(keyboardcanvas, width=2, text='k', style = "Key.TButton", command=ins_k)
kbutton.grid(column=8, row=2)

lbutton = ttk.Button(keyboardcanvas, width=2, text='l', style = "Key.TButton", command=ins_l)
lbutton.grid(column=9, row=2)

entbutton = ttk.Button(keyboardcanvas, width=2, image=enterimg, style = "Key.TButton", command=ins_ent)
entbutton.grid(column=10, row=2)

ybutton = ttk.Button(keyboardcanvas, width=2, text='y', style = "Key.TButton", command=ins_y)
ybutton.grid(column=1, row=3)

xbutton = ttk.Button(keyboardcanvas, width=2, text='x', style = "Key.TButton", command=ins_x)
xbutton.grid(column=2, row=3)

cbutton = ttk.Button(keyboardcanvas, width=2, text='c', style = "Key.TButton", command=ins_c)
cbutton.grid(column=3, row=3)

vbutton = ttk.Button(keyboardcanvas, width=2, text='v', style = "Key.TButton", command=ins_v)
vbutton.grid(column=4, row=3)

bbutton = ttk.Button(keyboardcanvas, width=2, text='b', style = "Key.TButton", command=ins_b)
bbutton.grid(column=5, row=3)

nbutton = ttk.Button(keyboardcanvas, width=2, text='n', style = "Key.TButton", command=ins_n)
nbutton.grid(column=6, row=3)

mbutton = ttk.Button(keyboardcanvas, width=2, text='j', style = "Key.TButton", command=ins_m)
mbutton.grid(column=7, row=3)

spacebutton = ttk.Button(keyboardcanvas, width=6, text='', style = "Key.TButton", command=ins_spc)
spacebutton.grid(column=8, row=3,columnspan=3)
#############################################################################
#Display Keyboard
#############################################################################


#Scanfunktion (Zu scannendes Verzeichnis, Treeview zum eintragen)
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

scanPath(path, manlist)         #mp3liste wird erstellt
scanPath(path_pl, pl_ls_list)   #Playlist Liste wird erstellt

for child in mainframe.winfo_children(): child.grid_configure(padx=2, pady=2)
keyboardcanvas.grid_forget()
root.mainloop()
