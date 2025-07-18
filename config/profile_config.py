
import os, sys, json, shutil, sqlite3

from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QGridLayout, QDialog,QLabel, QLineEdit, QApplication, QScrollArea)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal,  QTimer, QEvent
from config.ui_config import MessageBox

import pywinstyles, json, os

class CategoryManager():
    def __init__(self, profile_name):
        super().__init__()
    
        self.profile_name = profile_name

    def load_json(self):
    
        self.full_path = os.path.join(self.profile_name, f"{self.profile_name}_config.json")
        
        try:
            with open(self.full_path, 'r') as f:
                profile_data = json.load(f)
                categories_list = profile_data["categories"]
                
        except (FileNotFoundError, json.JSONDecodeError):

            self.dump_json(cat_list=None)
            
        return categories_list
    
    def dump_json(self, cat_list):

        category_default_config = {
            "categories": cat_list
            }
    
        with open(self.full_path, 'w') as f:
            json.dump(category_default_config, f, indent=4)

        return category_default_config

class ProfileConfig(QDialog):
    def __init__(self, main_window=None, booru_db=None):
        super().__init__()

        self.profile_list = []

        self.initUI()

        self.booru_db = booru_db
        self.main_window = main_window
        
        try:
            self.profile_list = self.booru_db.get_profile_list()

            if self.profile_list:
                self.load_profiles()
               
            else:
                self.no_profile_config()

        except:
            print('no profile detected')
            self.no_profile_config()


       

        try:
            with open('profiles.json', 'r') as f:
                current_profile = json.load(f)
                self.current_profile = current_profile["current_profile"]

        

        except (FileNotFoundError, json.JSONDecodeError):

            default_config = {
            "current_profile": None
            }
        
            with open('profiles.json', 'w') as f:
                json.dump(default_config, f, indent=4)

        if self.current_profile:
            try:
                self.booru_db.set_curr_profile(self.current_profile)
            except:
                self.current_profile = None

            try:

                directory_name = (f"{self.current_profile}")
                os.mkdir(directory_name)

                thumbnail_folder = (f"{self.current_profile}/thumbnails")
                os.mkdir(thumbnail_folder)

        
                

            except FileExistsError:
                print(f"'{directory_name}' already exist.")
            except PermissionError:
                print(f"Permission denied: Unable to create '{directory_name}'.")
            except Exception as e:
                print(f"An error occurred: {e}")


                  
        self.setWindowTitle(f"BooruSort - select profile")
        self.setFixedSize(800, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint )

    def no_profile_config(self):

        self.booru_db.create_tables()
        self.load_profiles()
        
        self.main_window.setWindowTitle(f"BooruSort - no profile")

    def load_profile(self, name):

        default_config = {
        "current_profile": name
        }

        with open('profiles.json', 'w') as f:
                json.dump(default_config, f, indent=4)

        self.booru_db.set_curr_profile(name)
        #self.main_window.load_profile()

        self.close()

    def set_style(self):
        pywinstyles.apply_style(self, "aero")

    def initUI(self):
      
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        self.grid_layout = QGridLayout(scroll_content)
        self.columns = 4

    def load_profiles(self):

        self.profile_in_progress = False
        for i, name in enumerate(self.profile_list):
            row = i // self.columns
            col = i % self.columns
            profile = Profile(name, profile_config=self)
            self.grid_layout.addWidget(profile, row, col)

        last_index = len(self.profile_list)
        self.add_to_last(last_index)

    def add_to_last(self, last_index):

        self.profile_in_progress = False
        row =  last_index // self.columns
        col =  last_index % self.columns
       
        self.last_profile = Profile(name=None, profile_config=self)
        self.grid_layout.addWidget(self.last_profile, row, col)

    def delete_last_profile(self):

        last_index = len(self.profile_list)
        
        self.profile_in_progress = False
        self.last_profile.deleteLater()
        self.add_to_last(last_index)

class Profile(QWidget):
    def __init__(self, name, profile_config):
        super().__init__()

        self.profile_config = profile_config
        self.curr_name = name

        self.enter_key = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.add_profile_widget = QWidget()
        self.add_profile_widget.setFixedSize(150, 200)

        self.add_profile_widget_layout = QVBoxLayout(self.add_profile_widget)
        self.add_profile_widget_layout.setSpacing(0)
        self.add_profile_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.load_config(name)

    def load_config(self, name):

        if name is not None:

            self.profile_button = QPushButton(QIcon(r"2bda51ca60cc3b5daaa8e062eb880430.jpg"), "")
            self.profile_button.setIconSize(QSize(150,150))
            self.profile_button.setCursor(Qt.PointingHandCursor)
            self.profile_button.setFixedSize(150,150)
            self.add_profile_widget_layout.addWidget(self.profile_button)

            if name == self.curr_name:
            
                self.profile_label = QLabel(name)
                self.profile_label.setText(name)
                self.profile_label.setAlignment(Qt.AlignCenter)
                self.profile_label.setStyleSheet("color: white;")
                self.profile_button.clicked.connect(lambda: self.profile_config.load_profile(name))
            
            else:
                
                self.profile_label = QLineEdit()
                self.profile_label.setStyleSheet("font-size:30px; color: white;")

                self.profile_label.setFixedHeight(35)
                self.profile_label.installEventFilter(self)
                self.profile_button.setCursor(Qt.ArrowCursor)

            self.add_profile_widget_layout.addWidget(self.profile_label)

        else:

            self.plus_button = QPushButton("+")  
            self.plus_button.setFixedSize(100, 100)
            self.plus_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.add_profile_widget_layout.addWidget(self.plus_button)

            if self.profile_config.profile_in_progress is False:
                self.plus_button.clicked.connect(self.add_new)
                self.plus_button.setStyleSheet("""
                QPushButton {
                    background-color: #cccccc;
                    border: none;
                    border-radius: 12px;
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                }
                                               
                QPushButton:hover {
                    background-color: #bbbbbb;
                }
                QPushButton:pressed {
                    background-color: #aaaaaa;
                }
                """)

            else:
                self.plus_button.setStyleSheet("""
                QPushButton {
                    background-color: #cccccc;
                    border: none;
                    border-radius: 12px;
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                }
        
                """)
              
        self.layout.addWidget(self.add_profile_widget)
        
    def add_new(self):
        self.profile_config.profile_in_progress = True

        self.plus_button.deleteLater()
        self.load_config(name="")

        new_len = len(self.profile_config.profile_list) + 1
        self.profile_config.add_to_last(new_len)
        QTimer.singleShot(0, self.profile_label.setFocus)

    def create_new_profile(self, source):
            
        self.enter_key = True
        profile_name = self.profile_label.text().strip()

        if profile_name:
         
            if profile_name not in self.profile_config.profile_list:
                self.profile_config.booru_db.add_profile(profile_name)

                self.profile_button.deleteLater()
                self.profile_label.deleteLater()

                self.curr_name = profile_name
                self.load_config(profile_name)

                self.profile_config.profile_list.append(profile_name)
                self.profile_config.load_profile(profile_name)


            

            else:
                invalid_entry = MessageBox(f"profile {profile_name} already exists.", "info", "BooruSort")
                self.cancel_profile()
                invalid_entry.show()

        elif source == 1:
            invalid_entry = MessageBox(f"Error: name can't be empty.", "info", "BooruSort")
            invalid_entry.show()
            
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
    
    

    