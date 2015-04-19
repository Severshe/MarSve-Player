#!/usr/bin/env python
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

'''Audio and video player with simple GUI controls.
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

#Was fuer Pakete brauchen wir
from pyglet.gl import *         #Grafikpaket
import pyglet
from pyglet.window import key   #Keyboard und Maus Unterstuetzung
import math

#Funktion zum zeichnen von Rechtecken
def draw_rect(x, y, width, height):
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

# Klasse von Controllfunktionen
class Control(pyglet.event.EventDispatcher):
    x = y = 0
    width = height = 10

    def __init__(self, parent):
        super(Control, self).__init__()
        self.parent = parent

#Wird ein Knopf getroffen
    def hit_test(self, x, y):
        return (self.x < x < self.x + self.width and  
                self.y < y < self.y + self.height)

#Playback pausieren
    def capture_events(self):
        self.parent.push_handlers(self)
#Playback weiterlaufen lassen
    def release_events(self):
        self.parent.remove_handlers(self)

#Klasse zum erstellen von Knoepfen
class Button(Control):
    charged = False

    def draw(self):
        if self.charged:
            glColor3f(1, 0, 0)
        draw_rect(self.x, self.y, self.width, self.height)
        glColor3f(1, 1, 1)
        self.draw_label()

    def on_mouse_press(self, x, y, button, modifiers):
        self.capture_events()
        self.charged = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.charged = self.hit_test(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.release_events()
        if self.hit_test(x, y):
            self.dispatch_event('on_press')
        self.charged = False

Button.register_event_type('on_press')
    
#Wie werden die Knoepfe beschrieben
class TextButton(Button):
    def __init__(self, *args, **kwargs):
        super(TextButton, self).__init__(*args, **kwargs)
        self._text = pyglet.text.Label('', anchor_x='center', anchor_y='center')

    def draw_label(self):
        self._text.x = self.x + self.width / 2
        self._text.y = self.y + self.height / 2
        self._text.draw()

    def set_text(self, text):
        self._text.text = text

    text = property(lambda self: self._text.text,
                    set_text)

class Slider(Control):
    THUMB_WIDTH = 6
    THUMB_HEIGHT = 10
    GROOVE_HEIGHT = 2

    def draw(self):
        center_y = self.y + self.height / 2
        draw_rect(self.x, center_y - self.GROOVE_HEIGHT / 2, 
                  self.width , self.GROOVE_HEIGHT)
        pos = self.x + self.value * self.width / (self.max - self.min)
        draw_rect(pos - self.THUMB_WIDTH / 2, center_y - self.THUMB_HEIGHT / 2, 
                  self.THUMB_WIDTH, self.THUMB_HEIGHT)
        
# Umrechung Tracklaenge Sliderlaenge
    def coordinate_to_value(self, x):
        return float(x - self.x) / self.width * (self.max - self.min) + self.min

    def on_mouse_press(self, x, y, button, modifiers):
        value = self.coordinate_to_value(x)
        self.capture_events()
        self.dispatch_event('on_begin_scroll')
        self.dispatch_event('on_change', value)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        value = min(max(self.coordinate_to_value(x), self.min), self.max)
        self.dispatch_event('on_change', value)
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.release_events()
        self.dispatch_event('on_end_scroll')

Slider.register_event_type('on_begin_scroll')
Slider.register_event_type('on_end_scroll')
Slider.register_event_type('on_change')


class PlayerWindow(pyglet.window.Window):
    GUI_WIDTH = 480
    GUI_HEIGHT = 320
    GUI_PADDING = 4         #Rand
    GUI_BUTTON_HEIGHT = 16

    def __init__(self, player):
# 480x320 ist Fullscreen beim PiTFT
        super(PlayerWindow, self).__init__(style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS,
                                           visible=False, 
                                           resizable=False)
        self.player = player
        self.player.push_handlers(self)
        self.player.eos_action = self.player.EOS_PAUSE
# Erstellen der Controll Buttons
# Sliders
        self.slider = Slider(self)
        self.slider.x = self.GUI_PADDING
        self.slider.y = self.GUI_PADDING * 2 + self.GUI_BUTTON_HEIGHT
        self.slider.on_begin_scroll = lambda: player.pause()
        self.slider.on_end_scroll = lambda: player.play()
        self.slider.on_change = lambda value: player.seek(value)
# Play Pause Button
        self.play_pause_button = TextButton(self)
        self.play_pause_button.x = self.GUI_PADDING
        self.play_pause_button.y = self.GUI_PADDING
        self.play_pause_button.height = self.GUI_BUTTON_HEIGHT
        self.play_pause_button.width = 90
        self.play_pause_button.on_press = self.on_play_pause
# Next Burtton
        self.next_button = TextButton(self)
        self.next_button.x = self.play_pause_button.x + \
                               self.play_pause_button.width + self.GUI_PADDING
        self.next_button.y = self.GUI_PADDING
        self.next_button.height = self.GUI_BUTTON_HEIGHT
        self.next_button.width = 90
        self.next_button.text = 'Next'
        self.next_button.on_press = self.on_play_next
        


        self.controls = [
            self.slider, 
            self.play_pause_button,
            self.next_button,
        ]


    def on_eos(self):
        self.gui_update_state()
        self.gui_update_source()

    def gui_update_source(self):
        if self.player.source:
            source = self.player.source
            self.slider.min = 0.
            self.slider.max = source.duration
        self.gui_update_state()

    def gui_update_state(self):
        if self.player.playing:
            tracklength = math.ceil(player.source.duration)
            tracksec = math.fmod (tracklength, 60)
            trackmin = (tracklength-tracksec)/60
            
            playlength = math.ceil(player.time)
            playsec = math.fmod (playlength, 60)
            playmin = (playlength-playsec)/60
            
            self.play_pause_button.text = '%i:%.2i/%i:%.2i' %(playmin, playsec, trackmin, tracksec)
        else:

            self.play_pause_button.text = 'Play'

    def on_resize(self, width, height):
        '''Position and size video image.'''
        super(PlayerWindow, self).on_resize(width, height)

        self.slider.width = width - self.GUI_PADDING * 2

        height -= self.GUI_HEIGHT
        self.video_height = 480
        self.video_width = 320
        self.video_x = (width - self.video_width) / 2
        self.video_y = (height - self.video_height) / 2 + self.GUI_HEIGHT

    def on_mouse_press(self, x, y, button, modifiers):
        for control in self.controls:
            if control.hit_test(x, y):
                control.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.on_play_pause()
        elif symbol == key.ESCAPE:
            self.dispatch_event('on_close')

    def on_close(self):
        self.player.pause()
        self.close()

    def on_play_pause(self):
        if self.player.playing:
            self.player.pause()
        else:
            if self.player.time >= self.player.source.duration:
                self.player.seek(0)
            self.player.play()
        self.gui_update_state()
        
    def on_play_next(self):
        self.player.next()
        self.player.play()
        self.gui_update_state()
        
    def on_draw(self):
        self.clear()
        

        # GUI
        self.slider.value = self.player.time
        for control in self.controls:
            control.draw()

#Updatefunktion fuer den Slider
    def update(self, dt):
        self.clear()
#Berechnung der Laenge in Minuten und Sekunden (funktioniert)
        if self.player.playing:
            tracklength = math.ceil(player.source.duration)
            tracksec = math.fmod (tracklength, 60)
            trackmin = (tracklength-tracksec)/60
            
            playlength = math.ceil(player.time)
            playsec = math.fmod (playlength, 60)
            playmin = (playlength-playsec)/60
            self.play_pause_button.text = '%i:%.2i/%i:%.2i' %(playmin, playsec, trackmin, tracksec)
        else:
            self.play_pause_button.text = 'Play'

        self.slider.value = self.player.time
        for control in self.controls:
            control.draw()
          

player = pyglet.media.Player()
window = PlayerWindow(player)

#Bis jetzt integrierte Musik
############################################################
source = pyglet.media.load('mp3/09 - Farin Urlaub - Schon Wieder.mp3')
player.queue(source)

source = pyglet.media.load('mp3/01 - Foo Fighters - All my Life.mp3')
player.queue(source)
############################################################

window.gui_update_source()
window.set_visible(True)

window.gui_update_state()
player.play()

window.gui_update_state()
window.width = 480
window.height = 320
window.set_size(480, 320)

def update(dt):
    window.update(dt)

#Updateintervall fuer den Slider in Sekunden
pyglet.clock.schedule_interval(update, 1/10.)

pyglet.app.run()
