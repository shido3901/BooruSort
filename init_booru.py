


from PyQt5.QtWidgets import (QMainWindow, QApplication, QLineEdit, QLabel, QWidget, QSizePolicy, QScrollArea, QMenu, QAction,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QToolButton)
from PyQt5.QtCore import Qt, QEvent, QPoint, QTimer

from config.app_config import ApplicationConfig
from config.booru_ui import LightWidget, DarkWidget

"""from db.booru_db import BooruDb
from config.ui_config import UiInfo, ProgressBar

from config.profile_config import ProfileConfig
from config.theme import Theme

from media_properties.media_viewer import MediaManager
from media_properties.search_bar import SearchBar

from tag_properties.taglist import TagList
from tag_properties.tag_manager import TagManager
from media_properties.import_entities import ImportEntities"""

from media_properties.media_bar import MediaBar

import sys

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
      
        app_config = ApplicationConfig(main_window=self)
        app_config.init_config()
        
    def init_ui(self):
       
        main_window     = DarkWidget ()
        top_left_panel  = LightWidget()
        left_panel      = LightWidget()
        top_right_panel = LightWidget(border_radius=True)
        middle_panel    = DarkWidget (border_radius=True)
        bottom_panel    = LightWidget(border_radius=True)

        main_window_layout     = QGridLayout(main_window)
        top_left_panel_layout  = QVBoxLayout(top_left_panel)
        left_panel_layout      = QVBoxLayout(left_panel)
        top_right_panel_layout = QVBoxLayout(top_right_panel)
        middle_panel_layout    = QVBoxLayout(middle_panel)
        bottom_panel_layout    = QVBoxLayout(bottom_panel)

        self.setCentralWidget(main_window)

        main_window_layout.setSpacing(0)

        main_window_layout.addWidget(top_left_panel,  0, 0, 1, 1)
        main_window_layout.addWidget(top_right_panel, 0, 1, 1, 1)
        main_window_layout.addWidget(left_panel,      1, 0, 2, 1) 
        main_window_layout.addWidget(middle_panel,    1, 1, 1, 1)
        main_window_layout.addWidget(bottom_panel,    2, 1, 1, 1)

        main_window_layout.    setContentsMargins(10,10,10,10)
        top_left_panel_layout. setContentsMargins(2,2,2,2)
        top_right_panel_layout.setContentsMargins(2,2,2,2)
        left_panel_layout.     setContentsMargins(2,2,2,2)
        middle_panel_layout.   setContentsMargins(2,2,2,2)
        bottom_panel_layout.   setContentsMargins(2,2,2,2)

        main_window_layout.setRowStretch(0, 1)
        main_window_layout.setRowStretch(1, 50)
        main_window_layout.setRowStretch(2, 1)

        main_window_layout.setColumnStretch(0, 2)
        main_window_layout.setColumnStretch(1, 30)

        #main widgets
        settings_bar       = QWidget()
        tab_bar            = QWidget()
        tag_panel          = QWidget()
        self.media_bar     = MediaBar(main_window)
        media_viewer       = QWidget()
        media_display_area = DarkWidget()
        status_bar         = QWidget()
        
        media_viewer_layout       = QVBoxLayout(media_viewer)
        media_display_area_layout = QHBoxLayout(media_display_area)

        tab_bar.  setMinimumWidth(300)
        tag_panel.setMinimumWidth(200)

        settings_bar.setMinimumHeight(30)
        tag_panel.   setMinimumHeight(500)
        status_bar.  setMinimumHeight(30)

        top_left_panel_layout. addWidget(settings_bar)
        top_right_panel_layout.addWidget(tab_bar)
        left_panel_layout.     addWidget(tag_panel)
        middle_panel_layout.   addWidget(media_viewer)
        bottom_panel_layout.   addWidget(status_bar)
        media_viewer_layout.   addWidget(self.media_bar, 1)
        media_viewer_layout.   addWidget(media_display_area, 30)

        media_display_area_layout.setContentsMargins(5,0,5,5)
        media_viewer_layout.      setContentsMargins(0,0,0,0)

        media_viewer_layout.setSpacing(0)

    
        
        #media_display_area.setStyleSheet("background-color: white;")
  
       

def main():

    BooruSort = QApplication(sys.argv)
    
    main_window = MainWindow()
    main_window.show()

    sys.exit(BooruSort.exec_())

if __name__ == "__main__":
    main()