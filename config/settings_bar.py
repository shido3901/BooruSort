from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QSizePolicy, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt

class SettingsBar(QWidget):
    def __init__(self, profile_config):
        super().__init__()

        self.profile_config = profile_config


    
        self.init_ui()

    def init_ui(self):

        self.settings_layout = QHBoxLayout(self)

        self.profile_list = QPushButton("profile")

        self.settings_layout.addWidget(self.profile_list)

        self.profile_list.setMinimumWidth(25)

        

        self.settings_layout.setContentsMargins(0, 0, 0, 0)

        self.settings_layout.addStretch()

        self.settings_layout.setSpacing(0)
     
        self.profile_list.clicked.connect(self.profile_config.show)
        self.profile_list.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: transparent;
                    border: none;
                    padding: 0 4px;
                    border-radius: 4px;   
                    margin: 0;
                    font-size: 14px;
                }
                QPushButton:hover {
                    color: cyan;
                    background-color: rgba(255, 255, 255, 60);  /* a bit more visible on hover */
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 80);  /* even more visible when clicked */
                }
            """)
        

        

