from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QDialog, QPushButton, QLabel, QListView, QSizePolicy)
from PyQt5.QtGui import QFont, QFont, QFont, QFontMetrics
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from media_properties.search_proxy import ItemDelegate, ItemModel, FilterProxy

import json
import os
import sqlite3

class TagList(QObject):
    def __init__(self, booru_db, new_tag_list=None, search_bar=None):
        super().__init__()

        self.new_tag_list = new_tag_list
        self.search_bar = search_bar
        self.booru_db = booru_db

        self.tag_list = {}

        self.categories = ["character", "artist", "series"]
   
        self.current_user = None
        self.option = "newest "
        self.not_name = False

        
    

    def update_filter_and_sort(self, text):
        self.proxy_model.setFilterRegExp(text)
        self.proxy_model.sort(0, Qt.AscendingOrder)

    def sort_option(self, option):

        self.option = option

    def load_new_tag_buttons(self):
        self.category = False

        self.tag_list = self.booru_db.get_tag_info()

        self.search_bar.load_tag_list(self.tag_list)
        self.load_proxy()


    def refresh_list(self):
        self.model.refresh(self.tag_list)


    def load_new_profile(self):
        self.tag_list = self.booru_db.get_tag_info()
        self.refresh_list()



    def new_sort(self):
      
        match self.option:
            case "newest ":
                pass
            case "oldest ":
                self.tag_list = dict(reversed(self.tag_list.items()))
               
            case "a-z ":
                self.tag_list = dict(sorted(self.tag_list.items()))
            case "category ":

                self.category = True
                category_name = self.categories[0]
             

                self.category_widget = QWidget()
                self.category_widget_layout = QVBoxLayout(self.category_widget)
                self.category_widget_layout.setContentsMargins(0, 0, 0, 0)

                tag_button_widget = QLabel(category_name)
                tag_button_widget.setMinimumHeight(34)
                tag_button_widget.setStyleSheet("background-color: purple")


                self.category_widget_layout.insertWidget(0, tag_button_widget)
                self.new_tag_list.insertWidget(0, self.category_widget)

                self.category_search_widget = QWidget()
                self.category_search_widget_layout = QVBoxLayout(self.category_search_widget)
                self.category_search_widget_layout.setContentsMargins(0, 0, 0, 0)

                sorted_by_color = dict(
                                        sorted(self.tag_list.items(), key=lambda item: item[1]["color"])
                                    )
                
                print(f"sorted by color{sorted_by_color}")

        self.model = ItemModel(self.tag_list)

        self.proxy_model = FilterProxy()
        self.proxy_model.setSourceModel(self.model)
        #self.proxy_model.sort(0, Qt.AscendingOrder)#alphabetical

      
        self.list_view.setModel(self.proxy_model)

    
            


    def load_proxy(self):

        self.model = ItemModel(self.tag_list)

        self.proxy_model = FilterProxy()
        self.proxy_model.setSourceModel(self.model)
        #self.proxy_model.sort(0, Qt.AscendingOrder)#alphabetical

        self.list_view = QListView()
        self.list_view.setModel(self.proxy_model)

        delegate = ItemDelegate(show_buttons=True)
        delegate.tagModified.connect(self.tag_input)

        self.list_view.setItemDelegate(delegate) 
        self.list_view.viewport().installEventFilter(delegate) 
        self.list_view.setMouseTracking(True)
        self.list_view.setSelectionMode(QListView.SingleSelection)
        self.list_view.setSelectionBehavior(QListView.SelectRows)
        self.list_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
      
        self.new_tag_list.addWidget(self.list_view, stretch=19)
        self.new_tag_list.addStretch()
     
        

    def tag_input(self, tag_name, delta):

        if delta == 0:


            self.search_bar.insert_tag_name(tag_name)

        elif delta == 1:
            self.search_bar.add_to_search_bar(tag_name)

        elif delta == -1:
            self.search_bar.add_to_search_bar(tag_name)
        
        


       


        """count = 0

        LIMIT = 499

        for tag_name, data in self.tag_list.items():
         
            if count >= LIMIT:
                break

            count += 1
            tag_color = data["color"]
            entity_count = data["count"]

            tag_button = TagButtons(
            tag_name=tag_name,
            tag_color=tag_color,
            entity_count=entity_count,
            search_bar=self.search_bar
            )

            if self.category == True:
                self.category_widget_layout.addWidget(tag_button)
                
            else:

                self.new_tag_list.insertWidget(0, tag_button)"""

            

class TagButtons(QWidget):
    def __init__(self, tag_name, tag_color, 
                 entity_count, search_bar):
        
        super().__init__()

        self.search_bar = search_bar
        self.font = QFont('Roboto')

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        tag_button_widget = QWidget()
        tag_button_widget.setFixedHeight(38)
        tag_button_widget.setStyleSheet(
                                        "background-color: #112233")
    
        tag_button_layout = QHBoxLayout()
        tag_button_layout.setContentsMargins(0,0,0,5)
        tag_button_widget.setLayout(tag_button_layout)

        import_pics = QPushButton("+")
        import_pics.setFont(self.font)
        import_pics.clicked.connect(lambda checked=False, t=tag_name: self.search_bar.add_to_search_bar(t))
        import_pics.setCursor(Qt.PointingHandCursor)
        import_pics.setMinimumWidth(20)
        import_pics.setStyleSheet(f"QPushButton {{ color: {tag_color}; background-color: #112233; border: none; font-size: 29px; }} QPushButton:hover {{ color: #00FFFF; }}")
        tag_button_layout.addWidget(import_pics, alignment=Qt.AlignLeft)

        import_pics = QPushButton("-")
        import_pics.setFont(self.font)
        import_pics.clicked.connect(lambda checked=False, t=tag_name: self.search_bar.add_to_search_bar(t))
        import_pics.setCursor(Qt.PointingHandCursor)
        import_pics.setMinimumWidth(20)
        import_pics.setStyleSheet(f"QPushButton {{ color: {tag_color}; background-color: #112233; border: none; font-size: 29px; }} QPushButton:hover {{ color: #00FFFF; }}")
        tag_button_layout.addWidget(import_pics, alignment=Qt.AlignLeft)

        tag_button = QPushButton(tag_name)
        tag_button.setCursor(Qt.PointingHandCursor)
        tag_button.setFont(self.font)
        tag_button.setFixedHeight(34)
        tag_button.setFixedWidth(220)

        metrics = QFontMetrics(tag_button.font())
        elided_text = metrics.elidedText(tag_name, Qt.ElideRight, tag_button.width() - 50)
        tag_button.setText(elided_text)
        tag_button.setStyleSheet(f"""
                            QPushButton {{
                                color: {tag_color};
                                background-color: #112233;
                                border: none;
                                max-width: 100px;
                                text-align: left;
                                font-size: 25px;
                            }}
                            QPushButton:hover {{
                                color: #00FFFF;
                            }}
                        """)

        tag_button_layout.addWidget(tag_button, alignment=Qt.AlignLeft)
        tag_button_layout.addStretch()
                
        tag_button.clicked.connect(lambda checked=False, t=tag_name: self.search_bar.insert_tag_name(t))


        if entity_count >= 1000:
                entity_display = f"{entity_count / 1000:.1f}k"
        else: 
            entity_display = entity_count

        tag_entity_count = QLabel(str(entity_display))
        tag_entity_count.setFont(self.font)
        tag_entity_count.setMinimumWidth(15)
        tag_entity_count.setFixedHeight(40)
        tag_entity_count.setStyleSheet("color: #B0B0B0; background-color: #112233; border: none; font-size: 23px; }")
        tag_button_layout.addWidget(tag_entity_count, alignment=Qt.AlignRight)

        outer_layout.addWidget(tag_button_widget)

            

         

    
                 
    