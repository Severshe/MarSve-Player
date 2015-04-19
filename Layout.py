import os
from os.path import join, getsize

from pytag import Audio
from tkinter import *
from tkinter import ttk

#path = "F:\\Downloads\MarSve-Player\mp3"
path = "/Users/Luftikus/Desktop/mp3"

root = Tk()
root.title("Mp3 Player MarSve")

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
# manlist["columns"]=("Artist","Song")
# manlist.column("Artist", width=50)
# manlist.column("Song", width=50)
# manlist.heading("Artist", text="Artist")
# manlist.heading("Song", text="Song")

manlistscroll = ttk.Scrollbar( manager, orient=VERTICAL, command=manlist.yview)
manlistscroll.grid(column=3, row=2, sticky=(N, E, S))
manlist.configure(yscrollcommand=manlistscroll.set)

songtext = ttk.Label(playframe, text="Artist - Song")
songtext.grid(column=1, row=1, columnspan=6, sticky=(N, W, E))

prevbutton = ttk.Button(playframe, text='Prev')
prevbutton.grid(column=1, row=2, sticky=(N, W, E, S))

playbutton = ttk.Button(playframe, text='Play')
playbutton.grid(column=2, row=2, sticky=(N, W, E, S))

nextbutton =ttk.Button(playframe, text='Next')
nextbutton.grid(column=3, row=2, sticky=(N, W, E, S))

progressbar =ttk.Progressbar(playframe, orient=HORIZONTAL, length=200, mode='determinate')
progressbar.grid(column=1, row=3, columnspan=3, sticky=(N, W, E, S))

playlist = Listbox(playframe)
playlist.grid(column=1, row=4, columnspan=3, sticky=(N, W, E, S))

manlistscroll = ttk.Scrollbar( playframe, orient=VERTICAL, command=playlist.yview)
manlistscroll.grid(column=3, row=4, sticky=(N, E, S))
playlist.configure(yscrollcommand=manlistscroll.set)

hinbutton = ttk.Button(playframe, text='Hinzufuegen')
hinbutton.grid(column=1, row=5, sticky=(W, S))

entbutton = ttk.Button(playframe, text='Entfernen')
entbutton.grid(column=3, row=5, sticky=(E, S))
#############################################################################
#Layout Elemente
#############################################################################

#############################################################################
#Dateimanager
#############################################################################
def scanPath(path):
    i = 0
    #for Schleife zum erstellen der Dateiliste "path" mit Listenstruktur (aktueller Pfad, unter Pfade, Dateien)
    for path in os.walk(path):
        j = 1
        #for Schleife zum Auslesen von unter Pfaden und Dateien
        for j in range(1, 3):
            #for Schleife zum Auslesen der eigentlichen Items
            k = 0
            for k in range(0,len(path[j])):
                if i==0:
                    manlist.insert("", 'end', os.path.join(path[0], path[j][k]), text=path[j][k])
                else:
                    manlist.insert(path[0], 'end', os.path.join(path[0], path[j][k]), text=path[j][k])
                k += 1
            j += 1
        i += 1
## Hier nochmal die Schleife die ich gefunden hatte:
#def scanPath(verz):
#    for name in os.listdir(verz):
#        pfad = os.path.join(verz, name)
#
#        if os.path.isfile(pfad):
#            manlist.insert("", 'end', name, text=name)
#        else:
#            scanPath(pfad)
#
scanPath(path)



#############################################################################
#Dateimanager
#############################################################################

for child in mainframe.winfo_children(): child.grid_configure(padx=2, pady=2)

root.mainloop()
