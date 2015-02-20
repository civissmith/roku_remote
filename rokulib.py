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
# @Purpose: Library of function/objects to interact with the Roku. Used
#           to make the generic functions of the remote control app
#           work specifically with Roku.
#
################################################################################
import pygtk
pygtk.require('2.0')
import gtk
import re
import sys
import time
import yaml
import fcntl
import socket
import struct
import requests
import threading

MAX_ROKUS = 3
selected_roku = None
class Roku(object):
   """
   Class to contain data for the Rokus on the network.
   """

   DIAL_URN = 'dial/dd.xml'


   def __init__(self, url):
       self.url = url


   def __str__(self):
       return "%s" % self.url


   def __repr__(self):


       if self.friendly_name:
           return "%s (%s)" % (self.friendly_name, self.url)
       if self.model_name:
           return "%s (%s)" % (self.model_name, self.url)
       return "%s" % self.url


   def get_dial_data(self):
       """
       Parses the DIAL config file from the Roku to find parameters of interest.
       """
       code = requests.get( self.url + self.DIAL_URN )

       name_map = {
           '3100X' : 'Roku 2 XS',
           '4200X' : 'Roku 3',
       }

       # Items of interest:
       # <friendlyName>
       # <modelName>
       # <modelNumber>
       # <serialNumber>
       for line in code.iter_lines():
           name_match    = re.search( '<friendlyName>(.*)</friendlyName>', line )
           mod_match     = re.search( '<modelNumber>(.*)</modelNumber>'  , line )
           mod_num_match = re.search( '<modelName>(.*)</modelName>'      , line )
           ser_num_match = re.search( '<serialNumber>(.*)</serialNumber>', line )

           if name_match:
               self.friendly_name = name_match.group(1)
               continue

           if mod_match:
               self.model_name = mod_match.group(1)
               if self.model_name in name_map:
                   self.model_name = name_map[self.model_name]
               continue

           if mod_num_match:
               self.model_number = mod_num_match.group(1)
               continue

           if ser_num_match:
               self.serial_number = ser_num_match.group(1)
               continue


class Launcher(object):
   """
   Class to contain data for the channel launcher buttons.
   """


   def __init__(self, disp_name, chan_name=None):
       if not chan_name:
           self.disp_name = disp_name
           self.chan_name = disp_name
           return
       self.disp_name  = disp_name
       self.chan_name  = chan_name
       self.button_ref = None


def keypress( button ):
   """
   Returns a callback that will press the specifed button.
   """

   # These are keys recognized by the Roku ECP.
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
   """
   Queries the channels installed on the targeted Roku.
   """

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
           # Ensure that the button text will change even if there is no stderr.
           button = rcbutton.set_label("ERROR!")
           if sys.stderr:
               sys.stderr.write( '"%s" is not a valid channel!\n' % channel )
               sys.stderr.write( 'Please update your saved channel configuration.\n\n')
               sys.stderr.write( 'Valid channels:\n' )
               for chan in channels:
                   sys.stderr.write( ' - "%s"\n' % chan )
           return

   # Return the callback
   return callback_function


def layout_remote_buttons( buttons ):
   """
   Positions buttons in a fixed location.
   """

   global launchers

   # Launchers may not be defined for some reason like the config
   # file was missing.
   if not launchers:
       launchers = { 0: Launcher("Empty"), 1: Launcher("Empty"),
                     2: Launcher("Empty") }

       for each in launchers:
           launchers[each].button_ref = None


   def add_image( button, image ):
       """
       Local function to manage adding icons to buttons.
       """
       im = gtk.Image()
       im.set_from_stock( image , gtk.ICON_SIZE_BUTTON )
       im.show()
       button.add(im)

   # Setup the position for the D-pad
   d_pad_row = 170
   d_pad_col = 410
   d_pad_row_off = 50
   d_pad_col_off = 70

   # Setup the position for the play control bar
   play_ctrl_row = 280
   play_ctrl_col = 410
   play_ctrl_off =  90

   # Setup the position for the utilities and launchers
   utl_lnch_row = 190
   utl_lnch_col = 100
   utl_lnch_row_off = 70
   utl_lnch_col_off = 100

   launch_count = 0
   launch_bias  = -1

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
       if "launcher" in this_button.label:

           this_button.x_pos = utl_lnch_col + (utl_lnch_col_off * launch_bias)
           this_button.y_pos = utl_lnch_row + utl_lnch_row_off

           this_button.set_label( launchers[launch_count].disp_name )
           this_button.register("launch %s" % launchers[launch_count].chan_name )
           launchers[launch_count].button_ref = this_button
           launch_count += 1
           launch_bias  += 1
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

   # Clear the text box.
   text_box.set_text("")


def send_backspace( text_box ):
   """
   Handles sending a backspace command to the Roku because GTK treats <bs>
   differently for a reason... I'm sure.
   """

   requests.post( roku_addr + "/keypress/Backspace" )


def choose_device( main_window, config_files ):
   """
   Discover Rokus on the network and displays a dialog box to select from.
   """
   global selected_roku

   # Create the device discovery window.
   dev_window = gtk.Dialog( title= "Find Devices", parent=main_window   )

   # Create a pane to contain widgets.
   pane = gtk.Fixed()
   save = gtk.Button(label="Save" )
   save.set_size_request( 75,35 )

   # Tie the save buttons to their callbacks.
   save_args = (update_vars, config_files['device'], dev_window, main_window)
   save.connect( 'clicked', save_dev_selection, save_args )

   # Request a size and inhibit resizing.
   dev_window.set_size_request( 400, 150 )
   dev_window.set_resizable( False )


   # Create the label to show the search/select text.
   label = gtk.Label("Please Select a device:")
   pane.put(label ,  10, 10 )
   pane.put(save  , 305, 80 )

   # Dialog boxes default with a VBox and HBox.
   dev_window.vbox.pack_start(pane)

   # Show the widgets.
   dev_window.show_now()
   save.show()
   pane.show_now()
   label.show_now()


   # Get a list of the Roku devices on the network.
   rokus = []
   find_complete = threading.Event()

   # Guess which Ethernet interface to use.
   eth_if = detect_ethernet()

   # No interface could be found. Stop.
   if eth_if == 'NO_IF':
       label.set_text( "No Network Interface Found!")
       save.hide()
       return

   find_thread = threading.Thread(target=find_rokus, args=(eth_if, rokus, find_complete ))
   find_thread.start()

   # Wait for the find thread to report completion.
   find_complete.wait()
   x_pos = 10
   y_pos = 25
   y_off = 20

   # Setup radio button selection for device list.
   if len( rokus ) == 0:
       label.set_text( "No Devices Found!")
       return

   if len( rokus ) == 1:
       label.set_text( "Selected Device: " )
       dev = gtk.RadioButton(group=None, label="%s (%s)" % ( rokus[0].model_name ,
                                                             rokus[0].friendly_name ))
       dev.set_active(True)
       dev.show()
       pane.put( dev, x_pos, y_pos )
       selected_roku = rokus[0]
       return


   # More than 1 Roku was found, there needs to be list.
   for ind in range(0, len(rokus)):
       # First device sets up the button group.
       if ind == 0:
           dev = gtk.RadioButton(group=None, label="%s (%s)" % ( rokus[ind].model_name,
                                                                 rokus[ind].friendly_name ))
           dev.set_active(True)
           leader = dev
           selected_roku = rokus[ind]
       else:
           dev = gtk.RadioButton(group=leader, label="%s (%s)" % ( rokus[ind].model_name,
                                                                   rokus[ind].friendly_name ))

       # Register the callback function that selects the Roku.
       dev.connect('toggled', rb_toggled, (rokus[ind],))
       pane.put( dev, x_pos, y_pos )
       dev.show()
       y_pos += y_off


def update_vars():
   """
   This function is used to refresh environment data. Symbols bound during
   signal connection may be stale when the callback is invoked at run time.
   """
   global roku_addr
   global selected_roku

   # Refresh the Roku Address
   roku_addr = selected_roku.url


def save_dev_selection( widget, data ):
   """
   Writes the selected Roku to the config file.
   """

   global selected_roku

   # Unpack the arguments.
   update_vars   = data[0]
   dev_file_name = data[1]
   dev_window    = data[2]
   main_window   = data[3]

   # Update the environment.
   update_vars()

   # Attempt to re-write the default device file.
   try:
       dev_file = open(dev_file_name, 'w')
   except:
       sys.stderr.write("Could not open %s for reading!" % dev_file_name)
       return

   # Write the configuration data to disk.
   data = [selected_roku.url, selected_roku.model_name]
   yaml.dump_all( data, dev_file )
   dev_file.close()

   # Set the main window's title to match the chosen device.
   main_window.set_title( "Roku Remote: %s" % selected_roku.model_name )
   dev_window.destroy()


def rb_toggled(widget, data):
   """
   Handles selecting the chosen Roku when its radio button is clicked.
   """
   global selected_roku

   # Update the selected Roku to the activated item.
   if widget.get_active():
       selected_roku = data[0]


def find_rokus( net, devices=[], event=None ):
   """
   Send out an SSDP packet requesting Rokus to identify themselves.
   """

   # Set the Multicast address and port for UPnP
   MULTICAST_ADDR = '239.255.255.250'
   MULTICAST_PORT = 1900

   # Timout in seconds.
   TIMEOUT = 2.5

   # DISCOVER will look for all Roku ECP devices.
   DISCOVER =  'M-SEARCH * HTTP/1.1\r\n' +\
               'HOST:%s:%s\r\n' % (MULTICAST_ADDR, MULTICAST_PORT) +\
               'ST:roku:ecp\r\n'         +\
               'MX:2\r\n'                +\
               'MAN:"ssdp:discover"\r\n'

   # Set socket timer to TIMEOUT seconds, any blocking operation on sockets will
   # abort if TIMEOUT seconds elapse.
   socket.setdefaulttimeout(TIMEOUT)

   # Get the IP address of the active interface. The null_socket is never bound
   # or used, other than to get the address.
   null_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   loc_addr =  socket.inet_ntoa(fcntl.ioctl(null_socket.fileno(), 0x8915, struct.pack('256s', net[:15]))[20:24])

   # Setup and send the MULTICAST request
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

   # Manually change the multicast interface to the chosen one.
   sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, 
                   socket.inet_aton(loc_addr))

   sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   sock.bind((loc_addr, MULTICAST_PORT))

   # Ask politely to join the multicast group.
   multicast_request = struct.pack('4sl', socket.inet_aton(MULTICAST_ADDR), 
                                   socket.INADDR_ANY)

   sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, 
                   multicast_request)

   # Send the DISCOVER string to look for UPnP devices on the network.
   sock.sendto(DISCOVER, (MULTICAST_ADDR, MULTICAST_PORT))
   raw_devices = []
   found = 0

   while True:
       try:
           # Try to receive data from any UPnP devices on the network.
           raw_devices.append( sock.recv(1024) )
       except socket.timeout:
           # Break out when no more devices respond.
           break
       found += 1

   # Sometimes devices will respond multiple times. Build a final list of devices.
   for device in raw_devices:

       # Search through the device information looking for key data.
       location = re.search(r'location:\s*(.*)', device, re.IGNORECASE)
       usn = re.search(r'usn:\s*(.*)', device, re.IGNORECASE)
       st  = re.search(r'st:\s*(.*)', device, re.IGNORECASE)

       if location and usn and st:
           device_data = ()
           device_data = (location.group(1).strip('\r\n'),
                          usn.group(1).strip('\r\n'),
                          st.group(1).strip('\r\n'))

       if (device_data not in devices) and len(devices) < MAX_ROKUS:
           roku = Roku(device_data[0])
           roku.get_dial_data()
           devices.append(roku)

   # Set the event so the main thread knows to continue.
   event.set()


def choose_launchers( main_window, config_files ):
   """
   Discover Rokus on the network and displays a dialog box to select from.
   """
   global launchers

   launch_window = gtk.Dialog( title="Edit Launchers", parent=main_window )
   launch_window.show()

   # Create a pane to contain widgets.
   pane = gtk.Fixed()

   # Request a size and inhibit resizing.
   launch_window.set_size_request( 600, 300 )
   launch_window.set_resizable( False )

   # Create the label to show the search/select text.
   window_label   = gtk.Label("Edit Quick Launch Settings:")
   disp_col_label = gtk.Label("Display Name")
   chan_col_label = gtk.Label("Channel Name")
   save_button    = gtk.Button(label="Save")

   title_row = 35

   # Text box base
   col_1 =  10
   col_2 = 310
   textbox_row = title_row + 25
   y_offset = 50
   box_len  = 275
   box_wid  = 30

   pane.put(window_label   ,   10, 10 )
   pane.put(disp_col_label ,   10, title_row )
   pane.put(chan_col_label ,  310, title_row )
   pane.put(save_button, 515, 255 )

   # Dialog boxes default with a VBox and HBox.
   launch_window.vbox.pack_start(pane)

   # Load the text brothers.
   num_launchers = 3

   save_button.set_size_request( 75, 35 )
   text_boxes = []
   for cnt in range(0, num_launchers):
       disp = None
       chan = None
       # Create new text boxes
       disp = gtk.Entry(max=256)
       chan = gtk.Entry(max=256)

       disp.set_text( launchers[cnt].disp_name )
       if launchers[cnt].chan_name:
           chan.set_text( launchers[cnt].chan_name )
       chan.set_size_request( box_len, box_wid )
       disp.set_size_request( box_len, box_wid )

       pane.put( disp, col_1, textbox_row+y_offset*cnt)
       pane.put( chan, col_2, textbox_row+y_offset*cnt)
       text_boxes.append( [disp, chan ] )

       chan.show()
       disp.show()

   save_args = ( config_files['launcher'], text_boxes, launch_window )
   save_button.connect( "clicked", save_launch_file, save_args )

   # Show the widgets.
   launch_window.show()
   disp_col_label.show()
   chan_col_label.show()
   save_button.show()
   pane.show()
   window_label.show()


def save_launch_file( widget, data ):
   """
   Responds to the 'Save' button click event on the edit launcher page.
   """

   global launchers

   launch_file_name = data[0]
   text_boxes = data[1]
   window = data[2]

   # Grab the text in each box
   for count in range(0, len(text_boxes)):
       launchers[count].disp_name = text_boxes[count][0].get_text()
       launchers[count].chan_name = text_boxes[count][1].get_text()

       # Reset the display name and re-register the callback for the new channel.
       if launchers[count].button_ref:
           launchers[count].button_ref.set_label( launchers[count].disp_name )
           if launchers[count].button_ref.handler:
               launchers[count].button_ref.disconnect( launchers[count].button_ref.handler )
           launchers[count].button_ref.register("launch %s" % launchers[count].chan_name )

   try:
       launch_file = open(launch_file_name, 'w')
   except:
       sys.stderr.write("Could not open %s for reading!" % launch_file_name)
       return

   yaml.dump_all( [launchers,], launch_file )

   launch_file.close()
   window.destroy()


def detect_ethernet():
   """
   Uses /proc/net/dev to determine which Ethernet interface to use.
   """
   net_file = open('/proc/net/dev', 'r')

   # These are the first fields in rows we're not interested in.
   rejects = ['Inter-|', 'face', 'lo:']
   for line in net_file:

       data = line.split()
       if data[0] in rejects:
           continue

       # Chop the ':' from the device name.
       name = data[0][:-1]

       # Check for a interface that has transmitted.
       tx_bytes = int(data[9])

       if tx_bytes > 0:
           return name

   return 'NO_IF'
