#!/bin/python3
import soco
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import zonesPage
from zonesPage import ZonesPage, Zones
from MusicPage import MusicPage
from MusicPlayingPage import MusicPlayingPage
from MusicAlbumArtPage import MusicAlbumArtPage
from QueuePage import QueuePage
from musicLibraryPage import MusicLibraryPage
from mediaListItemsPage import MediaListItemsPage
from mediaListArtistsPage import MediaListArtistsPage
from mediaListAlbumsPage import MediaListAlbumsPage
from systemSettingsPage import SystemSettingsPage
from Zone import Zone
from threading import Thread, Event
import time
from mediaListTracksPage import MediaListTracksPage
from zoneListener import ZoneListener
from I2C import I2CListener, CRi2c
import I2C
import imageManager

def moduleExists(module_name):
   try:
      __import__(module_name)
   except ImportError:
      return False
   else:
      return True

class PyApp(Gtk.Window):

   class zoneListener(ZoneListener):
      def __init__(self, owner):
         super().__init__(owner)

      def on_selected_zone_changed(self):
         for key, value in self.owner.zoneListeners.items():
            value.on_selected_zone_changed()

      def on_zone_transport_change_event(self, event):
         for key, value in self.owner.zoneListeners.items():
            value.on_zone_transport_change_event(event)

      def on_zone_render_change_event(self, event):
         for key, value in self.owner.zoneListeners.items():
            value.on_zone_render_change_event(event)

      def on_zone_queue_update_begin(self):
         for key, value in self.owner.zoneListeners.items():
            value.on_zone_queue_update_begin()

      def on_zone_queue_update_end(self):
         for key, value in self.owner.zoneListeners.items():
            value.on_zone_queue_update_end()
   
      def on_current_track_update_state(self, trackInfo):
         for key, value in self.owner.zoneListeners.items():
            value.on_current_track_update_state(trackInfo)

   class i2cListenerInterface(I2CListener):
      def __init__(self, owner):
         self.owner = owner

      def on_button_pressed_event(self, btn):
         pass

      def on_button_released_event(self, btn):
          print("BUTTON: ", btn)
          if btn == I2C.SWITCH_MUTE:
             self.owner.on_zoneMuteButton_Clicked(None)
          elif btn == I2C.SWITCH_VOL_UP:
             self.owner.on_zoneVolUpButton_Clicked(None)
          elif btn == I2C.SWITCH_VOL_DN:
             self.owner.on_zoneVolDownButton_Clicked(None)
          elif btn == I2C.SWITCH_A:
             self.owner.on_Button_A_Clicked(None)
          elif btn == I2C.SWITCH_B:
             self.owner.on_Button_B_Clicked(None)
          elif btn == I2C.SWITCH_C:
             self.owner.on_Button_C_Clicked(None)
          elif btn == I2C.SWITCH_ZONE:
             self.owner.on_Zones_Button_Clicked(None)
          elif btn == I2C.SWITCH_BACK:
             self.owner.on_Return_Button_Clicked(None)
          elif btn == I2C.SWITCH_MUSIC:
             self.owner.on_Music_Button_Clicked(None)
          elif btn == I2C.SWITCH_ENTER:
             self.owner.on_Button_Ok_Clicked(None)
          elif btn == I2C.SWITCH_REWIND:
             self.owner.on_Previous_Button_Clicked(None)
          elif btn == I2C.SWITCH_PLAY_PAUSE:
             self.owner.on_Play_Button_Clicked(None)
          elif btn == I2C.SWITCH_FORWARD:
             self.owner.on_Next_Button_Clicked(None)

      def on_scroll_event(self, steps):
         pass

      def on_battery_level_event(self):
         pass

      def on_charger_event(self):
         pass

      def on_system_event(self):
         pass

   def on_Zones_Button_Clicked(self, button):
      self.pageInView.on_zoneButton_Clicked()

   def on_Music_Button_Clicked(self, button):
      self.pageInView.on_musicButton_Clicked()

   def on_zoneMuteButton_Clicked(self, button):
      print("Mute")
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.mute(not zp.selectedZone.is_muted())

   def on_zoneVolUpButton_Clicked(self, button):
      print("Up")
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.volume('+')

   def on_zoneVolDownButton_Clicked(self, button):
      print("Down")
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.volume('-')

   def get_selected_zone(self):
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         return(zp.selectedZone)
      else:
         return(None)

   def get_page(self, page):
      return(self.pageDict[page])

   def show_page(self, page):

      if self.pageInView is self.pageDict["QueuePage"]:
         self.hide_queue_page()
      else:
         self.pageInView.hide()

      self.pageInView.on_Page_Exit_View()

      if isinstance(page, str) and page == "PastPage":
         page = self.pageDict["PastPage"]

      self.pageDict["PastPage"] = self.pageInView

      self.pageRevealer.remove(self.pageInView)

      if isinstance(page, str):
         self.pageInView = self.pageDict[page]
      else:
         self.pageInView = page

      self.pageRevealer.add(self.pageInView)
      self.pageInView.on_Page_Entered_View(self.pageDict["ZonesPage"].selectedZone)
      self.pageInView.show()

      # Consider moving this, it starts the event monitoring
      # thread on initial call
      if self.pageInView is self.pageDict["ZonesPage"]:
         print("on PAge Changed: ", zonesPage.Zones)
         if zonesPage.Zones is not None and len(zonesPage.Zones) > 0:
            if self.eventThread.is_alive() == False:
               print("Starting event thread.")
               self.eventThread.start()

   def on_Page_Changed(self, stack, gparamstring):
#       self.show_page(self.stack.get_visible_child())
      pass

   def on_Button_A_Clicked(self, button):
       self.pageInView.on_Button_A_Clicked()

   def on_Button_B_Clicked(self, button):
       self.pageInView.on_Button_B_Clicked()

   def on_Button_C_Clicked(self, button):
      self.pageInView.on_Button_C_Clicked()

   def on_Return_Button_Clicked(self, button):
      self.pageInView.on_Return_Button_Clicked()

   def on_Scroll_Up(self, button):
       self.pageInView.on_Scroll_Up()

   def on_Button_Ok_Clicked(self, button):
       self.pageInView.on_Button_Ok_Clicked()

   def on_Scroll_Down(self, button):
       self.pageInView.on_Scroll_Down()

   def on_Previous_Button_Clicked(self, button):
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.previous()
      else :
         print(zp.selectedZone)

   def on_Play_Button_Clicked(self, button):
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.play()
      else :
         print(zp.selectedZone)

   def on_Next_Button_Clicked(self, button):
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.next()
      else :
         print(zp.selectedZone)

   def eventThreadHandler(self):
      print("Running event thread handler: ", zonesPage.Zones)
      while self.RunEventThread:
         for zone in zonesPage.Zones:
            zone.update()
         if self.get_selected_zone() is not None:
            self.get_selected_zone().monitor()
         time.sleep(1.0)

   def hide_queue_page(self):
      self.queueRevealer.set_reveal_child(False)
      if self.pageDict["PastPage"] is not None:
         self.pageInView = self.pageDict["PastPage"]
      else:
         self.pageInView = self.pageDict["MusicPage"]

      self.queueRevealer.hide()
      self.pageRevealer.show()
#      self.pageInView.show()
   
   def show_queue_page(self):
      self.pageRevealer.hide()
      self.pageDict["PastPage"] = self.pageInView
      self.pageInView = self.pageDict["QueuePage"]
      self.pageInView.on_Page_Entered_View(self.pageDict["ZonesPage"].selectedZone)
      self.queueRevealer.show_all()
      self.queueRevealer.set_reveal_child(True)
#      self.pageInView.show()

   def add_zone_listener(self, id, listener):
      self.zoneListeners[id] = listener

   def remove_zone_listener(self, id):
      if id in self.zoneListeners:
         self.zoneListeners.pop(id)

   def on_destroy(self, widget):
      self.RunEventThread = False
      self.i2c.Close()
      time.sleep(1.0)
      Gtk.main_quit()

###############################################################################
###############################################################################
###############################################################################

   def __init__(self):
      super(PyApp, self).__init__()

      self.zoneListeners = {}

      imageManager.add_image("./images/AlbumArtEmpty.jpg", 'emptyArt')
      imageManager.add_image("./images/CrossFade.png", 'crossFade')
      imageManager.add_image("./images/Mute.png", 'mute')
      imageManager.add_image("./images/NoAlbumArt.jpg", 'noArt')
      imageManager.add_image("./images/Pause.png", 'pause')
      imageManager.add_image("./images/Play.png", 'play')
      imageManager.add_image("./images/Queue.png", 'queue')
      imageManager.add_image("./images/Repeat.png", 'repeat')
      imageManager.add_image("./images/separator.png", 'separator')
      imageManager.add_image("./images/Shuffle.png", 'shuffle')
      imageManager.add_image("./images/Stop.png", 'stop')
      imageManager.add_image("./images/Shrug.png", 'shrug')
      imageManager.add_image("./images/Transition.png", 'transition')

      self.pageDict = {
         "ZonesPage" : ZonesPage(self),
         "MusicPage" : MusicPage(self),
         "MusicPlayingPage" : MusicPlayingPage(self),
         "MusicAlbumArtPage" : MusicAlbumArtPage(self),
         "QueuePage" : QueuePage(self),
         "MusicLibraryPage" : MusicLibraryPage(self),
         "MediaListArtistsPage" : MediaListArtistsPage(self),
         "MediaListAlbumsPage" : MediaListAlbumsPage(self),
         "MediaListTracksPage" : MediaListTracksPage(self),
         "SystemSettingsPage" : SystemSettingsPage(self),
         "PastPage" : None
         }

      self.zlistener = self.zoneListener(self)
      self.i2cListener = self.i2cListenerInterface(self)
      self.i2c = CRi2c()
      self.i2c.setListener(self.__class__.__name__, self.i2cListener)

      self.pageInView = self.pageDict["ZonesPage"]
      self.pageInView.set_listener(self.zlistener)

      self.RunEventThread = True
      self.eventThread = Thread(target = self.eventThreadHandler)

#      self.set_default_size(480, 320)
      self.set_default_size(620, 320)
#      self.set_resizable(False)
      self.set_title("CR101!")

#      if moduleExists("RPi.GPIO"):
#         # connect to the hardware IO
#         import RPi.GPIO as GPIO

      topHBox = Gtk.HBox()

      vBbox = Gtk.VButtonBox()
      b = Gtk.Button("MUTE")
      b.connect("clicked", self.on_zoneMuteButton_Clicked)
      vBbox.pack_start(b, False, False, 1)
      b = Gtk.Button("VOL")
      b.set_sensitive(False)
      vBbox.pack_start(b, False, False, 1)
      b = Gtk.Button("UP")
      b.connect("clicked", self.on_zoneVolUpButton_Clicked)
      vBbox.pack_start(b, False, False, 1)
      b = Gtk.Button("DN")
      b.connect("clicked", self.on_zoneVolDownButton_Clicked)
      vBbox.pack_start(b, False, False, 1)

      topHBox.pack_start(vBbox, False, False, 1)

      self.vbox = Gtk.VBox()
#      self.stack = Gtk.Stack()
#      self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
#      self.stack.set_transition_duration(500)
#      self.stack.set_homogeneous(True)
#      self.stack.connect("notify::visible-child", self.on_Page_Changed)

#      self.stack.add_titled(pageDict["ZonesPage"], "ZonesPage", "Zones!!")
#      self.stack.add_titled(pageDict["MusicPage"], "MusicPage", "Music!!")

#      stack_switcher = Gtk.StackSwitcher()
#      stack_switcher.set_stack(self.stack)

      self.pageRevealer = Gtk.Revealer()
      self.pageRevealer.set_transition_duration(0.5)
      self.pageRevealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
      self.pageRevealer.add(self.pageDict["ZonesPage"])
      self.pageRevealer.set_reveal_child(True)
      self.vbox.pack_start(self.pageRevealer, True, True, 0)

#      self.vbox.pack_start(self.stack, True, True, 0)

      self.queueRevealer = Gtk.Revealer()
      self.queueRevealer.set_transition_duration(0.5)
      self.queueRevealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
      self.queueRevealer.add(self.pageDict["QueuePage"])
      self.queueRevealer.set_reveal_child(False)
      self.vbox.pack_start(self.queueRevealer, True, True, 0)

      buttonBox = Gtk.HButtonBox()
#      buttonBox.set_layout(Gtk.BUTTONBOX_START)
      b = Gtk.Button("A")
      b.connect("clicked", self.on_Button_A_Clicked)
      buttonBox.pack_start(b, True, False, 1)

      b = Gtk.Button("B")
      b.connect("clicked", self.on_Button_B_Clicked)
      buttonBox.pack_start(b, True, False, 1)

      b = Gtk.Button("C")
      b.connect("clicked", self.on_Button_C_Clicked)
      buttonBox.pack_start(b, True, False, 1)

      self.vbox.pack_start(buttonBox, False, False, 0)

      topHBox.pack_start(self.vbox, True, False, 1)


      vBox = Gtk.VBox()
#
      buttonBox = Gtk.HButtonBox()
#      vBox.pack_start(stack_switcher, False, False, 1)
      
      b = Gtk.Button("Zones")
      b.connect("clicked", self.on_Zones_Button_Clicked)
      buttonBox.pack_start(b, True, False, 1)
      
      b = Gtk.Button("Ret")
      b.connect("clicked", self.on_Return_Button_Clicked)
      buttonBox.pack_start(b, True, False, 1)
#      vBox.pack_start(b, False, False, 1)
      b = Gtk.Button("Music")
      b.connect("clicked", self.on_Music_Button_Clicked)
      buttonBox.pack_start(b, True, False, 1)
      
      vBox.pack_start(buttonBox, False, False, 1)

      buttonBox = Gtk.HButtonBox()
#      buttonBox.set_layout(Gtk.BUTTONBOX_START)
      b = Gtk.Button("B")
      b.connect("clicked", self.on_Scroll_Up)
      buttonBox.pack_start(b, True, False, 1)
      b = Gtk.Button("OK")
      b.connect("clicked", self.on_Button_Ok_Clicked)
      buttonBox.pack_start(b, True, False, 1)
      b = Gtk.Button("F")
      b.connect("clicked", self.on_Scroll_Down)
      buttonBox.pack_start(b, True, False, 1)

      vBox.pack_start(buttonBox, True, False, 1)

      buttonBox = Gtk.HButtonBox()
#      buttonBox.set_layout(Gtk.BUTTONBOX_START)
      b = Gtk.Button("Prev")
      b.connect("clicked", self.on_Previous_Button_Clicked)
      buttonBox.pack_start(b, True, False, 1)
      b = Gtk.Button(stock = Gtk.STOCK_MEDIA_PLAY)
      b.connect("clicked", self.on_Play_Button_Clicked)
      buttonBox.pack_start(b, True, False, 1)
      b = Gtk.Button("Next")
      b.connect("clicked", self.on_Next_Button_Clicked)
      buttonBox.pack_start(b, True, False, 1)

      vBox.pack_start(buttonBox, True, False, 1)

      topHBox.pack_start(vBox, False, False, 1)

      self.add(topHBox)

      self.connect("destroy", self.on_destroy)

      self.show_all()

      self.queueRevealer.hide()
      
      self.pageInView.on_Page_Entered_View(None)

   def __del__(self):
      self.RunEventThread = False
#      if self.eventThread.is_alive():
#         self.eventThread.join()


try:
   app = PyApp()
   Gtk.main()
except KeyboardInterrupt:
   app.i2c.Close()
