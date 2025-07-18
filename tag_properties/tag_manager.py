from PyQt5.QtWidgets import (QVBoxLayout, QDialog, QDesktopWidget, QToolButton, QMessageBox,
                             QMenu, QAction, QPushButton, QStackedLayout, QTabWidget, QListView, 
                             QHBoxLayout, QLineEdit, QWidget, QSizePolicy, QColorDialog, QLayout, QListWidget, QListWidgetItem, QTableView, QAbstractItemView)

from PyQt5.QtGui import (QFont, QColor, QPainter, QPen, QFontMetrics, QPixmap, QPalette, QBrush)

from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QSize, QSortFilterProxyModel, QAbstractListModel, QVariant, QModelIndex, QEvent

from media_properties.search_proxy import ItemDelegate, ItemModel, FilterProxy
from config.profile_config import CategoryManager



#$env:PYTHONFAULTHANDLER=1 python main.py



class TagManager(QDialog):
    def __init__(self, new_tag_list, booru_db, parent=None):
        super().__init__(parent)

       
        self.booru_db = booru_db
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

       

        self.tag_page = QWidget()
        self.tag_page.setMinimumHeight(100)
   
        self.tag_page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tag_page_layout = QVBoxLayout(self.tag_page)
        self.tag_page_layout.setContentsMargins(0,10,0,0)

        self.tag_page_layout.addStretch()

        self.right_widget.addTab(self.tag_page, "tags")

        self.tag_window_widget = QWidget()
        self.tag_window_widget.setMinimumHeight(100)
        self.tag_window_widget.setStyleSheet("background-color: #0d1117; border: 2px solid #1f618d; border-radius: 20px;")
        self.tag_window_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tag_window_widget_layout = QHBoxLayout(self.tag_window_widget)
        self.tag_window_widget_layout.setContentsMargins(10,15,10,10)

        self.tag_page_layout.addWidget(self.tag_window_widget, stretch=12)
        
        self.tag_window = QWidget() #actual widget where tags get put in
        self.tag_window.setMinimumHeight(100)
        self.tag_window.setStyleSheet("background-color: #0d1117; border: none;")
        self.tag_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tag_window_widget_layout.addWidget(self.tag_window, stretch=5)


        self.category_list_panel = QWidget()
        self.category_list_panel.setMinimumHeight(100)
        self.category_list_panel.setMinimumWidth(120)
        self.category_list_panel.setStyleSheet("background-color: #112233; border: none;")
        self.category_list_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tag_window_widget_layout.addWidget(self.category_list_panel, stretch=1)

        self.category_list_panel_layout = QHBoxLayout(self.category_list_panel)



        self.flow_layout = FlowLayout()
        self.tag_window.setLayout(self.flow_layout)

        import_widget = QWidget()
        import_widget.setMinimumHeight(70)
        import_widget.setMaximumHeight(90)
        import_widget.setStyleSheet("background-color: none;")
        import_widget_layout = QHBoxLayout(import_widget)

        clear_tag_box = QPushButton("-")
        clear_tag_box.setCursor(Qt.PointingHandCursor)
        clear_tag_box.setFixedSize(60,60)
        clear_tag_box.setStyleSheet("background-color: purple;")
        clear_tag_box.clicked.connect(self.clear_tag_box)
        import_widget_layout.addWidget(clear_tag_box, Qt.AlignLeft)

        import_entities = QPushButton("+")
        import_entities.setMinimumWidth(60)
        import_entities.setMinimumHeight(60)
        import_entities.setCursor(Qt.PointingHandCursor)
        import_entities.setStyleSheet("QPushButton { font-size: 40px; background-color: #444; color: white; border: 2px solid #888; border-radius: 8px; } QPushButton:hover { background-color: #666; }")
        import_entities.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        import_widget_layout.addWidget(import_entities, Qt.AlignCenter)
        import_entities.clicked.connect(self.import_entities)

        
        delete_button = QPushButton("-")
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.setFixedSize(60,60)
        delete_button.setStyleSheet("QPushButton { font-size: 40px; background-color: red; color: white; border: 2px solid #888; border-radius: 8px; } QPushButton:hover { background-color: red; }")
        import_widget_layout.addWidget(delete_button, Qt.AlignRight)
        delete_button.clicked.connect(self.delete_tags)

        self.tag_page_layout.addWidget(import_widget, stretch=3)

        groups_page = QWidget()
        groups_page.setMinimumHeight(100)
        groups_page.setStyleSheet("background-color: cyan; border: none;")
        groups_page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        groups_page_layout = QVBoxLayout(self.tag_page)
        groups_page_layout.setContentsMargins(5,5,5,5)
        groups_page_layout.addStretch()

        self.right_widget.addTab(groups_page, "groups")
        self.right_widget.currentChanged.connect(self.change_page)

        self.tag_widget = QWidget()
        self.tag_widget.setMinimumHeight(40)
        self.tag_widget.setMaximumHeight(70)
        self.tag_widget.setStyleSheet("background-color: #112233;")
        self.tag_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tag_widget_layout = QHBoxLayout(self.tag_widget)
        self.tag_widget_layout.setContentsMargins(0, 0, 0, 0)
      
       

        self.import_entity_count = 0

        self.new_tags = []
        self.tag_list = {} #name, color, count, etc
        self.tag_box_list = {} #tags in box

        self.tag_color = "#FFFFFF"
        self.category_name = "tags"

        self.load_list()

        self.tag_box_entry = TagEntry()
        self.flow_layout.addWidget(self.tag_box_entry)
        self.tag_box_entry.setFocus()

        

        

        self.load_cat_list()

        self.load_proxy()


    def set_category(self, name, color):
        self.tag_color = color
        self.category_name = name

        self.tag_box_entry.set_color(self.tag_color)
        

    #==vvvvvvvvv====== temporary, redo later ===vvvvvvvv===

    def load_cat_list(self):
        self.category_info = self.booru_db.get_category_info()
        self.widget = CategoryList(self.category_info, tag_manager=self)
        self.category_list_panel_layout.addWidget(self.widget)


    def update_list_color(self, name, color):  #list on right side
        self.widget.deleteLater()
        self.load_cat_list()
        
        if self.tag_box_list:
            for (_,  cat_name), icon in self.tag_box_list.items():
                if name == cat_name:
                    icon.update_color(color)

        self.refresh_tag_list()
        

    def refresh_tag_list(self): #VERY TEMPORARY PLEASE JUST LOOP THROUGH LIST AND SET MODEL AGAIN. I DID THIS AD MIDNIGHT YESTERDAY
        self.booru_db.refresh_tag_info()
        self.load_new_profile()
        
        self.new_tag_list.refresh_list()


    def refresh_category_right_list(self):
        self.widget.deleteLater()
        self.load_cat_list()
            

    def load_list(self):

        self.tag_list = self.booru_db.get_tag_info()
    def refresh_model(self):
        self.model.refresh(self.tag_list)
       

    def load_new_profile(self):
        self.load_list()
        self.refresh_model()
        
   #==^^^^^^^====== temporary, redo later ===^^^^^^^===

    def add_tagd(self, tag_name, tag_color, cat_name):
            
            category_name = cat_name
            
            self.flow_layout.removeWidget(self.tag_box_entry)

            self.tag_icons = TagIcon(name=tag_name, cat_name=cat_name,
                                     color=tag_color, restore=self.restore_tag)
            
            self.tag_box_list[tag_name, category_name] = self.tag_icons

            if len(self.tag_box_list) < 100:
            
                self.flow_layout.addWidget(self.tag_icons)

    def add_back_text_box_entry(self):

        self.flow_layout.addWidget(self.tag_box_entry)  
        self.tag_box_entry.clear()
        self.tag_box_entry.setFocus()

        self.update_import_stats()

    def tag_filter(self):
    
        current_text = self.tag_box_entry.text().lower()
        split_text = current_text.split()

        if len(split_text) > 1:

                for words in split_text:
                
                    self.tag_check(words, self.category_name)    #change this later

                self.add_back_text_box_entry()
                self.tag_box_entry.clear()

    def tag_check(self, tag_name, category_name):

        name = tag_name.lower().replace("_"," ")
        tag_name = name

        if (tag_name, self.category_name) not in self.tag_box_list:

            color = self.tag_color
            self.add_tagd(tag_name, color, category_name)

    def delete_tags(self):
        if self.tag_box_list:

            delete_list = [tag_name for (tag_name, _) in self.tag_box_list]
            self.booru_db.delete_tags(delete_list)

        for i in range(len(self.tag_box_list)):
            self.remove_last()
        self.tag_box_list.clear()

        self.refresh_tag_list()

    def clear_tag_box(self):
        for i in range(len(self.tag_box_list)):
            self.remove_last()
        self.tag_box_list.clear()

        self.new_tags.clear()
        self.update_import_stats()

    def get_tag_from_list(self, index):
     
        self.item = index.data(Qt.UserRole)

        tag_name = self.item["name"]
        tag_color = self.item["color"]
        category_name = self.item["category"]

        if (tag_name, category_name) not in self.tag_box_list:
            self.add_tagd(tag_name, tag_color, category_name)

        self.add_back_text_box_entry()
        self.update_import_stats()

    def restore_tag(self, tag_name, cat_name, widget):
    
        self.flow_layout.removeWidget(widget)
        widget.deleteLater()

        del self.tag_box_list[(tag_name, cat_name)]

        self.flow_layout.update()
        self.tag_box_entry.clear()
        self.tag_box_entry.setFocus()

    def remove_last(self):
        if self.tag_box_list:
            last_item = list(self.tag_box_list.keys())[-1] 
            last_widget = self.tag_box_list[last_item]

            name, cat_name = last_item 

            self.restore_tag(name, cat_name, last_widget)
            self.update_import_stats()

            
            

    def load_proxy(self):
        
        self.model = ItemModel(self.tag_list)

        self.proxy_model = FilterProxy()
        self.proxy_model.setSourceModel(self.model)
        #self.proxy_model.sort(0, Qt.AscendingOrder)#alphabetical

        self.list_view = QListView()
        self.list_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list_view.clicked.connect(self.get_tag_from_list)
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

        self.tag_box_entry.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.proxy_model.sort(0, Qt.AscendingOrder)
        
        self.tag_box_entry.textChanged.connect(self.update_filter_and_sort)
        self.tag_box_entry.textChanged.connect(self.tag_filter)

        self.tag_box_entry.installEventFilter(self)
        self.tag_window.installEventFilter(self)
    
        self.list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_view.setSelectionBehavior(QAbstractItemView.SelectRows)

    def update_filter_and_sort(self, text):
        self.proxy_model.setFilterRegExp(text)
        
        
    def eventFilter(self, obj, event):
        if obj == self.tag_box_entry:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Space:
                    
                    if self.tag_box_entry.text().strip():
                        tag_name = self.tag_box_entry.text()

                        self.tag_check(tag_name, self.category_name)
                        self.add_back_text_box_entry()

                        #print(f" {tag_name, self.category_name}")

                    else:
                        self.tag_box_entry.clear()

                    return True
                
                elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Tab:
                    model = self.list_view.model()
                    if model and model.rowCount() > 0:
                    
                        index = self.list_view.model().index(0, 0)
                        self.item = index.data(Qt.UserRole)
                        self.get_tag_from_list(index)

                    return True

                if event.key() == Qt.Key_Backspace:
                    if not self.tag_box_entry.text().strip(): 
                            self.remove_last()
                            
                
        elif obj == self.tag_window:
            if event.type() == QEvent.Enter:
          
                self.setCursor(Qt.IBeamCursor)
            elif event.type() == QEvent.Leave:
                self.setCursor(Qt.ArrowCursor)

            if event.type() == QEvent.MouseButtonPress:
                self.tag_box_entry.setFocus()
                
                return True
        return super().eventFilter(obj, event)



    def select_option(self, number):
        self.option = number

        if self.option == 1:
            self.button3.show()
            self.button4.show()
        else:
            self.button3.hide()
            self.button4.hide()

     
        #1: add tag       #4: edit tag       #7: delete tag
        #2: add category  #5: edit category  #8: delete category
        #3: add group     #6: edit group     #9: delete group

    
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

    def update_import_stats(self):

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
            self.setWindowTitle(f"tag manager - {self.import_entity_count} item{'s' if self.import_entity_count != 1 else ''}")

    def change_page(self, index):
        tab_name = self.right_widget.tabText(index)
     
        if tab_name == "tags":
            self.list_view.show()
            self.search_bar.show()
            self.tag_manager_categories.hide_page()
        
        if tab_name == "categories":
            self.list_view.hide()
            self.search_bar.hide()
            
            self.tag_manager_categories.show_page()


        if tab_name == "groups":
            self.list_view.show()
            self.search_bar.show()
            try:
                self.tag_manager_categories.hide_page()
            except:
                pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape ignored — not closing dialog")
            event.ignore()  # Block closing
        else:
            super().keyPressEvent(event)

class TagIcon(QPushButton):
    def __init__(self, name, cat_name, color, restore):

        tag_name = name
        tag_color = color
        super().__init__(f"{tag_name} x")
        restore_tag = restore 
        self.update_color(tag_color)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda checked, tag_name=tag_name, category_name=cat_name, widget=self: restore_tag(tag_name, category_name, widget))

    def update_color(self, tag_color):

        self.setStyleSheet(f"""
        background-color: #2C3539;
        color: {tag_color};
        border-radius: 6px;
        font-size: 20px;
        padding: 6px 10px;
        margin-left: -5px
    """)

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=5):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.item_list = []

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.item_list):
            return self.item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.item_list:
            widget = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX

            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()
    
    
class TagEntry(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(100)
      
        self.setPlaceholderText("ex: travel")
            
        self.setFixedHeight(34)  
        self.setMinimumWidth(200)
        self.setStyleSheet(f"""
                QLineEdit {{
                    background-color: #0d1117;
                    color: "white";                 
                    border: none;
                    
                }}
            """)
        

        palette = self.palette()
        palette.setColor(QPalette.PlaceholderText, QColor(255, 255, 255, 120)) 
        self.setPalette(palette)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.textChanged.connect(self.adjust_width)

    def set_color(self, color):
        self.setStyleSheet(f"""
                QLineEdit {{
                    background-color: #0d1117;
                    color: {color};                 
                    border: none;
                    
                }}
            """)


    def adjust_width(self):
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.text()) + 20
      
        self.setFixedWidth(max(50, text_width))



class CategoryList(QListWidget):
    def __init__(self, categories, tag_manager):
        super().__init__()
        self.setSelectionMode(QListWidget.SingleSelection)

        self.tag_manager = tag_manager

        for name, font_color in categories.items():
            item = QListWidgetItem(name)
            item.setForeground(QColor(font_color))  
            self.insertItem(0, item)

        self.setStyleSheet("""
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: rgba(30, 144, 255, 80);  /* Semi-transparent blue */
            }
                                
        """)

    def update_list(self):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                name = item.text()
                color = item.foreground().color().name()
                self.tag_manager.set_category(name, color)

        super().mousePressEvent(event)
