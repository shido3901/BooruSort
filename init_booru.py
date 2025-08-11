


from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QSizePolicy,
                             QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt

from config.app_configuration import ApplicationConfiguration as Config
from config.booru_ui import LightWidget, DarkWidget

from media_properties.media_bar import MediaBar
from media_properties.media_viewer import MediaViewer
from media_properties.tab_bar import TabBar

import sys

DEBUG_MODE = 0

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
      
        app_config = Config(main_window=self)
        app_config.init_config(DEBUG_MODE)
        self.init_ui()

    def resizeEvent(self, a0):
        return super().resizeEvent(a0)
        
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

        #settings widget

        tab_bar      = TabBar()
        media_area   = QWidget()
        media_viewer = MediaViewer(media_area)
        media_bar    = MediaBar(main_window, media_viewer)

        media_area.setStyleSheet("border-top-left-radius: 0px; border-top-right-radius: 0px;")


        media_area_layout = QVBoxLayout(media_area)
        


        tabs_area._layout  .addWidget(tab_bar)
        center_area._layout.addWidget(media_bar, 1)

        center_area._layout.addWidget(media_area, 50)
        media_area_layout  .addWidget(media_viewer)


        tabs_area._layout  .setContentsMargins(0,0,0,0)

        center_area._layout.setContentsMargins(0,0,0,0)

        center_area._layout.setSpacing(0)

        
     

    
        
        #media_display_area.setStyleSheet("background-color: white;")"""

    
  
       

def main():

    BooruSort = QApplication(sys.argv)
    
    main_window = MainWindow()
    main_window.show()

    sys.exit(BooruSort.exec_())

if __name__ == "__main__":
    main()