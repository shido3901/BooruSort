# Copyright (C) 2025 Booru Sort Lite
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

from PyQt5.QtWidgets import (QMainWindow, QApplication, QLabel, QWidget, QSizePolicy, QScrollArea, QMenu, QAction,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QDesktopWidget, QToolButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication

from config.booru_db import BooruDb
from config.profile_config import ProfileConfig
from config.theme import Theme

from media_properties.import_entities import ImportEntities, ThumbnailCreation
from media_properties.media_viewer import MediaManager
from media_properties.search_bar import SearchBar

from tag_properties.taglist import TagList
from tag_properties.tag_manager import TagManager
from tag_properties.tag_manager_categories import TMCategories


import pywinstyles

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        screen = QGuiApplication.primaryScreen()
        available = screen.availableGeometry()

        screen_width = available.width()
        screen_height = available.height()

        aspect_ratio = screen_width / screen_height
        if aspect_ratio >= 1.0:
            window_width = int(screen_width * 0.7)
            window_height = int(screen_height * 0.7)
        else:
            window_width = int(screen_width * 0.9)
            window_height = int(screen_height * 0.5)

        x = (screen_width - window_width) // 2 + available.x()
        y = (screen_height - window_height) // 2 + available.y()

        self.setGeometry(x, y, window_width, window_height)
        
        self.setStyleSheet("background-color: #010c1c;")

        self.theme = Theme(theme=1)

        self.booru_db = BooruDb(main_window=self)
        self.profile = ProfileConfig(main_window=self, booru_db=self.booru_db)
        self.initUI()

    
    def load_info(self):
        pass

        
    def initUI(self):
        self.tag_manager = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        pywinstyles.change_header_color(self, color="#00366CFF") 
        pywinstyles.change_border_color(self, color="#112233") 
        
        grid_layout = QGridLayout(self.central_widget)
        self.central_widget.setLayout(grid_layout)

        self.左パネル = QWidget(self.central_widget)
        self.左パネル.setMinimumWidth(300)
        self.左パネル.setMaximumWidth(475)
        self.左パネル.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.左パネル.setStyleSheet(self.theme.left_panel_ui)
        grid_layout.addWidget(self.左パネル, 0, 0, 3, 1)

        self.左パネルレイアウト = QVBoxLayout(self.左パネル)
        self.左パネルレイアウト.setContentsMargins(0, 0, 0, 0)
        self.左パネルレイアウト.setSpacing(5)

        self.profile_panel = QWidget(self.左パネル)
        self.profile_panel.setMinimumWidth(250)
        self.profile_panel.setMinimumHeight(70)
        self.profile_panel.setMaximumHeight(70)
        self.profile_panel.setStyleSheet(self.theme.widgets)
        self.左パネルレイアウト.addWidget(self.profile_panel)

        profile_panel_layout = QVBoxLayout(self.profile_panel)

        profile_select_button = QPushButton(f"profile",  self.profile_panel)
        profile_select_button.setCursor(Qt.PointingHandCursor)
        profile_select_button.setStyleSheet(self.theme.buttons)       
        profile_panel_layout.addWidget(profile_select_button, alignment=Qt.AlignLeft)
        profile_select_button.clicked.connect(self.open_profile_config)

        self.タグパネル追加 = QWidget(self.左パネル)
        self.タグパネル追加.setMinimumWidth(250)
        self.タグパネル追加.setMinimumHeight(50)
        self.タグパネル追加.setMaximumHeight(70)
        self.タグパネル追加.setStyleSheet(self.theme.widgets_next)
        self.左パネルレイアウト.addWidget(self.タグパネル追加, stretch=1)

        self.add_tag_panel_layout = QHBoxLayout(self.タグパネル追加)

        self.tag_label = QLabel("tags")
        self.tag_label.setStyleSheet(self.theme.qlabel)
        self.tag_label.setMinimumHeight(27)
        self.add_tag_panel_layout.addWidget(self.tag_label, alignment=Qt.AlignLeft)

        self.sort_button = QToolButton()
        self.sort_button.setText(f"sort by: newest ")
        self.sort_button.setPopupMode(QToolButton.InstantPopup)
        self.sort_button.setCursor(Qt.PointingHandCursor)
        self.sort_button.setMinimumHeight(40)
        self.sort_button.setStyleSheet(self.theme.buttons)
        self.sort_button.setMenu(self.create_menu())
        self.add_tag_panel_layout.addWidget(self.sort_button, alignment=Qt.AlignLeft)
        
        add_tag_button = QPushButton("add +", self.タグパネル追加)
        add_tag_button.setCursor(Qt.PointingHandCursor)
        add_tag_button.setMinimumHeight(30)
        add_tag_button.setStyleSheet(self.theme.buttons)
        self.add_tag_panel_layout.addWidget(add_tag_button, alignment=Qt.AlignRight)

        self.tag_list = QWidget(self.左パネル)
        self.tag_list.setMinimumWidth(250)
        self.tag_list.setMinimumHeight(200)
        self.tag_list.setStyleSheet(self.theme.widgets)

        self.tag_list_layout = QVBoxLayout()
        self.tag_list_layout.setSpacing(0)
        self.tag_list_layout.setContentsMargins(0,0,0,0)
        self.tag_list.setLayout(self.tag_list_layout)

        new_tag_scroll_area = QScrollArea()
        new_tag_scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0,0,0,0)
        scroll_layout.setSpacing(2)
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
     
        new_tag_scroll_area.setWidget(scroll_content)
        new_tag_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }

            QScrollBar:vertical {
                background: #2c2c2c;
                width: 10px;
                margin: 2px 0 2px 0;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: #555;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #888;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
                border: none;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollBar:horizontal {
                height: 8px;
                background: #2c2c2c;
            }

            QScrollBar::handle:horizontal {
                background: #555;
                border-radius: 4px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #888;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0;
                background: none;
                border: none;
            }

            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

        self.tag_list_layout.addWidget(new_tag_scroll_area)
        
        self.左パネルレイアウト.addWidget(self.tag_list, stretch=7)

        
        
      
        self.top_bar = QWidget(self.central_widget)
        self.top_bar.setMinimumWidth(600)
        self.top_bar.setMinimumHeight(30)
        self.top_bar.setMaximumHeight(70)
        self.top_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.top_bar.setStyleSheet(self.theme.ui)
        grid_layout.addWidget(self.top_bar, 0, 1)

        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.top_bar_layout.setSpacing(0)

        self.search_bar_widget = QWidget(self.top_bar)
        self.search_bar_widget.setMinimumWidth(300)
        self.search_bar_widget.setStyleSheet(self.theme.widgets_next)
        self.top_bar_layout.addWidget(self.search_bar_widget)

        self.search_bar_widget_layout = QHBoxLayout(self.search_bar_widget)
        self.search_bar_widget_layout.setContentsMargins(10,1,1,10)
        self.search_bar_widget_layout.setSpacing(7)

        self.save_search = QPushButton("", self.search_bar_widget)
        self.save_search.setCursor(Qt.PointingHandCursor)
        self.save_search.setMinimumHeight(30)
        self.save_search.setMaximumWidth(170)
        self.save_search.setStyleSheet(self.theme.buttons)
        self.search_bar_widget_layout.addWidget(self.save_search)


        self.main_area = QWidget(self.central_widget)
        self.main_area.setMinimumWidth(300)
        self.main_area.setMinimumHeight(600)
        self.main_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_area.setStyleSheet(self.theme.ui)
        grid_layout.addWidget(self.main_area, 1, 1)

        self.main_area_layout = QGridLayout()
        self.main_area.setLayout(self.main_area_layout)

        self.image_manager = MediaManager(self.booru_db, self.main_area)
        self.main_area_layout.addWidget(self.image_manager)
        

        self.search_bar = SearchBar(self.image_manager, self.search_bar_widget)

        #loading TagList will CRASH if there is no profile. add a "if curr user exists, then load this" or
        #put the try and exxcept block in taglist.py

        self.new_tag_list = TagList(self.booru_db, scroll_layout, self.search_bar)
        self.new_tag_list.load_new_tag_buttons()

        self.thumb_creator = ThumbnailCreation(entity_list=None, tag_list=None)
  

        self.search_bar.text_box.setStyleSheet("""
            QLineEdit {
                background-color: #2f2f2f;
                color: white;
                border: 3px;
                padding: 5px;
                font-size: 21px;                                            
            }
        """)

        self.set_size = QPushButton("size", self.search_bar_widget)
        self.set_size.setCursor(Qt.PointingHandCursor)
        self.set_size.setMinimumHeight(30)
        self.set_size.setMinimumWidth(70)
        self.set_size.setMaximumWidth(170)
        self.set_size.setStyleSheet(self.theme.buttons)
        self.search_bar_widget_layout.addWidget(self.set_size)
        self.set_size.clicked.connect(self.image_manager.set_image_size)

        self.search_bar_widget_layout.addWidget(self.search_bar.text_box)
        add_tag_button.clicked.connect(self.open_tag_window)
        
        self.bottom_bar = QWidget(self.central_widget)
        self.bottom_bar.setMinimumHeight(30)
        self.bottom_bar.setMaximumHeight(50)
        self.bottom_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bottom_bar.setObjectName("bottomBar")
        self.bottom_bar.setStyleSheet(self.theme.widgets_next)
        grid_layout.addWidget(self.bottom_bar, 2, 1)

        self.bottom_bar_layout = QHBoxLayout(self.bottom_bar)
        self.bottom_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_bar_layout.setSpacing(0)

        self.bottom_bar_area = QWidget(self.bottom_bar)
        self.bottom_bar_area.setStyleSheet(self.theme.widgets_next)

        self.bottom_bar_area_layout = QHBoxLayout(self.bottom_bar_area)
        self.bottom_bar_area_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_bar_area_layout.setSpacing(0)
        self.bottom_bar_layout.addWidget(self.bottom_bar_area, alignment=Qt.AlignCenter)

        self.page_count_area = QWidget(self.bottom_bar_area)
        self.page_count_area.setStyleSheet(self.theme.ui)  
        self.page_count_area.setMaximumWidth(600)
        self.page_count_area.setMinimumHeight(20)
        self.bottom_bar_area_layout.addWidget(self.page_count_area, alignment=Qt.AlignCenter)

        self.page_count_area_layout = QHBoxLayout(self.page_count_area)
        self.page_count_area_layout.setContentsMargins(0, 0, 0, 0)
        self.page_count_area_layout.setSpacing(25) 

        self.first_page = QPushButton("<<", self.page_count_area)
        self.first_page.setStyleSheet(self.theme.buttons)       
        self.page_count_area_layout.addWidget(self.first_page, alignment=Qt.AlignLeft)
        self.first_page.clicked.connect(self.image_manager.skip_to_previous)

        self.previous_page =  QPushButton("<", self.page_count_area)
        self.previous_page.setStyleSheet(self.theme.buttons)       
        self.previous_page.setCursor(Qt.PointingHandCursor)
        self.page_count_area_layout.addWidget(self.previous_page, alignment=Qt.AlignLeft)
        self.previous_page.clicked.connect(self.image_manager.previous_page)

        self.page_count =  QLabel("", self.page_count_area)
        self.page_count.setStyleSheet(self.theme.buttons)       
        self.page_count.setMinimumWidth(100)
        self.page_count_area_layout.addWidget(self.page_count, alignment=Qt.AlignCenter)
        self.image_manager.set_page_count(self.page_count)

        self.next_page =  QPushButton(">", self.page_count_area)
        self.next_page.setStyleSheet(self.theme.buttons)       
        self.next_page.setCursor(Qt.PointingHandCursor)
        self.page_count_area_layout.addWidget(self.next_page, alignment=Qt.AlignRight)
        self.next_page.clicked.connect(self.image_manager.next_page)

        self.last_page =  QPushButton(">>", self.page_count_area)
        self.last_page.setStyleSheet(self.theme.buttons)       
        self.last_page.setCursor(Qt.PointingHandCursor)
        self.page_count_area_layout.addWidget(self.last_page, alignment=Qt.AlignRight)
        self.last_page.clicked.connect(self.image_manager.skip_to_last)

        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 20)
        grid_layout.setRowStretch(2, 1)

        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 3)
        self.close()

        self.installEventFilter(self)

    def open_profile_config(self):
        self.profile.show()
        self.profile.set_style()
    
    def create_menu(self):
        menu = QMenu()

        newest = QAction("newest", self)
        newest.triggered.connect(lambda: self.update_name("newest "))
        menu.addAction(newest)

        oldest = QAction("oldest", self)
        oldest.triggered.connect(lambda: self.update_name("oldest "))
        menu.addAction(oldest)

        recent = QAction("recent", self)
        recent.triggered.connect(lambda: self.update_name("recent "))
        menu.addAction(recent)

        a_to_z = QAction("a-z", self)
        a_to_z.triggered.connect(lambda: self.update_name("a-z "))
        menu.addAction(a_to_z)

        category = QAction("category ", self)
        category.triggered.connect(lambda: self.update_name("category "))
        menu.addAction(category)

        color = QMenu("color ", menu)
        color.addAction("Subitem 2-1")
        color.addAction("Subitem 2-2")
        menu.addMenu(color)

        return menu
    
    def update_name(self, option):
        self.sort_button.setText(f"sort by: {option}")
        self.new_tag_list.sort_option(option)
        self.new_tag_list.new_sort()

 
    def load_profile(self): 
        self.new_tag_list.load_new_profile() #might be temporary, move or refractor

        if self.tag_manager is not None:
            self.tag_manager.load_new_profile()
     
    
    def open_tag_window(self):
        try:
    
            self.tag_manager = TagManager(self.new_tag_list, self.booru_db)
            
            self.import_entities = ImportEntities(tag_manager=self.tag_manager)
            self.tag_manager.import_entities = self.import_entities

            self.tag_manager_categories = TMCategories(tag_manager=self.tag_manager,
                                                        booru_db=self.booru_db)
            
            self.tag_manager.tag_manager_categories = self.tag_manager_categories

            self.tag_manager.show()
        except Exception as e:
            print(e)
       
    def resizeEvent(self, event):
      
        self.search_bar.close()
        super().resizeEvent(event)
    
    def moveEvent(self, event):
        self.search_bar.close()

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
            self.image_manager.copy_media()

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_A:
            self.image_manager.ctrl_a()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
         {
            background-color: #112233;
            color: white;
            border: 1px solid white;
            border-radius: 15px;
            padding: 5px;
            opacity: 200;
        }
                      
    """)
    window = MainWindow()
    window.show()

    window.load_info()
    sys.exit(app.exec_())

    

if __name__ == "__main__":
    main()

