# roku_remote
A simple GTK application to control Roku streaming boxes. Written without using a builder.

Features:
 * Controls similar to standard Roku remote including D-PAD, play controls and menu controls.
 * User configurable Quick Launch controls to launch channels directly.
 * Keyboard entry pad to send keystrokes to the Roku like a civilized human (not supported by all channels - I'm glaring at you YouTube...)

**Main Window**
![Screenshot](Screenshot.png?raw=true "Roku Screenshot")

The main window is managed mostly by the App class in App.py. One design goal was to keep this 
window separated from the Roku-specific functions. To maintain some sort of modularity, App.py
imports functions from rokulib.py, but calls them within a wrapper function. There are a couple
of cases where there is no wrapper - just to make reading the code easier.
If no launchers are found in the launcher config file, the buttons will not be drawn at all.

**Device Selection Window**
![Device List](device_dialog.png?raw=true "Roku Screenshot")

The device selection window is implemented in rokulib.py. It is spawned by a call to rokulib.choose_device().
On start up, the application requests that all Roku boxes on the network identify themselves. The first
3 to respond are listed as selections.
When a Roku is selected, the information is saved to a config file and the main window updated to reflect
the new selection.

**Quick Launch Editor Window**
![Quick Launch](launcher_dialog.png?raw=true "Roku Screenshot")

The quick launch editor lets users change the channels associated with the quick launch buttons. The
dialog is spawned by a call to rokulib.choose_launchers(). Data entered on this page is also saved
to a config file (different than the device file).
