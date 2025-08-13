


from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout)
from PyQt5.QtCore import Qt

from db.booru_db import BooruDb
from config.app_configuration import ApplicationConfiguration as AppConfig

from config.settings_bar import SettingsBar

from media_properties.media_bar import MediaBar
from media_properties.media_viewer import MediaViewer
from media_properties.tab_bar import TabBar

from config.booru_ui import LightWidget, DarkWidget, InformationBar, message_signal

import sys

DEBUG_MODE = 0

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.booru_db   = BooruDb(main_window=self)
        self.app_config = AppConfig(main_window=self, db=self.booru_db, DEBUG_MODE=DEBUG_MODE)

        self.profile_config = self.app_config.profile_config

        self.init_ui()     
        self.profile_config.load_profile()

    def init_profile_info(self):

        self.tab_bar.load_tabs()
       
    def clear_ui(self):
        self.setWindowTitle("BooruSort")

        self.tab_bar.clear()

    def closeEvent(self, event):
        self.app_config.save_window_state()
        
        super().closeEvent(event)

        
    def init_ui(self):
       
        main_window = DarkWidget ("QGrid", border_radius=True)
        settings    = LightWidget("QVBox", border_radius=True)
        tag_area    = LightWidget("QVBox", border_radius=True)
        tabs_area   = LightWidget("QHBox", border_radius=True)
        center_area = DarkWidget ("QVBox", border_radius=True)
        bottom_area = LightWidget("QVBox", border_radius=True)

        self.setCentralWidget(main_window)

        main_window.BooruLayout.setSpacing(0)

        main_window.BooruLayout.addWidget(settings,    0, 0, 1, 1)
        main_window.BooruLayout.addWidget(tabs_area,   0, 1, 1, 1)
        main_window.BooruLayout.addWidget(tag_area,    1, 0, 2, 1) 
        main_window.BooruLayout.addWidget(center_area, 1, 1, 1, 1)
        main_window.BooruLayout.addWidget(bottom_area, 2, 1, 1, 1)

        main_window.BooruLayout.setContentsMargins(10,10,10,10)
        settings.   BooruLayout.setContentsMargins(2,2,2,2)
        tabs_area.  BooruLayout.setContentsMargins(2,2,2,2) 
        tag_area.   BooruLayout.setContentsMargins(2,2,2,2)
        center_area.BooruLayout.setContentsMargins(2,2,2,2)
        bottom_area.BooruLayout.setContentsMargins(2,2,2,2)

        main_window.BooruLayout.setRowStretch(0, 1)
        main_window.BooruLayout.setRowStretch(1, 50)
        main_window.BooruLayout.setRowStretch(2, 1)

        main_window.BooruLayout.setColumnStretch(0, 2)
        main_window.BooruLayout.setColumnStretch(1, 30)

        tabs_area.setMinimumWidth(300)
        tag_area .setMinimumWidth(200)

        settings .setMinimumHeight(30)
        tag_area .setMinimumHeight(500)
       
        bottom_area.setMinimumHeight(30)

        settings_bar = SettingsBar(self.profile_config)
        self.tab_bar = TabBar     (self.profile_config)
        media_area   = QWidget    (          )
        media_viewer = MediaViewer(media_area)
        media_bar    = MediaBar   (main_window, media_viewer)
        notification = InformationBar()

        
       
        media_area_layout = QVBoxLayout(media_area)

        media_area.setStyleSheet("border-top-left-radius: 0px; border-top-right-radius: 0px;")

        settings._layout   .addWidget(settings_bar)
        tabs_area._layout  .addWidget(self.tab_bar)
        center_area._layout.addWidget(media_bar, 1)
        bottom_area._layout.addWidget(notification)

        center_area._layout.addWidget(media_area, 50)
        media_area_layout  .addWidget(media_viewer)

        settings._layout   .setContentsMargins(0,0,0,0)
        tabs_area._layout  .setContentsMargins(0,0,0,0)
        bottom_area._layout.setContentsMargins(0,0,0,0)

        center_area._layout.setContentsMargins(0,0,0,0)

        center_area._layout.setSpacing(0)

        message_signal.text.connect(notification.change_text)

         #media_display_area.setStyleSheet("background-color: white;")"""

    def mousePressEvent(self, a0):
        self.setFocus()
        return super().mousePressEvent(a0)

def main():

    BooruSort = QApplication(sys.argv)
    
    main_window = MainWindow()
    main_window.show()

    sys.exit(BooruSort.exec_())

if __name__ == "__main__":
    main()