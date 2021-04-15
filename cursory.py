#!/usr/bin/env python3

# Copyright (C) 2020 Konstantin Unruh <freaxmate@protonmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import gi

from gi.repository import GLib

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
from gi.repository import GdkPixbuf

gi.require_version('GdkX11', '3.0')
from gi.repository import GdkX11
from gi.repository import Gio
from gi.repository import GObject

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gi.repository import GdkPixbuf
import numpy

def array_from_pixbuf(p):
    " convert from GdkPixbuf to numpy array"
    w,h,c,r=(p.get_width(), p.get_height(), p.get_n_channels(), p.get_rowstride())
    assert p.get_colorspace() == GdkPixbuf.Colorspace.RGB
    assert p.get_bits_per_sample() == 8
    if  p.get_has_alpha():
        assert c == 4
    else:
        assert c == 3
    assert r >= w * c
    a=numpy.frombuffer(p.get_pixels(),dtype=numpy.uint8)
    if a.shape[0] == w*c*h:
        return a.reshape( (h, w, c) )
    else:
        b=numpy.zeros((h,w*c),'uint8')
        for j in range(h):
            b[j,:]=a[r*j:r*j+w*c]
        return b.reshape( (h, w, c) )


class Cursor:
    def get_brightness(self, window, x, y):
        offset = 8
        pixbuf = Gdk.pixbuf_get_from_window(window, x-offset, y-offset, 2*offset, 2*offset)
        pix_array = array_from_pixbuf(pixbuf)
        sum = 0
        for j in range(2*offset):
            for i in range(2*offset):
                #print("j: ", j, "i: ", i)
                sum += (int(pix_array[j][i][0])+int(pix_array[j][i][1])+int(pix_array[j][i][2]))**2
                #print ("sum: ", pix_array[j][i][0], "+", pix_array[j][i][1], "+", pix_array[j][i][2])
        brightness = sum**0.5
        #pixbuf.savev("pixbuf.png", "png", None, None)
        return brightness

    def cursor(self, window, pointer):
        (screen, x, y) = pointer.get_position()
        brightness = self.get_brightness(window, x, y)
        #print("x: ", x)
        #print("y: ", y)
        #print("brightness: ", brightness)
        settings = Gio.Settings.new("org.mate.peripherals-mouse")
        if brightness >= 3060:
            if settings.get_string("cursor-theme") != "xcursor-breeze":
                settings.set_string("cursor-theme", "xcursor-breeze")
        else:
            if settings.get_string("cursor-theme") != "xcursor-breeze-snow":
                settings.set_string("cursor-theme", "xcursor-breeze-snow")
        return True

    def __init__(self):
        window = Gdk.Screen.get_root_window(Gdk.Screen.get_default())

        display =  Gdk.Display.get_default()
        seat = Gdk.Display.get_default_seat(display)
        pointer = Gdk.Seat.get_pointer(seat)

        GLib.timeout_add(100, self.cursor, window, pointer)

if __name__=='__main__':
    cursor = Cursor()
    Gtk.main()
