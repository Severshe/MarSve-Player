#!/usr/bin/env python3
#############################################################################
#   {Table of Conent}
#   {C01}   Verzeichnisse
#   {C02}   Definitionen und Globalvars
#   {C03}   Bilder
#   {C04}   Playlist Funktionen
#   {C05}   Steuerfunktionen
#   {C06}   Wechselfunktionen der Linken Seite
#   {C07}   Keyboardfunktionen
#   {C08}   Updatefunktion
#   {C09}   Optionen Funktionen
#   {C10}   Play Funktionen
#   {C11}   Playlist Drag and Drop Funktionen
#   {C12}   Layout Elemente
#   {C13}   Display Keyboard
#   {C14}   Scanfunktion 
#############################################################################

import os
import sys
import shutil

from tkinter import *
from tkinter import ttk

import pyglet

import random

if not sys.platform == "win32":
    from pytag import Audio

import math

import threading
#############################################################################
#{C01} Verzeichnis der zu scannenden Musik und Name der Standardplaylist im Layout.py Ordner
#############################################################################
#path Pi:
# path_main = "/media/pi/USBSTICK/MarSve-Player"
# path_usb = "/media/pi/USBSTICK/MP3-Player"
# akt_pl = "standard_playlist.lst"
# path_pl = "/media/pi/USBSTICK/MarSve-Player/playlists"
#path Martin:
#path_main = "/Users/Luftikus/Desktop/mp3"
#path_usb =
#akt_pl = 
#path_pl = 
#path Sven:
path_main = "F:\Downloads\MarSve-Player\mp3"
path_usb = "K:\Musik\MP3-Player"
akt_pl = "standard_playlist.lst"
path_pl = "F:\Downloads\MarSve-Player\playlists"

if not os.path.isdir(os.path.join(path_main, "USB")):
    os.mkdir(os.path.join(path_main, "USB"), mode=0o777)

root = Tk()
root.title("Mp3 Player MarSve")
#os.system("sudo pkill lxpanel")
#root.wm_overrideredirect(True)     #Option fuer randloses Fenster
root.minsize(480, 320)              #Groesse wird auf PiTFT festgelegt
root.maxsize(480, 320)

player = pyglet.media.Player()

if sys.platform == "linux":
    os.system("amixer -q sset 'Master' 50%")

#############################################################################
#{C02} Definitionen und Globalvars
#############################################################################
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
manager_mode = 0                    #Globalvar in welchem Mode das linke Fenster ist (DatMan = 0, USB = 1, Playlst = 2)
search_mode = False                 #Globalvar ob im Suchmodes
overlength = 0                      #Globalvar ob und wieviel currenttrack_name zu lang fuer die Anzeige ist
left_right = False                  #Globalvar ob der Name nach links oder rechts laeuft
update_runs = False                 #Globalvar ob die Updatefunktion laeuft
options_show = False                #Globalvar ob die Optionen gezeigt werden
shuffle_var = BooleanVar()
shuffle_var.set(False)
copy_var = BooleanVar()
copy_var.set(False)
create_string = StringVar()
message_string = StringVar()
master_volume = 50

player.volume = 0.5

#############################################################################
#{C03} Images
#############################################################################
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
optionimg = PhotoImage(file="options.gif")
refreshimg = PhotoImage(file="refresh.gif")
exitimg = PhotoImage(file="exit.gif")
folderimg = PhotoImage(file="folder.gif")
clistimg = PhotoImage(file="c_list.gif")
confirmimg = PhotoImage(file="confirm.gif")

#############################################################################
#{C04} Playlist Funktionen
#############################################################################

#Funktion zum pruefen des verfuegbaren Speichers in MB
def getFreeSpace( Laufwerk ):
    MB_txt = os.popen( 'dir %s\\' % Laufwerk ).readlines()
    MB_txt = MB_txt[-1]
    MB_txt = MB_txt.split(",")[1]
    MB_txt = MB_txt.split("Bytes")[0]
    MB_txt = "".join( MB_txt.split(".") )
    MB_txt = int(MB_txt) / 1024 / 1024
    GB_txt = int(MB_txt / 1024)
    MB_txt = int(MB_txt - GB_txt * 1024)
    txt = [GB_txt , MB_txt]
    return txt

#Funktion zum aufbauen der queue aus list_loc
def build_queue():
    global currenttrack_id
    global shuffle_var
    if shuffle_var.get() == True:
        shuffle_id = currenttrack_id
        while shuffle_id == currenttrack_id:
            currenttrack_id = random.randrange(0, len(list_loc), 1)
    if currenttrack_id == len(list_loc)-1:
        music = pyglet.media.load(list_loc[currenttrack_id])
        player.queue(music)
        music = pyglet.media.load(list_loc[0])
        player.queue(music)
    else:
        music = pyglet.media.load(list_loc[currenttrack_id])
        player.queue(music)
        music = pyglet.media.load(list_loc[currenttrack_id+1])
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
    global playlist_changed
    playlist.delete(0, 'end')
    list_loc.clear()
    if os.path.isfile(pl_ls_list.focus()):
        akt_pl = pl_ls_list.focus()
        currentplaylist.set(os.path.basename(akt_pl)[:-4])
        with open(pl_ls_list.focus(), 'r') as plfile:   #standard Playlist wird geladen
            standard_playlist = plfile.readlines()
        for i in range (0, len(standard_playlist)):     #standard Playlist wird uebertragen
            if i < len(standard_playlist)-1:
                playlist.insert(END, os.path.basename(standard_playlist[i])[:-5])
                list_loc.append(standard_playlist[i][:-1])
            elif i == len(standard_playlist)-1:
                playlist.insert(END, os.path.basename(standard_playlist[i])[:-4])
                list_loc.append(standard_playlist[i])
            plfile.close()
    playlist_changed = True

#Funktion zum Hinzufuegen von Songs zur Playlist
def addToList():
    global manager_mode
    global playlist_changed
    global search_mode
    global copy_var
    global path_main
    if manager_mode == 0 and not search_mode:
        if os.path.isfile(manlist.focus()) and manlist.focus()[-4:] == ".mp3":
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
                        if os.path.isfile(os.path.join(path[0], path[j][k])) and path[j][k][-4:] == ".mp3":
                            playlist.insert(END, path[j][k][:-4])
                            list_loc.append(os.path.join(path[0], path[j][k]))
                    k += 1
                j += 1
    elif manager_mode == 1 and not search_mode:
        if copy_var == False:
            if os.path.isfile(USBlist.focus()) and USBlist.focus()[-4:] == ".mp3":
                playlist.insert(END, os.path.basename(USBlist.focus())[:-4])
                list_loc.append(USBlist.focus())
            elif os.path.isdir(USBlist.focus()):
                #for Schleife zum erstellen der Dateiliste "path" mit Listenstruktur (aktueller Pfad, unter Pfade, Dateien)
                for path in os.walk(USBlist.focus()):
                    j = 1
                    #for Schleife zum Auslesen von unter Pfaden und Dateien
                    for j in range(1, 3):
                        #for Schleife zum Auslesen der eigentlichen Items
                        k = 0
                        for k in range(0,len(path[j])):
                            if os.path.isfile(os.path.join(path[0], path[j][k])) and path[j][k][-4:] == ".mp3":
                                playlist.insert(END, path[j][k][:-4])
                                list_loc.append(os.path.join(path[0], path[j][k]))
                        k += 1
                    j += 1
        else:
            if os.path.isfile(USBlist.focus()) and USBlist.focus()[-4:] == ".mp3":
                shutil.copy(USBlist.focus(),os.path.join(path_main,"USB"))
                playlist.insert(END, os.path.basename(USBlist.focus())[:-4])
                list_loc.append(os.path.join(os.path.join(path_main,"USB"),os.path.basename(USBlist.focus())))
            elif os.path.isdir(USBlist.focus()):
                # for Schleife zum erstellen der Dateiliste "path" mit Listenstruktur (aktueller Pfad, unter Pfade, Dateien)
                for path in os.walk(USBlist.focus()):
                    j = 1
                    # for Schleife zum Auslesen von unter Pfaden und Dateien
                    for j in range(1, 3):
                        # for Schleife zum Auslesen der eigentlichen Items
                        k = 0
                        for k in range(0,len(path[j])):
                            if os.path.isfile(os.path.join(path[0], path[j][k])) and path[j][k][-4:] == ".mp3":
                                playlist.insert(END, path[j][k][:-4])
                                list_loc.append(os.path.join(path[0], path[j][k]))
                        k += 1
                    j += 1
    elif search_mode:
        idxs = searchlist.curselection()
        idx = int(idxs[0])
        playlist.insert(END, os.path.basename(search_loc[idx])[:-4])
        list_loc.append(search_loc[idx])
    elif manager_mode == 2:
        playlist_load('<Button-1>')
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
#{C05} Steuerfunktionen
#############################################################################
#Funktion fuer den naechsten Track
def nexttrack():
    global currenttrack_id
    global playlist_changed
    global currenttrack_fullname
    if currenttrack_id == len(list_loc)-1:
        currenttrack_id = 0
    else:
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
    if currenttrack_id == 0:
        currenttrack_id = len(list_loc)-1
    else:
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
    global path_main
    global path_usb
    if manager_mode == 0:
        verz = path_main
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
                if os.path.isfile(os.path.join(path_i[0], path_i[j][k])) and path_i[j][k][-4:] == ".mp3":
                    if str.casefold(search_string.get()) in str.casefold(path_i[j][k]):
                        search_loc.append(os.path.join(path_i[0], path_i[j][k]))
                        searchlist.insert(END, path_i[j][k][:-4])
                k += 1
            j += 1

#############################################################################
#{C06} Wechselfunktionen der Linken Seite
#############################################################################
    
def switchToUSB():                   #Zu USBlist
    global manager_mode
    global search_mode
    manager_mode = 1
    search_mode = False
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
    hide_confirm()
    delete_list_button.state(['disabled'])
    create_folder_button.state(['disabled'])
    create_pllst_button.state(['disabled'])
    create_entry.state(['disabled'])
    searchlistbutton.grid(column=1, row=1, sticky=(N, E))
    datmanbutton.grid(column=1, row=1, sticky=(N))
    USBlist.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))
    USBlistscroll.grid(column=3, row=2, sticky=(N, E, S))
    #USBlist.delete(*USBlist.get_children())
    
def switchTosearchlist():               #Zu Searchlist
    global manager_mode
    global search_mode
    search_mode = True
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
    global search_mode
    global manager_mode
    manager_mode = 2
    search_mode = False
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
    delete_list_button.state(['!disabled'])
    create_folder_button.state(['!disabled'])
    create_pllst_button.state(['!disabled'])
    create_entry.state(['!disabled'])
    datmanbutton.grid(column=1, row=1, sticky=(N, E))
    USBbutton.grid(column=1, row=1, sticky=(N))
    pl_ls_list.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))
    pl_ls_listscroll.grid(column=3, row=2, sticky=(N, E, S))
    
def switchToDatMan():                   #Von zu Dateimanager 0
    global manager_mode
    global search_mode
    manager_mode = 0
    search_mode = False
    datmanbutton.grid_forget()
    USBbutton.grid_forget()
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
    hide_confirm()
    delete_list_button.state(['disabled'])
    create_folder_button.state(['disabled'])
    create_pllst_button.state(['disabled'])
    create_entry.state(['disabled'])
    playlistbutton.grid(column=1, row=1, sticky=(N))
    searchlistbutton.grid(column=1, row=1, sticky=(N, E))
    manlist.grid(column=1, row=2, columnspan=3, sticky=(N, W, E, S))
    manlistscroll.grid(column=3, row=2, sticky=(N, E, S))

def switchOptions():
    global options_show
    message_string.set(str(getFreeSpace(path_main)[0]) + " GB " + str(getFreeSpace(path_main)[1]) + " MB frei")
    if options_show == False:
        optioncanvas.grid_propagate(False)
        optioncanvas.grid(column=1, row=1, columnspan=2, sticky=(N, E))
        options_show = True
    elif options_show == True:
        optioncanvas.grid_forget()
        options_show = False

#############################################################################
#{C07} Keyboardfunktionen
#############################################################################

def show_keyboard(event):
    keyboardcanvas.grid(column=1, row=1, columnspan=2, sticky=(W, E, S))
    
def hide_keyboard(event):
    keyboardcanvas.grid_forget()
    
def ins_q():
    if search_mode:
        searchbox.insert(END, 'q')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'q')
    
def ins_w():
    if search_mode:
        searchbox.insert(END, 'w')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'w')
    
def ins_e():
    if search_mode:
        searchbox.insert(END, 'e')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'e')
    
def ins_r():
    if search_mode:
        searchbox.insert(END, 'r')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'r')
    
def ins_t():
    if search_mode:
        searchbox.insert(END, 't')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 't')
    
def ins_z():
    if search_mode:
        searchbox.insert(END, 'z')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'z')
    
def ins_u():
    if search_mode:
        searchbox.insert(END, 'u')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'u')
    
def ins_i():
    if search_mode:
        searchbox.insert(END, 'i')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'i')
    
def ins_o():
    if search_mode:
        searchbox.insert(END, 'o')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'o')
    
def ins_p():
    if search_mode:
        searchbox.insert(END, 'p')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'p')
    
def ins_bs():
    if search_mode:
        if searchbox.selection_present():
            searchbox.delete("sel.first", "sel.last")
        else:
            searchbox.delete(len(searchbox.get())-1)
    if options_show and manager_mode == 2:
        if create_entry.selection_present():
            create_entry.delete("sel.first", "sel.last")
        else:
            create_entry.delete(len(create_entry.get())-1)
    
def ins_a():
    if search_mode:
        searchbox.insert(END, 'a')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'a')
    
def ins_s():
    if search_mode:
        searchbox.insert(END, 's')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 's')
    
def ins_d():
    if search_mode:
        searchbox.insert(END, 'd')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'd')
    
def ins_f():
    if search_mode:
        searchbox.insert(END, 'f')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'f')
    
def ins_g():
    if search_mode:
        searchbox.insert(END, 'g')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'g')
    
def ins_h():
    if search_mode:
        searchbox.insert(END, 'h')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'h')
    
def ins_j():
    if search_mode:
        searchbox.insert(END, 'j')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'j')
    
def ins_k():
    if search_mode:
        searchbox.insert(END, 'k')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'k')
    
def ins_l():
    if search_mode:
        searchbox.insert(END, 'l')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'l')
    
def ins_ent():
    if search_mode:
        start_search('<Return>')
    
def ins_y():
    if search_mode:
        searchbox.insert(END, 'y')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'y')
    
def ins_x():
    if search_mode:
        searchbox.insert(END, 'x')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'x')
    
def ins_c():
    if search_mode:
        searchbox.insert(END, 'c')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'c')
    
def ins_v():
    if search_mode:
        searchbox.insert(END, 'v')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'v')
    
def ins_b():
    if search_mode:
        searchbox.insert(END, 'b')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'b')
    
def ins_n():
    if search_mode:
        searchbox.insert(END, 'n')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'n')
    
def ins_m():
    if search_mode:
        searchbox.insert(END, 'm')
    if options_show and manager_mode == 2:
        create_entry.insert(END, 'm')
    
def ins_spc():
    if search_mode:
        searchbox.insert(END, ' ')
    if options_show and manager_mode == 2:
        create_entry.insert(END, ' ')

#############################################################################
#{C08} Updatefunktion
#############################################################################
def update_clock():                                     #Funktion fuer regelmaessige Updates 
    global overlength
    global left_right
    global update_runs
    global currenttrack_fullname
    global currenttrack_id
    global playlist_changed
    if probar["maximum"] != player.source.duration:        #If Routine, falls der Track sich geaendert hat
        if currenttrack_id == len(list_loc)-1:
            currenttrack_id = 0                            #ohne Eingreifen (automatischer next Track)
        else:
            currenttrack_id = currenttrack_id + 1
        player.delete()
        build_queue()
        player.play()
        playlist_changed = False
        currenttrack_fullname = currenttrack_fullname = playlist.get(currenttrack_id)
        probar["maximum"] = player.source.duration         #Das Maximum der Progressbar wird gesetzt
        overlength=0
            
    if player.playing:
        update_runs = True
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
            if not left_right:
                currenttrack_name.set(currenttrack_fullname[overlength:(36+overlength)])
                overlength += 1
            else:
                currenttrack_name.set(currenttrack_fullname[overlength:(36+overlength)])
                overlength -= 1
            if overlength == 0:
                left_right = False
            elif overlength == len(playlist.get(currenttrack_id))-36:
                left_right = True
        else:
            currenttrack_name.set(currenttrack_fullname)

#############################################################################
#{C09} Optionen Funktionen
#############################################################################
            
def refreshUSB():
    for i in USBlist.get_children():
        USBlist.delete(i)
    scanPath(path_usb, USBlist)         #USBliste wird erstellt
    
#Exit Funktion
def exit_player():
    player.delete()
    exit()

#Create Folder Funktion
def create_Folder():
    if create_string.get() != "":                   #Es werden keine Ordner ohne Namen erstellt
        if os.path.isfile(pl_ls_list.focus()):
            os.mkdir(os.path.join(os.path.dirname(pl_ls_list.focus()), create_string.get()), mode=0o777)
        elif os.path.isdir(pl_ls_list.focus()):
            os.mkdir(os.path.join(pl_ls_list.focus(), create_string.get()), mode=0o777)
        for i in pl_ls_list.get_children():         #Playlist Liste wird erstellt
            pl_ls_list.delete(i)
        scanPath(path_pl, pl_ls_list)
    
#Create Playlist Funktion
def create_List():                                  #Es werden keine Ordner ohne Namen erstellt
    if create_string.get() != "":
        if os.path.isfile(pl_ls_list.focus()):
            file =os.open(os.path.join(os.path.dirname(pl_ls_list.focus()), create_string.get() + ".lst"), os.O_CREAT, mode=0o777)
            os.close(file)
        elif os.path.isdir(pl_ls_list.focus()):
            file = os.open(os.path.join(pl_ls_list.focus(), create_string.get() + ".lst"), os.O_CREAT, mode=0o777)
            os.close(file)
        for i in pl_ls_list.get_children():         #Playlist Liste wird erstellt
            pl_ls_list.delete(i)
        scanPath(path_pl, pl_ls_list)

def show_confirm():
    message_string.set("Sicher?")
    confirm_txt.grid(column=3, row=3, sticky=(N), padx=5)
    confirm_button.grid(column=3, row=4, sticky=(N))
    decline_txt.grid(column=3, row=5, sticky=(N), padx=5)
    decline_button.grid(column=3, row=6, sticky=(N))
    
def hide_confirm():
    message_string.set(str(getFreeSpace(path_main)[0]) + " GB " + str(getFreeSpace(path_main)[1]) + " MB frei")
    confirm_txt.grid_forget()
    confirm_button.grid_forget()
    decline_txt.grid_forget()
    decline_button.grid_forget()
    
def delPlaylist():
    if os.path.isfile(pl_ls_list.focus()):
        os.remove(pl_ls_list.focus())
    elif os.path.isdir(pl_ls_list.focus()):
        os.rmdir(pl_ls_list.focus())
    for i in pl_ls_list.get_children():         #Playlist Liste wird erstellt
        pl_ls_list.delete(i)
    scanPath(path_pl, pl_ls_list)
    hide_confirm()

def mastervol_down():
    if sys.platform == "linux" and master_volume > 0:
        os.system("amixer -q sset 'Master' 5%-")
        master_volume = master_volume - 5
        message_string.set(str(master_volume))
        
def mastervol_up():
    if sys.platform == "linux" and master_volume < 100:
        os.system("amixer -q sset 'Master' 5%+")
        master_volume = master_volume + 5
        message_string.set(str(master_volume))
        
#############################################################################
#{C10} Play Funktionen
#############################################################################

def standard_play():
    global update_runs
    global left_right
    global overlength
    left_right = False
    overlength = 0
    playbutton["image"]=pauseimg
    player.play()
    probar["maximum"] = player.source.duration
    if not update_runs:
        update_clock()

#Play/Pause
def play_pause():
    global currenttrack_id
    global currenttrack_fullname
    global update_runs
    if player.playing:
        player.pause()
        playbutton["image"]=playimg
        update_runs = False
    else:
        if not player.source:
            build_queue()
            currenttrack_fullname = playlist.get(currenttrack_id)
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
    currenttrack_fullname = searchlist.get(idx)
    standard_play()

#Direct Play des Dateitrees
def direkt_play(event):
    global currenttrack_fullname
    global manager_mode
    if os.path.isfile(manlist.focus()) and manlist.focus()[-4:] == ".mp3" and manager_mode == 0:
        player.delete()
        music = pyglet.media.load(manlist.focus())
        player.queue(music)
        source = player.source
        currenttrack_fullname = os.path.basename(manlist.focus())[:-4]
        standard_play()
    elif os.path.isfile(USBlist.focus()) and USBlist.focus()[-4:] == ".mp3" and manager_mode == 1:
        player.delete()
        music = pyglet.media.load(USBlist.focus())
        player.queue(music)
        source = player.source
        currenttrack_fullname = os.path.basename(USBlist.focus())[:-4]
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
    currenttrack_fullname = playlist.get(currenttrack_id)
    standard_play()

#############################################################################
#{C11} Playlist Drag and Drop Funktionen
#############################################################################
def setCurrent(event):
    global curIndex
    curIndex = playlist.nearest(event.y)

def shiftSelection(event):
    global curIndex
    global playlist_changed
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
    playlist_changed = True
    write_akt_pl()

#############################################################################
#{C12} Layout Elemente
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

#Option Window
optioncanvas = Canvas(mainframe, height = 170, width = 375, bd=5, relief = RAISED, highlightthickness=0)
optioncanvas.grid_propagate(False)
optioncanvas.create_line((75, 0, 75, 160))
optioncanvas.create_line((158, 0, 158, 160))
optioncanvas.create_line((200, 0, 200, 160))

refreshUSB_txt = ttk.Label(optioncanvas, text=("Refresh USB"))
refreshUSB_txt.grid(column=1, row=1, sticky=(N), padx = 5, pady = 5)

refreshUSBbutton = ttk.Button(optioncanvas, width=2, image=refreshimg, command=refreshUSB)
refreshUSBbutton.grid(column=1, row=2, sticky=(N))

shuffle_txt = ttk.Label(optioncanvas, text=("Shuffle"))
shuffle_txt.grid(column=1, row=3, sticky=(N))

shuffle_box = ttk.Checkbutton(optioncanvas, variable=shuffle_var, onvalue=True, offvalue=False)
shuffle_box.grid(column=1, row=4, sticky=(N))

copy_txt = ttk.Label(optioncanvas, text=("USB Copy"))
copy_txt.grid(column=1, row=5, sticky=(N))

copy_box = ttk.Checkbutton(optioncanvas, variable=copy_var, onvalue=True, offvalue=False)
copy_box.grid(column=1, row=6, sticky=(N), pady=3)

create_folder_txt = ttk.Label(optioncanvas, text=("Create Folder"))
create_folder_txt.grid(column=2, row=1, sticky=(N), padx = 3, pady = 5)

create_folder_button = ttk.Button(optioncanvas, width=2, image=folderimg, command=create_Folder)
create_folder_button.grid(column=2, row=2, sticky=(N))
create_folder_button.state(['disabled'])

create_pllst_txt = ttk.Label(optioncanvas, text=("Create Playlist"))
create_pllst_txt.grid(column=2, row=3, sticky=(N))

create_pllst_button = ttk.Button(optioncanvas, width=2, image=clistimg, command=create_List)
create_pllst_button.grid(column=2, row=4, sticky=(N))
create_pllst_button.state(['disabled'])

filename_txt = ttk.Label(optioncanvas, text=("Name:"))
filename_txt.grid(column=2, row=5, sticky=(N))

create_entry = ttk.Entry(optioncanvas, width=12, textvariable=create_string)
create_entry.grid(column=2, row=6, sticky=(N))
create_entry.state(['disabled'])
create_entry.bind('<Return>', start_search('<Return>'))
create_entry.bind('<FocusIn>', show_keyboard)
create_entry.bind('<FocusOut>', hide_keyboard)

exit_txt = ttk.Label(optioncanvas, text=("Exit"))
exit_txt.grid(column=7, row=1, sticky=(N), padx = 3, pady = 5)

exitbutton = ttk.Button(optioncanvas, width=2, image=exitimg, command=exit_player)
exitbutton.grid(column=7, row=2, sticky=(N))

delete_list_txt = ttk.Label(optioncanvas, text=("Delete"))
delete_list_txt.grid(column=3, row=1, sticky=(N), padx = 5, pady = 5)

delete_list_button = ttk.Button(optioncanvas, width=2, image=entimg, command=show_confirm)
delete_list_button.state(['disabled'])
delete_list_button.grid(column=3, row=2, sticky=(N))

confirm_txt = ttk.Label(optioncanvas, text=("Ja"))

confirm_button = ttk.Button(optioncanvas, width=2, image=confirmimg, command=delPlaylist)

decline_txt = ttk.Label(optioncanvas, text=("Nein"))

decline_button = ttk.Button(optioncanvas, width=2, image=entimg, command=hide_confirm)

mastervol_txt = ttk.Label(optioncanvas, text=("Master Volume"))
mastervol_txt.grid(column=4, row=1, columnspan=2, sticky=(N), pady = 5)

mastervol_down_button = ttk.Button(optioncanvas, width=2, image=minusimg, command=mastervol_down)
mastervol_down_button.grid(column=4, row=2, sticky=(N))

mastervol_up_button = ttk.Button(optioncanvas, width=2, image=plusimg, command=mastervol_up)
mastervol_up_button.grid(column=5, row=2, sticky=(N))

placeholder_txt1 = ttk.Label(optioncanvas, text="")
placeholder_txt1.grid(column=4, row=3, sticky=(N), padx = 20)

placeholder_txt2 = ttk.Label(optioncanvas, text=" ")
placeholder_txt2.grid(column=5, row=3, sticky=(N), padx = 20)

placeholder_txt3 = ttk.Label(optioncanvas, text=" ")
placeholder_txt3.grid(column=6, row=3, sticky=(N), padx = 20)

message_txt = ttk.Entry(optioncanvas, width=50,  textvariable=message_string)
message_txt.grid(column=1, row=7, columnspan = 7, rowspan=2, sticky=(S, E, W),padx =5, pady=5)
message_txt.state(['disabled'])
message_string.set("Dies ist ein Test abcdefghijklmnopqrstuvwxyz1234567890")

#Datei Manager Window
datmanbutton = ttk.Button(manager, width=2, image=datmanimg, command=switchToDatMan)

optionbutton = ttk.Button(manager, width=2, image=optionimg, command=switchOptions)
optionbutton.grid(column=1, row=1, sticky=(N, W))

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
playlistbutton.grid(column=1, row=1, sticky=(N))

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
#{C13} Display Keyboard
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
#{C14} Scanfunktion (Zu scannendes Verzeichnis, Treeview zum eintragen)
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

scanPath(path_main, manlist)         #mp3liste wird erstellt
scanPath(path_pl, pl_ls_list)   #Playlist Liste wird erstellt
scanPath(path_usb, USBlist)     #USBliste wird erstellt

#for child in mainframe.winfo_children(): child.grid_configure(padx=2, pady=2)
optioncanvas.grid_forget()
keyboardcanvas.grid_forget()

root.mainloop()
