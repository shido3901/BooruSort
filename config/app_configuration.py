import json, os
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QTimer
from config.booru_ui import Theme



app_config = (
{
  "theme": {
    "mode": "booru",
  },
  "media_viewer": {
    "amount_per_page": 25,
    "size": 256,
    "layout": "fit"
  },
  "window": {
    "fullscreen": False,
  },
  "first_open": {
    "show_tips": True
  },

  "version": {
    "current_version": "1.0.0",
    "last_updated": "2025-08-07"
  }
})

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "app_config.json")

class ApplicationConfiguration():
    def __init__(self, main_window):

        self.main_window=main_window

        self.app_config = app_config
        self.config_path = config_path

        try:
            with open(self.config_path, 'r') as f:

                self.app_config = json.load(f)

        except FileNotFoundError:

            with open(self.config_path, 'w') as f:
                json.dump(self.app_config, f, indent=4)

    def init_config(self, DEBUG_MODE):

        theme = Theme()
        mode = (self.app_config["theme"]["mode"]) if DEBUG_MODE == 0 else "debug"

        theme.set_theme(mode)
       
        x, y, window_width, window_height = self.get_screen_info()

        self.main_window.setGeometry(x, y, window_width, window_height)
        self.main_window.setStyleSheet(theme.background_color_dark)
     
        




        

    def get_screen_info(self):
        screen = QGuiApplication.primaryScreen()
        available = screen.availableGeometry()

        screen_width = available.width()
        screen_height = available.height()

        x =  available.x()
        y =  available.y()

        aspect_ratio = screen_width / screen_height

        if aspect_ratio >= 1.0:
            window_width = int(screen_width * 0.7)
            window_height = int(screen_height * 0.7)
        else:
            window_width = int(screen_width * 0.9)
            window_height = int(screen_height * 0.5)

        x = (screen_width - window_width) // 2 + x
        y = (screen_height - window_height) // 2 + y

        return x, y, window_width, window_height
        

        

    
        

