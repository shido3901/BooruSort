
import os

from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QSizePolicy,
                             QGridLayout, QDialog,QLabel, QLineEdit, QScrollArea)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize,  QTimer, QEvent 

from config.booru_ui import notification_message as notify

import json, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

profile_config_json = {
    "tabs":{
      "tab_list": [],
      "current_tab": [],
    },
    "category": {},

}

class ProfileConfiguration(QDialog):
    def __init__(self, main_window, db, app_config):
        super().__init__()

        self.booru_db    = db
        self.main_window = main_window
        self.app_config  = app_config

        self.profile_config_json = profile_config_json
        self.app_config_json = self.app_config.app_config_json

        self.current_profile = self.app_config_json["profile"]["current_profile"]

        if self.current_profile:
            notify(f"loaded profile {self.current_profile}")
            self.set_current_profile(self.current_profile)

        else:
            profile_name = "User"

            self.booru_db.add_profile(profile_name)
            self.current_profile = profile_name  

        self.initUI()

        self.profile_list = self.booru_db.get_profile_list()

        if self.profile_list:
            self.load_profile_list()

        else:
            print('no profile, creating new...')

        if self.current_profile not in self.profile_list:
            print('PROFILE MISMATCH') #add error handling later

            profile_name = "User"

            self.booru_db.add_profile(profile_name)
            self.current_profile = profile_name  


    
    def load_profile(self):

        

        

        self.close()

        self.profile_config_json = self.load_json()
        self.booru_db.load_db_info(self.current_profile)

        QTimer.singleShot(1000, lambda: (self.main_window.init_profile_info(),
                                         notify(f"successfully loaded '{self.current_profile}'"),
                                         (self.booru_db.set_window_title())
                                         ))
        
    def select_profile(self, profile_name):

        if profile_name != self.current_profile:

            self.set_current_profile(profile_name)
            self.main_window.clear_ui()
            self.load_profile()
       
        else:
            print('already selected')

            self.close()

    def set_current_profile(self, profile_name):

        self.current_profile = profile_name

        self.app_config_json["profile"]["current_profile"] = profile_name
        self.app_config.dump_json(self.app_config_json)

        self.directory_name   = f"{self.current_profile}"
        self.thumbnail_folder = f"{self.current_profile}/thumbnails"
        self.config_path = os.path.join(self.directory_name, "config.json")
        
        try:
            os.mkdir(self.directory_name)

        except FileExistsError:
            
            print(f"Directory '{self.directory_name}' already exists.")

        try:
            os.mkdir(self.thumbnail_folder)

        except FileExistsError:
            
            print(f"Thumbnail folder '{self.thumbnail_folder}' already exists.")

    def dump_json(self, info):

        with open(self.config_path, 'w') as f:
                json.dump(info, f, indent=4)

    def load_json(self):

        try:
            with open(self.config_path, 'r') as f:

                profil_config_info = json.load(f)
                return profil_config_info
            
        except Exception as e:
            
            with open(self.config_path, 'w') as f:
                json.dump(self.profile_config_json, f, indent=4)

                print(e)

                return self.profile_config_json
        
    def load_profile_list(self):

        self.profile_in_progress = False

        for i, name in enumerate(self.profile_list):

            row = i // self.columns
            col = i % self.columns
            profile = Profile(name, profile_config=self)
            self.grid_layout.addWidget(profile, row, col)

        last_index = len(self.profile_list)
        self.add_to_last(last_index)

    def add_to_last(self, last_index, pip=False):

        self.profile_in_progress = False if not pip else True

        row =  last_index // self.columns
        col =  last_index % self.columns
       
        self.last_profile = Profile(name=None, profile_config=self)
        self.grid_layout.addWidget(self.last_profile, row, col)

    def delete_last_profile(self):

        last_index = len(self.profile_list)
        
        self.profile_in_progress = False
        self.last_profile.deleteLater()
        self.add_to_last(last_index)

    def initUI(self):

        self.profile_icon = os.path.join(BASE_DIR, "icons", "profile.png")

        self.setWindowTitle(f"BooruSort - select profile")
        self.setFixedSize(400,300)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint )
        self.setStyleSheet("background-color: #010c1c;")
      
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        self.grid_layout = QGridLayout(scroll_content)
        self.columns = 4

class Profile(QWidget):
    def __init__(self, name, profile_config):
        super().__init__()

        self.profile_config = profile_config
        self.curr_name = name

        self.enter_key = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.add_profile_widget = QWidget()
        self.add_profile_widget.setFixedSize(50, 75)

        self.add_profile_widget_layout = QVBoxLayout(self.add_profile_widget)
        self.add_profile_widget_layout.setSpacing(0)
        self.add_profile_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.load_config(name)

    def load_config(self, name):

        if name is not None:

            self.profile_button = QPushButton(QIcon(self.profile_config.profile_icon), "")
            self.profile_button.setIconSize(QSize(50,50))
            self.profile_button.setCursor(Qt.PointingHandCursor)
            self.profile_button.setFixedSize(50,50)
            self.add_profile_widget_layout.addWidget(self.profile_button)

            if name == self.curr_name:
            
                self.profile_label = QLabel(name)
                self.profile_label.setText(name)
                self.profile_label.setAlignment(Qt.AlignCenter)
                
                self.profile_button.clicked.connect(lambda: self.profile_config.select_profile(name))
            
            else:
                
                self.profile_label = QLineEdit()

                self.profile_label.setFixedHeight(20)
                self.profile_label.installEventFilter(self)
                self.profile_button.setCursor(Qt.ArrowCursor)

            self.profile_label.setStyleSheet("font-size: 14px; color: white;")

            self.add_profile_widget_layout.addWidget(self.profile_label)

        else:

            self.plus_button = QPushButton("+")  
            self.plus_button.setFixedSize(50, 50)
            self.plus_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.add_profile_widget_layout.addWidget(self.plus_button)

            #bbbbbb

            #aaaaaa

            pip = self.profile_config.profile_in_progress

            if not pip:
                self.plus_button.clicked.connect(self.add_new)

            self.plus_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #cccccc;
                    border: none;
                    border-radius: 12px;
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                }}

                QPushButton:hover {{
                    background-color: {"#bbbbbb" if not pip else "#cccccc"};
                }}

                QPushButton:pressed {{
                    background-color: {"#aaaaaa" if not pip else "#cccccc"};
                }}
                """)
              
        self.layout.addWidget(self.add_profile_widget)
        
    def add_new(self):

        self.plus_button.deleteLater()
        self.load_config(name="")

        new_len = len(self.profile_config.profile_list) + 1
        self.profile_config.add_to_last(new_len, pip=True)
        
        QTimer.singleShot(0, self.profile_label.setFocus)

    def create_new_profile(self, source):
            
        self.enter_key = True
        profile_name = self.profile_label.text().strip()

        if profile_name:
         
            if profile_name not in self.profile_config.profile_list:

                self.profile_config.booru_db.add_profile(profile_name)
                self.profile_config.profile_list.append(profile_name)

                self.profile_button.deleteLater()
                self.profile_label.deleteLater()

                self.curr_name = profile_name
                self.load_config(profile_name)

                self.profile_config.select_profile(profile_name)
                print('loaded NEW PROFILE')


            else:
                #invalid_entry = MessageBox(f"profile {profile_name} already exists.", "info", "BooruSort")
                self.cancel_profile()
                #invalid_entry.show()

        elif source == 1:
            pass
            #invalid_entry = MessageBox(f"Error: name can't be empty.", "info", "BooruSort")
            #invalid_entry.show()
            
        elif source == 0:

            self.cancel_profile()

        self.profile_label.setFocus()
        self.enter_key = False
      
    def cancel_profile(self):

        self.add_profile_widget.deleteLater()
        self.profile_config.delete_last_profile()

    def eventFilter(self, obj, event):
        if obj == self.profile_label:
            if event.type() == QEvent.FocusOut:

                if self.enter_key is False:
                    self.create_new_profile(0)

            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Escape:
                    self.cancel_profile()
                    return True

            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Return:
            
                    self.create_new_profile(1)

        return super().eventFilter(obj, event)