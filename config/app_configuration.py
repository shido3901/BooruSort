import json, os
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QTimer, QSettings
from config.booru_ui import Theme

from config.profile_configuration import ProfileConfiguration as ProfileConfig
from config.booru_ui import message_signal

import logging

with open("info.log", "w"):
    pass

logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("info.log"),
            logging.StreamHandler() 
        ]
    )

def log_info(text):
    logging.info(text)
    

message_signal.text.connect(log_info)

default_app_config = (
{
  "profile":{
      "current_profile": False
  },
  "theme": {
    "mode": "booru",
  },
  "media_viewer": {
    "amount_per_page": 25,
    "size": 256,
    "layout": "fit"
  },
  "first_open": {
    "show_tips": True
  },

  "version": {
    "current_version": "1.0.0",
    "last_updated": "2025-08-07"
  }
})

script_dir  = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "app_config.json")

class ApplicationConfiguration():
    def __init__(self, db, main_window, DEBUG_MODE):
        
      self.booru_db = db
      self.main_window=main_window
      self.config_path = config_path
  
      try:
          with open(self.config_path, 'r') as f:

              self.app_config_json = json.load(f)

      except FileNotFoundError:
          
          self.app_config_json = default_app_config
          self.dump_json(self.app_config_json)

      mode = (self.app_config_json["theme"]["mode"]) if DEBUG_MODE == 0 else "debug"

      self.theme = Theme()
      self.theme.set_theme(mode)

      self.restore_window_state()

      self.main_window.setStyleSheet(self.theme.background_color_dark)
      self.main_window.setWindowTitle("BooruSort")

      self.profile_config = ProfileConfig(main_window=self.main_window, db=self.booru_db, app_config=self)

    def dump_json(self, dump_info):
        
        with open(self.config_path, 'w') as f:
              json.dump(dump_info, f, indent=4)

    def restore_window_state(self):
        
        settings        = QSettings("BooruSort")
        window_geometry = settings.value("geometry")
        window_state    = settings.value("windowState")

        if window_geometry:
            self.main_window.restoreGeometry(window_geometry)

        else:
            self.set_screen_dimensions()
            
        if window_state:
            self.main_window.restoreState(window_state)

    def save_window_state(self):
        
        settings = QSettings("BooruSort")
        settings.setValue("geometry", self.main_window.saveGeometry())
        settings.setValue("windowState", self.main_window.saveState())
      
    def set_screen_dimensions(self):
        
        screen = QGuiApplication.primaryScreen()
        available = screen.availableGeometry()

        screen_width = available.width()
        screen_height = available.height()

        x = available.x()
        y = available.y()

        aspect_ratio = screen_width / screen_height

        if aspect_ratio >= 1.0:
            window_width = int(screen_width * 0.7)
            window_height = int(screen_height * 0.7)
        else:
            window_width = int(screen_width * 0.9)
            window_height = int(screen_height * 0.5)

        x = (screen_width - window_width) // 2 + x
        y = (screen_height - window_height) // 2 + y

        self.main_window.setGeometry(x, y, window_width, window_height)
        
        

    
        

