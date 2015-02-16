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
# @Title: Button.py
#
# @Author: Phil Smith
#
# @Date: Sat, 14-Feb-15 08:38PM
#
# @Project: Roku Remote
#
# @Purpose: Create Buttons that can be tied to other actions.
#
#
################################################################################
import pygtk
pygtk.require('2.0')
import gtk
from rokulib import keypress, launch


class RCButton( gtk.Button):
   """
   This class represents remote control buttons.
   """


   def __init__(self, label=None):
      """
      Initializes a button. Button position and size wll be set by
      rokulib.
      """

      # Call the Button init method so class is seen as GTK Widget.
      super(RCButton, self).__init__()
      self.label = label


   def register( self, string ):
      """
      Register the button to the appropriate callback.
      """

      string   = string.split()
      command  = string[0].lower()
      argument = " ".join( string[1:] )

      # Keypress commands should be in format 'keypress button'
      if command == "keypress":
         self.connect( "clicked", keypress( argument ))

      elif command == "launch":
         self.connect( "clicked", launch( argument ))

      else:
         error = '"%s" is not a valid command.' % command
         raise SyntaxError, error
