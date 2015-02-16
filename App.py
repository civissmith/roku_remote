#!/usr/bin/python -B
################################################################################
# Copyright (c) 2015 Phil Smith
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
################################################################################
################################################################################
# @Title: App.py
#
# @Author: Phil Smith
#
# @Date: Sat, 14-Feb-15 08:38PM
#
# @Project: Roku Remote
#
# @Purpose: Main application for the Roku Remote app.
#
#
################################################################################
import pygtk
pygtk.require('2.0')
import gtk
import os
import yaml
import os.path as op
from Button import RCButton

# Import the application specific library.
import rokulib

# Import the layout function for the specific application.
from rokulib import send_text
from rokulib import send_backspace
from rokulib import layout_remote_buttons

__appname__ = "Roku Remote"
__author__  = "Phil Smith"
__version__ = "0.99"

class App( object ):
   """
   Represents the main application. The run() method invokes the GTK main loop.
   """


   def __init__(self):
      """
      Initialize the program state.
      """

      self.config_path = op.join(op.expanduser('~'), '.roku_remote')
      self.launcher_file = op.join(self.config_path, 'launchers.yml')
      self.device_file = op.join(self.config_path, 'default_device.yml')
      self.icon_file = op.join(self.config_path, 'icons', 'roku.png')


      # Set the default window size.
      self.window = gtk.Window( gtk.WINDOW_TOPLEVEL )
      self.window.set_title ( __appname__ )

      # Tie to the control-specific variables.
      self.fill_libvars()

      # Set the starting dimensions.
      self.window.set_size_request( 615, 330 )
      self.window.set_border_width( 5 )

      # Inihibit resizing. size is set by the gtk.Fixed() size request.
      self.window.set_resizable( False )

      # Create the buttons to be added.
      self.create_buttons()

      # Create/pack the display pane.
      self.pane = gtk.Fixed()
      self.window.add(self.pane)

      # Lay the labels out.
      self.layout_labels()

      # Lay the text box out.
      self.layout_text_box()

      # Lay the buttons out.
      self.layout_buttons()

      # Register the delete event so the window can close.
      self.window.connect( "delete_event", self.terminate )
      self.window.connect( "destroy", self.terminate )

      # Show the window.
      self.pane.show()
      self.window.show()


   def terminate(self, widget, event=None, data=None):
      """
      Lets the window close. Callback for the 'delete_event' and 'destroy'.
      """
      gtk.main_quit()
      return False


   def run(self):
      """
      Setup the run state and start the GTK loop.
      """

      # Run the gtk main loop.
      gtk.main()


   def create_buttons(self):
      """
      Create the remote control buttons.
      """
      button_01 = None
      button_02 = None
      button_03 = None
      button_04 = None
      button_05 = None
      button_06 = None
      button_07 = None
      button_08 = None
      button_09 = None
      button_10 = None
      button_11 = None
      button_12 = None
      button_13 = None
      button_14 = None

      self.buttons = {
         "Back"       : button_01,
         "Home"       : button_02,
         "Select"     : button_03,
         "Up"         : button_04,
         "Left"       : button_05,
         "Down"       : button_06,
         "Right"      : button_07,
         "Rev"        : button_08,
         "Play"       : button_09,
         "Fwd"        : button_10,
         "Search"     : button_11,
         "launcher_1" : button_12,
         "launcher_2" : button_13,
         "launcher_3" : button_14,
      }


      for each in self.buttons:
         # Treat launchers differently
         if each in [ "launcher_1", "launcher_2", "launcher_3" ]:
             self.buttons[each] = RCButton( each )
             self.buttons[each].set_size_request(75, 35)
             continue
         self.buttons[each] = RCButton( each )
         self.buttons[each].register("keypress %s" % each)
         self.buttons[each].set_size_request(75, 35)


   def layout_text_box(self):
      """
      Adds the text box to the layout.
      """

      self.text_box = gtk.Entry(max=256)
      self.text_box.connect("activate", send_text )
      self.text_box.connect("backspace", send_backspace )
      self.text_box.show()
      self.text_box.set_size_request(520, 30)
      self.pane.put(self.text_box, 10, 20)


   def layout_labels(self):
      """
      Adds labels to the blocks of controls.
      """

      menu = gtk.Label("Menu Controls")
      dpad = gtk.Label("Cursor Controls")
      play = gtk.Label("Playback Controls")
      entry = gtk.Label("Keyboard Entry:")
      launch = gtk.Label("Quick Launch Controls")

      self.pane.put( menu,   5,  80 )
      self.pane.put( dpad, 400,  80 )
      self.pane.put( play, 400, 240 )
      self.pane.put( entry,  0,   5 )
      self.pane.put( launch, 5, 225 )

      menu.show()
      dpad.show()
      play.show()
      entry.show()
      launch.show()


   def layout_buttons(self):
      """
      Organizes buttons on the display area.
      """
      # Call the layout function from specific library
      layout_remote_buttons( self.buttons )

      for each in self.buttons:
         this_button = self.buttons[each]

         try:
            self.pane.put(this_button, this_button.x_pos, this_button.y_pos)
            this_button.show()
         except AttributeError:
            # If launchers are not defined, they will give attribute errors.
            pass

   def fill_libvars(self):
      # Changing the names in the launcher dict will change the channel
      # Bound to the launcher.

      # These vars determine where to look for launcher disp name (_label)
      # and channel name ( _name )
      _name  = 1
      _label = 0
      if not op.isdir(self.config_path):

         # Without the directory, files can't exist.
         roku_address = ""
         roku_name    = "NONE SELECTED"
         rokulib.launchers = {}

      else:

         # Read the launcher configuration and device configuration files.
         if op.isfile(self.launcher_file):
            lnch_file = open( self.launcher_file )
            launchers = list( yaml.load_all( lnch_file ))
            lnch_file.close()

            launch_1 = launchers[0]
            launch_2 = launchers[1]
            launch_3 = launchers[2]
            rokulib.launchers = {
               1: rokulib.Launcher(disp_name=launch_1[_label], 
                                   chan_name=launch_1[_name]),
 
               2: rokulib.Launcher(disp_name=launch_2[_label], 
                                   chan_name=launch_2[_name]),
 
               3: rokulib.Launcher(disp_name=launch_3[_label], 
                                   chan_name=launch_3[_name]),
            }
         else:
            rokulib.launchers = {}

         if op.isfile(self.device_file):

            dev_file    = open( self.device_file, 'r' )
            device_info = list( yaml.load_all( dev_file )) 
            dev_file.close()

            roku_address = device_info[0]
            roku_name    = device_info[1]
         else:
            roku_address = ""
            roku_name    = "NONE SELECTED"

         if op.isfile(self.icon_file):
            self.window.set_icon_from_file( self.icon_file )


      # Set the roku_addr for the registration function.
      rokulib.roku_addr = roku_address
      old_title = self.window.get_title()
      self.window.set_title( old_title + ': %s' % roku_name )
      if roku_address:
         rokulib.channels = rokulib.get_channels()


if __name__ == "__main__":
   prog = App()
   prog.run()
