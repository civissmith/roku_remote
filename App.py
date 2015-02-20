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
import sys
import yaml
import signal as sig
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

class App( object ):
   """
   Represents the main application. The run() method invokes the GTK main loop.
   """


   def __init__(self):
      """
      Initialize the program state.
      """
      # Initialize threads.
      gtk.gdk.threads_init()

      self.config_path = op.join(op.expanduser('~'), '.roku_remote')
      self.launcher_file = op.join(self.config_path, 'launchers.yml')
      self.device_file = op.join(self.config_path, 'default_device.yml')
      self.icon_file = op.join(self.config_path, 'icons', 'roku.png')

      self.config_files = {
         'device': self.device_file,
         'launcher': self.launcher_file,
      }

      # Set the default main window size.
      self.main_window = gtk.Window( gtk.WINDOW_TOPLEVEL )
      self.main_window.set_title ( __appname__ )


      # Tie to the control-specific variables.
      self.fill_libvars()

      # Set the starting dimensions.
      self.main_window.set_size_request( 585, 330 )

      # Inihibit resizing. size is set by the gtk.Fixed() size request.
      self.main_window.set_resizable( False )

      # Create the buttons to be added.
      self.create_buttons()

      # Create/pack the display pane.
      self.pane = gtk.Fixed()
      self.main_window.add(self.pane)

      self.create_menu()

      # Lay the labels out.
      self.layout_labels()

      # Lay the text box out.
      self.layout_text_box()

      # Lay the buttons out.
      self.layout_buttons()

      # Register the delete event so the main window can close.
      self.main_window.connect( "delete_event", self.terminate )
      self.main_window.connect( "destroy", self.terminate )

      # Show the main window.
      self.pane.show()
      self.main_window.show()


   def terminate(self, widget, event=None, data=None):
      """
      Lets the main window close. Callback for the 'delete_event' and 'destroy'.
      """
      gtk.main_quit()
      return False


   def run(self):
      """
      Setup the run state and start the GTK loop.
      """

      # Run the gtk main loop.
      gtk.main()

   def get_main_menu(self, window):
      accel_group = gtk.AccelGroup()

      # This function initializes the item factory.
      # Param 1: The type of menu - can be MenuBar, Menu,
      #          or OptionMenu.
      # Param 2: The path of the menu.
      # Param 3: A reference to an AccelGroup. The item factory sets up
      #          the accelerator table while generating menus.
      item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)

      # This method generates the menu items. Pass to the item factory
      #  the list of menu items
      item_factory.create_items(self.menu_items)

      # Attach the new accelerator group to the window.
      window.add_accel_group(accel_group)

      # need to keep a reference to item_factory to prevent its destruction
      self.item_factory = item_factory
      # Finally, return the actual menu bar created by the item factory.
      return item_factory.get_widget("<main>")


   def create_menu(self):
      """
      Create the 'File' menu for the application.
      """

      self.menu_items = (
          ( "/File/Find _Devices", "<control>D", self.menu_d_action, 0, None ),
          ( "/File/_Launchers"   , "<control>L", self.menu_l_action, 0, None ),
          ( "/File/Quit"    , "<control>Q", gtk.main_quit, 0, None ),
      )

      self.menu = self.get_main_menu( self.main_window )
      self.menu.show()
      self.pane.put(self.menu, 0 , 0)

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
         "launcher_0" : button_12,
         "launcher_1" : button_13,
         "launcher_2" : button_14,
      }


      for each in self.buttons:
         # Treat launchers differently
         if each in [ "launcher_0", "launcher_1", "launcher_2" ]:
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
      self.pane.put(self.text_box, 10, 40)


   def layout_labels(self):
      """
      Adds labels to the blocks of controls.
      """

      menu = gtk.Label("Menu Controls")
      dpad = gtk.Label("Cursor Controls")
      play = gtk.Label("Playback Controls")
      entry = gtk.Label("Keyboard Entry:")
      launch = gtk.Label("Quick Launch Controls")

      self.pane.put( menu,   5, 100 )
      self.pane.put( dpad, 400, 100 )
      self.pane.put( play, 400, 260 )
      self.pane.put( entry,  5,  25 )
      self.pane.put( launch, 5, 245 )

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

      if not op.isdir(self.config_path):

         # Without the directory, files can't exist.
         roku_address = ""
         roku_name    = "NONE SELECTED"
         rokulib.launchers = {}

      else:

         # Read the launcher configuration and device configuration files.
         launchers = None
         if op.isfile(self.launcher_file):
            lnch_file = open( self.launcher_file )
            yaml_gen = yaml.load_all( lnch_file )
            for single in yaml_gen:
               launchers = single
            lnch_file.close()

            if launchers == None:
               rokulib.launchers = {}

            rokulib.launchers = launchers
                                       
         else:
            rokulib.launchers = {}

         if op.isfile(self.device_file):

            dev_file    = open( self.device_file, 'r' )
            device_info = list( yaml.load_all( dev_file )) 
            dev_file.close()

            if len(device_info) == 2:
                roku_address = device_info[0]
                roku_name    = device_info[1]
            else:
                roku_address = ""
                roku_name    = "NONE SELECTED"
         else:
            roku_address = ""
            roku_name    = "NONE SELECTED"

         if op.isfile(self.icon_file):
            self.main_window.set_icon_from_file( self.icon_file )


      # Set the roku_addr for the registration function.
      rokulib.roku_addr = roku_address
      old_title = self.main_window.get_title()
      self.main_window.set_title( old_title + ': %s' % roku_name )
      if roku_address:
         rokulib.channels = rokulib.get_channels()


   def menu_d_action( self, action, widget ):
      """
      Calls the appropriate function because user selected 'D' option from 'File' menu.
      """
      rokulib.choose_device( self.main_window, self.config_files )

   def menu_l_action( self, action, widget ):
      """
      Calls the appropriate function because user selected 'L' option from 'File' menu.
      """
      rokulib.choose_launchers( self.main_window, self.config_files )

def ctrl_c( context, signo ):
   if sys.stdout:
      sys.stdout.write("\b\b")
      sys.stdout.write( "Quitting...\n")
   gtk.main_quit()

if __name__ == "__main__":
   sig.signal( sig.SIGINT, ctrl_c )
   prog = App()
   prog.run()
