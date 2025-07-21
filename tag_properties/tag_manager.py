from PyQt5.QtWidgets import (QVBoxLayout, QDialog, QDesktopWidget, QToolButton, QMessageBox,
                             QMenu, QAction, QPushButton, QStackedLayout, QTabWidget, QListView, 
                             QHBoxLayout, QLineEdit, QWidget, QSizePolicy, QColorDialog, QLayout, QListWidget, QListWidgetItem, QTableView, QAbstractItemView)

from PyQt5.QtGui import (QFont, QColor, QPainter, QPen, QFontMetrics, QPixmap, QPalette, QBrush)

from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QSize, QSortFilterProxyModel, QAbstractListModel, QVariant, QModelIndex, QEvent


from media_properties.search_proxy import ItemDelegate, ItemModel, FilterProxy
from config.profile_config import CategoryManager

from tag_properties.tagbox import TagBox

from collections import defaultdict



#$env:PYTHONFAULTHANDLER=1 python main.py



class TagManager(QDialog):
    def __init__(self, new_tag_list, db, parent=None):
        super().__init__(parent)

       
        self.booru_db = db
        self.new_tag_list = new_tag_list


        self.option = 1 #DELETE LATER====================

        self.font = QFont('Roboto')

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self.setWindowTitle(f"tag manager - 0 items")
      
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        window_width = int(screen_width * 0.35)
        window_height = int(window_width)

        self.setGeometry(
            (screen_width - window_width) // 2,
            (screen_height - window_height) // 2,
            window_width,
            window_height
        )

        min_height = int(window_height * 0.60)
      

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        self.setMinimumHeight(min_height)
      
        self.stacked_layout = QStackedLayout()
        self.setLayout(self.stacked_layout)

        self.left_widget = QWidget()
        self.left_widget.setMinimumWidth(250)
        self.left_widget.setStyleSheet("background-color: #112233;")
        self.left_widget.setMaximumWidth(350)
        main_layout.addWidget(self.left_widget, stretch=5)

        self.left_widget_layout = QVBoxLayout()
        self.left_widget.setLayout(self.left_widget_layout)
        self.left_widget_layout.setContentsMargins(2,2,2,2)


        self.search_bar = QWidget()
        self.search_bar.setMinimumHeight(30)
        self.search_bar.setStyleSheet("background-color: orange")

        self.left_widget_layout.addWidget(self.search_bar, stretch=1)

        self.right_widget = QTabWidget()
        self.right_widget.setMinimumWidth(250)
        self.right_widget.setStyleSheet("background-color: black;")
        main_layout.addWidget(self.right_widget, stretch=11)
        self.right_widget.setStyleSheet("""
                QTabWidget::pane {
                    background: #112233;
                }

                QTabBar::tab {
                    margin-right: 3px;
                    background: #2e4053;
                    color: white;
                    padding: 12px;
                    border: 3px solid #223344;
             
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    border-bottom-left-radius: 8px;
                    border-bottom-right-radius: 8px;
                }

                QTabBar::tab:selected {
                    background: #1f618d;
                    color: white;
                    
                }

                QTabBar::tab:hover {
                    background: #34495e;
                }
            """)


        self.load_list()
        self.load_proxy()

        self.tag_pairs = self.booru_db.load_group()

        self.tag_group_list = {child: parent for parent, child in self.tag_pairs}


        print(self.tag_group_list)
      

        


        self.tag_tab_box = TagBox(self.booru_db, taglist=self.tag_list, tm=self, s=0)
        self.tag_tab_box.tag_box_entry.setFocus()

        self.test = True #TEMPORARRY
        self.tab_name = "tags"

    def set_curr_source(self, source):
        self.curr_source = source

        if source is 1:
            self.tag_group_top_box.tag_window_widget.setStyleSheet("background-color: #0d1117; border: 2px solid white; border-radius: 20px;")
            self.tag_group_bottom_box.tag_window_widget.setStyleSheet("background-color: #0d1117; border: 2px solid #1f618d; border-radius: 20px;")

        if source is 2:
            
            self.tag_group_top_box.tag_window_widget.setStyleSheet("background-color: #0d1117; border: 2px solid #1f618d; border-radius: 20px;")
            self.tag_group_bottom_box.tag_window_widget.setStyleSheet("background-color: #0d1117; border: 2px solid white; border-radius: 20px;")
            


        print(self.curr_source)
      
    
    def change_page(self, index):
        self.tab_name = self.right_widget.tabText(index)
     
        if self.tab_name == "tags":
            
                self.list_view.show()
                self.search_bar.show()
                self.tag_tab_box.tag_box_entry.setFocus()

                #self.tag_categories.hide_page()
                #self.tag_groups.hide_page()
            
                
        
        if self.tab_name == "categories":
        
                self.list_view.hide()
                self.search_bar.hide()

               
                
                self.tag_categories.show_page()
                #self.tag_groups.hide_page()
            
        


        if self.tab_name == "groups":
            if self.test is True: #TEMPORARRY
                try:
                    self.list_view.show()
                    self.search_bar.show()

                    self.curr_source = 1



                    self.tag_group_top_box = TagBox(self.booru_db, taglist=self.tag_list, tm=self, s=1)
                    self.tag_group_top_box.tag_window_widget.setStyleSheet("background-color: #0d1117; border: 2px solid white; border-radius: 20px;")
                    
                    self.tag_group_bottom_box = TagBox(self.booru_db, taglist=self.tag_list, tm=self, s=2)

                    self.tag_group_top_box.tag_box_entry.setFocus()

                    self.tag_groups.show_page()              
                    #self.tag_categories.hide_page()
                    self.test = False

                except:
                    pass



    #==vvvvvvvvv====== temporary, redo later ===vvvvvvvv===

    def refresh_tag_list(self): #VERY TEMPORARY PLEASE JUST LOOP THROUGH LIST AND SET MODEL AGAIN. I DID THIS AD MIDNIGHT YESTERDAY
        self.booru_db.refresh_tag_info()
        self.load_new_profile()
        
        self.new_tag_list.refresh_list()

    def load_list(self):
        self.tag_list = self.booru_db.get_tag_info()
    def refresh_model(self):
        self.model.refresh(self.tag_list)
       

    def load_new_profile(self):
        self.load_list()
        self.refresh_model()
        
   #==^^^^^^^====== temporary, redo later ===^^^^^^^===

    def load_proxy(self):
        
        self.model = ItemModel(self.tag_list)

        self.proxy_model = FilterProxy()
        self.proxy_model.setSourceModel(self.model)
        #self.proxy_model.sort(0, Qt.AscendingOrder)#alphabetical

        self.list_view = QListView()
        self.list_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.list_view.clicked.connect(self.tag_window.get_tag_from_list)
        self.list_view.setStyleSheet("""
                                        QScrollBar:vertical {
                                            background: #1e1e2f;
                                            width: 10px;
                                            margin: 0px 0px 0px 0px;
                                        }

                                        QScrollBar::handle:vertical {
                                            background: #5c7aff;
                                            min-height: 20px;
                                            border-radius: 5px;
                                        }

                                        QScrollBar::add-line:vertical,
                                        QScrollBar::sub-line:vertical {
                                            background: none;
                                            height: 0px;
                                        }

                                        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                                            background: none;
                                        }

                                        QScrollBar:horizontal {
                                            background: #1e1e2f;
                                            height: 10px;
                                        }

                                        QScrollBar::handle:horizontal {
                                            background: #5c7aff;
                                            min-width: 20px;
                                            border-radius: 5px;
                                        }

                                        QScrollBar::add-line:horizontal,
                                        QScrollBar::sub-line:horizontal {
                                            background: none;
                                            width: 0px;
                                        }

                                        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                                            background: none;
                                        }
                                    """)

      
        self.left_widget_layout.addWidget(self.list_view, stretch=19)
        self.left_widget_layout.addStretch()

        QTimer.singleShot(0, self.set_model)

    def set_model(self):

        self.list_view.setModel(self.proxy_model)
        self.list_view.setItemDelegate(ItemDelegate(show_buttons=False))

        self.tag_tab_box.tag_box_entry.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.proxy_model.sort(0, Qt.AscendingOrder)
        
        self.tag_tab_box.tag_box_entry.textChanged.connect(self.update_filter_and_sort)

        self.list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list_view.clicked.connect(self.insert_tag_from_list)

    def update_filter_and_sort(self, text):
        self.proxy_model.setFilterRegExp(text)

    def insert_tag_from_list(self, index):
            
            if self.tab_name == "tags":
                self.tag_tab_box.get_tag_from_list(index)

            if self.tab_name == "groups":
                if self.curr_source == 1:
                    self.tag_group_top_box.get_tag_from_list(index)
                elif self.curr_source == 2:
                    self.tag_group_bottom_box.get_tag_from_list(index)


        
    def select_option(self, number):
        self.option = number
    
    def import_entities(self):
        #print(f"only new list {self.new_tags}")
        match self.option:

            case 1:

    

                if self.new_tags:

                    #print("WHAT?")

                    #print(f"only new list {self.new_tags}")
                    self.booru_db.add_tags(self.new_tags)
                    self.new_tag_list.refresh_list()

                    #noting here, test later to see if loading this while importnig photos will crash if it loads twice

                    self.load_list()
                    self.refresh_model()

                if self.import_entity_count != 0:

                    import_tag_list = [tag_name[0] for tag_name in self.tag_box_list.keys()]

                    self.import_entities.retrieve_tag_list(import_tag_list)


                else:

                    for i in range(len(self.tag_box_list)):
                        self.remove_last()
                    self.tag_box_list.clear()

    """def update_import_stats(self):

        self.import_entity_count = self.import_entities.retrieve_import_length()

        #this is the one actually importing to db
        self.new_tags = [(tag_name, cat_name) for (tag_name, cat_name) in self.tag_box_list.keys() if (tag_name, cat_name) not in self.tag_list] 
        
        new_tag_count = len([tag_name for (tag_name, _) in self.tag_box_list.keys() if tag_name not in self.tag_list])

        total_tags = len(self.tag_box_list)

        if total_tags and self.import_entity_count > 0:
            self.setWindowTitle(f"tag manager - add {self.import_entity_count} item{'s' if self.import_entity_count != 1 else ''} to {total_tags} tag{'s' if total_tags != 1 else ''}{f' ({new_tag_count} new)' if new_tag_count != 0 else ''}")
        elif new_tag_count > 0:
            self.setWindowTitle(f"tag manager - add {new_tag_count} new tag{'s' if new_tag_count != 1 else ''}")
        elif self.import_entity_count >= 0:
            self.setWindowTitle(f"tag manager - {self.import_entity_count} item{'s' if self.import_entity_count != 1 else ''}")"""

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape ignored — not closing dialog")
            event.ignore()  # Block closing
        else:
            super().keyPressEvent(event)