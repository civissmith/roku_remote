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
# @Title: rokulib.py
#
# @Author: Phil Smith
#
# @Date: Sat, 14-Feb-15 08:38PM
#
# @Project: Roku Remote
#
# @Purpose: Tie the buttons to the Roku library.
#
################################################################################
import pygtk
pygtk.require('2.0')
import gtk
import re
import sys
import requests
import time

class Launcher(object):
   """
   Class to contain data for the channel launcher buttons.
   """


   def __init__(self, disp_name, chan_name=None):
      if not chan_name:
        self.disp_name = disp_name
        self.chan_name = disp_name
        return
      self.disp_name = disp_name
      self.chan_name = chan_name


def keypress( button ):
   """
   Returns a callback that will press the specifed button.
   """

   # Setup valid keys:
   keys = ["Home", "Rev", "Fwd", "Play", "Select", "Left", "Right",
           "Down", "Up", "Back", "Info", "Backspace", "Search", "Enter"]

   if button not in keys:
     error = "'%s' not in valid key press list." % button
     raise SyntaxError, error


   def callback_function( rcbutton ):
      """
      Calback function bound to the button to press.
      """
      requests.post( roku_addr + '/keypress/' + button )

   # Return the callback
   return callback_function


def get_channels():

   code = requests.get(roku_addr + "/query/apps")
   channels = {}
   for channel in code.iter_lines():
      app_id = re.search(r'<app id=("\d+?")', channel)
      name   = re.search(r'>([A-Za-z0-9\s\.\-]+?)</app>', channel)
      if app_id and name:
        channels[name.group(1)] = app_id.group(1)

   return channels


def launch( channel ):
   """
   Returns a callback that will launch the specified channel.
   """


   def callback_function( rcbutton ):
      """
      Callback function bound to the channel launcher.
      """
      try:
         code = requests.post(roku_addr + "/launch/" + channels[channel].strip('"'))
      except KeyError as err:
         sys.stderr.write( '"%s" is not a valid channel!\n' % channel )
         sys.stderr.write( 'Please update your saved channel configuration.\n\n')
         sys.stderr.write( 'Valid channels:\n' )
         button = rcbutton.set_label("ERROR!")
         for chan in channels:
            sys.stderr.write( ' - "%s"\n' % chan )
         return

   # Return the callback
   return callback_function


def layout_remote_buttons( buttons ):
   """
   Positions buttons in a fixed location.
   """


   def add_image( button, image ):
      im = gtk.Image()
      im.set_from_stock( image , gtk.ICON_SIZE_BUTTON )
      im.show()
      button.add(im)

   # Setup the position for the D-pad
   d_pad_row = 150
   d_pad_col = 410
   d_pad_row_off = 50
   d_pad_col_off = 70

   # Setup the position for the play control bar
   play_ctrl_row = 260
   play_ctrl_col = 410
   play_ctrl_off =  90

   # Setup the position for the utilities and launchers
   utl_lnch_row = 170
   utl_lnch_col = 100
   utl_lnch_row_off = 70
   utl_lnch_col_off = 100

   # Lay the pattern and adjust labels as needed.
   for each in buttons:
      this_button = buttons[each]

      # Utilities
      if this_button.label == "Back":
         this_button.x_pos = utl_lnch_col - utl_lnch_col_off
         this_button.y_pos = utl_lnch_row - utl_lnch_row_off
         add_image( this_button, gtk.STOCK_GO_BACK )
         continue

      if this_button.label == "Home":
         this_button.x_pos = utl_lnch_col
         this_button.y_pos = utl_lnch_row - utl_lnch_row_off
         add_image( this_button, gtk.STOCK_HOME )
         continue

      if this_button.label == "Select":
         this_button.x_pos = utl_lnch_col
         this_button.y_pos = utl_lnch_row
         this_button.set_label("Ok")
         continue

      if this_button.label == "Search":
         this_button.x_pos = utl_lnch_col + utl_lnch_col_off
         this_button.y_pos = utl_lnch_row - utl_lnch_row_off
         add_image( this_button, gtk.STOCK_FIND )
         continue
      # Launchers
      if launchers:
         if this_button.label == "launcher_1":
            this_button.x_pos = utl_lnch_col - utl_lnch_col_off
            this_button.y_pos = utl_lnch_row + utl_lnch_row_off
            this_button.set_label( launchers[1].disp_name )
            this_button.register("launch %s" % launchers[1].chan_name )
            continue
         if this_button.label == "launcher_2":
            this_button.x_pos = utl_lnch_col
            this_button.y_pos = utl_lnch_row + utl_lnch_row_off
            this_button.set_label( launchers[2].disp_name )
            this_button.register("launch %s" % launchers[2].chan_name )
            continue
         if this_button.label == "launcher_3":
            this_button.x_pos = utl_lnch_col + utl_lnch_col_off
            this_button.y_pos = utl_lnch_row + utl_lnch_row_off
            this_button.set_label( launchers[3].disp_name )
            this_button.register("launch %s" % launchers[3].chan_name )
            continue

      # D-Pad
      if this_button.label == "Up":
         this_button.x_pos = d_pad_col
         this_button.y_pos = d_pad_row - d_pad_row_off
         add_image( this_button, gtk.STOCK_GO_UP )
         continue
      if this_button.label == "Left":
         this_button.x_pos = d_pad_col - d_pad_col_off
         this_button.y_pos = d_pad_row
         add_image( this_button, gtk.STOCK_GO_BACK )
         continue
      if this_button.label == "Down":
         this_button.x_pos = d_pad_col
         this_button.y_pos = d_pad_row + d_pad_row_off
         add_image( this_button, gtk.STOCK_GO_DOWN )
         continue
      if this_button.label == "Right":
         this_button.x_pos = d_pad_col + d_pad_col_off
         this_button.y_pos = d_pad_row
         add_image( this_button, gtk.STOCK_GO_FORWARD )
         continue

      # Play Controls
      if this_button.label == "Rev":
         this_button.x_pos = play_ctrl_col - play_ctrl_off
         this_button.y_pos = play_ctrl_row
         add_image( this_button, gtk.STOCK_MEDIA_REWIND )
         continue
      if this_button.label == "Play":
         this_button.x_pos = play_ctrl_col
         this_button.y_pos = play_ctrl_row
         add_image( this_button, gtk.STOCK_MEDIA_PLAY )
         continue
      if this_button.label == "Fwd":
         this_button.x_pos = play_ctrl_col + play_ctrl_off
         this_button.y_pos = play_ctrl_row
         add_image( this_button, gtk.STOCK_MEDIA_FORWARD )
         continue


def send_text( text_box ):
   """
   Handle sending text from text box to the Roku. This function will not
   automatically send the selection because the Roku protocol is unreliable and
   may miss key presses (especially for long strings). Sending an empty string
   will force the selection.
   """
   text = text_box.get_text()
   if text == "":
      requests.post( roku_addr + "/keypress/Enter" )
      return

   for letter in text:
      if letter == ' ':
         letter = '%20'
      requests.post( roku_addr + "/keypress/Lit_" + letter )
      time.sleep(.3)
   text_box.set_text("")


def send_backspace( text_box ):
   """
   Handles sending a backspace command to the Roku because GTK treats <bs>
   differently for a reason... I'm sure.
   """
   requests.post( roku_addr + "/keypress/Backspace" )
