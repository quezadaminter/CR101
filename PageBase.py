import soco
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from abc import ABCMeta, abstractmethod

class PageBase(Gtk.VBox):
   __metaclass__=ABCMeta
#   @abstractmethod
   def on_zoneButton_Clicked(self):
      self.topLevel.show_page("ZonesPage")

   def on_musicButton_Clicked(self):
      if self.topLevel.pageInView == self.topLevel.pageDict["MusicPage"]:
         self.topLevel.show_page("MusicPlayingPage")
      else:
         self.topLevel.show_page("MusicPage")

   @abstractmethod
   def on_Page_Entered_View(self, selectedZone):
       pass

   # The row of buttons at the bottom of the screen
   @abstractmethod
   def on_Button_A_Clicked(self):
       pass

   @abstractmethod
   def on_Button_B_Clicked(self):
       pass

   @abstractmethod
   def on_Button_C_Clicked(self):
       pass

   @abstractmethod
   def on_Return_Button_Clicked(self):
       pass

   # The scroll wheel
   @abstractmethod
   def on_Scroll_Up(self):
       pass

   @abstractmethod
   def on_Scroll_Down(self):
       pass

   @abstractmethod
   def on_Button_Ok_Clicked(self):
       pass

   @abstractmethod
   def title(self):
       pass

   @abstractmethod
   def scrolledWindow(self):
       pass

   @abstractmethod
   def status(self):
       pass

   @abstractmethod
   def footer(self):
       pass

   def set_top_level(self, tl):
       self.topLevel = tl

   def __init__(self):
      super().__init__(self, Gtk.Orientation.HORIZONTAL, 6)
      # Initialize data members
      self.topLevel = None
      self.selectedZone = None
      self.fromPage = None
      # Build the basic GUI structure of
      # the interface pages.
      self.set_homogeneous(False)
      self.pack_start(self.title(), False, False, 0)
      self.pack_start(self.scrolledWindow(), True, True, 1)
      self.statusGrid = self.status()
      if self.statusGrid is not None:
         self.pack_start(self.status(), False, False, 0)
      self.pack_start(self.footer(), False, False, 0)
      self.show_all()