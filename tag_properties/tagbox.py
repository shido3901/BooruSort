from PyQt5.QtWidgets import (QMessageBox, QCheckBox, QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, 
                             QWidget, QLayout, QSizePolicy, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QRect, QSize, QPoint, QEvent
from PyQt5.QtGui import QPalette, QColor

from collections import defaultdict

class TagBox(QWidget):
    def __init__(self, db, taglist, tm, s):
        super().__init__()

        #source
        #0 = tag_tab
        #1 = tag_group_top
        #2 = tag_group_bottom

        self.source = s
        self.tag_manager = tm

        self.tag_group_list = self.tag_manager.tag_group_list #parent -> child

        print(self.tag_group_list)

        self.booru_db = db
        self.list_view = self.tag_manager.list_view
        self.tag_list = taglist

        if self.source == 1:

            self.tag_pairs = self.tag_manager.tag_pairs
            
            self.parent_tag_list = defaultdict(list)
            for parent, child in self.tag_pairs:
                self.parent_tag_list[parent].append(child)

            print(self.parent_tag_list)

       

        self.tag_window_widget = QWidget()
        self.tag_window_widget.setMinimumHeight(100)
        self.tag_window_widget.setStyleSheet("background-color: #0d1117; border: 2px solid #1f618d; border-radius: 20px;")
        self.tag_window_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tag_window_widget_layout = QHBoxLayout(self.tag_window_widget)
        self.tag_window_widget_layout.setContentsMargins(10,15,10,10)
        
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

        self.tag_box_entry = TagEntry(tm=self.tag_manager, s=self.source)#QLineEdit
        self.flow_layout.addWidget(self.tag_box_entry)

        self.tag_window_widget.setMouseTracking(True)

        self.tag_window_widget.installEventFilter(self)
        self.tag_box_entry.installEventFilter(self)

     
        self.tag_box_list = {} #tags in box

        self.tag_color = "#FFFFFF"
        self.category_name = "tags"

      


        self.load_cat_list()

        self.initUI()#located at bottom



    #this part kina cancer ima re do this. Its functional but kina hard to read
    def add_tagd(self, tag_name, cat_name, tag_color):

        if tag_name in self.tag_group_list and self.source == 0:
            parent_tag_name = self.tag_group_list[tag_name]

            parent_cat_name = self.tag_list[parent_tag_name]["category"]
            color = self.tag_list[parent_tag_name]["color"]
            border_color = color

            if (parent_tag_name, parent_cat_name) not in self.tag_box_list:

                self.add_tag_widget_to_box(parent_tag_name, parent_cat_name, color, border_color)
        else:
            border_color = None

        if (tag_name, cat_name) not in self.tag_box_list:

        
            self.add_tag_widget_to_box(tag_name, cat_name, tag_color, border_color)

        if self.source == 1:

            if tag_name in self.parent_tag_list:
                
                child_tag_name_list = self.parent_tag_list[tag_name]
                for child_tag_name in child_tag_name_list:

                    child_cat_name = self.tag_list[child_tag_name]["category"]
                    color = self.tag_list[child_tag_name]["color"]

                    print(child_tag_name, child_cat_name, color)

                    self.tag_manager.tag_group_bottom_box.add_tagd(child_tag_name, child_cat_name, color)
                    self.tag_manager.tag_group_bottom_box.add_back_text_box_entry()

        
    def add_tag_widget_to_box(self, tag_name, cat_name, tag_color, border_color):

            
        self.flow_layout.removeWidget(self.tag_box_entry)

        self.tag_icons = TagIcon(name=tag_name, cat_name=cat_name, color=tag_color, restore=self.restore_tag, border_color=border_color)
        
        self.tag_box_list[tag_name, cat_name] = self.tag_icons

        if len(self.tag_box_list) < 100:
        
            self.flow_layout.addWidget(self.tag_icons)

    def add_back_text_box_entry(self):

        self.flow_layout.addWidget(self.tag_box_entry)  
        self.tag_box_entry.clear()
        self.tag_box_entry.setFocus()

        #self.update_import_stats()

    def refresh_category_right_list(self):
        self.widget.deleteLater()
        self.load_cat_list()

    def tag_filter(self):
    
        current_text = self.tag_box_entry.text().lower()
        split_text = current_text.split()

        if len(split_text) > 1:

            for words in split_text:
            
                self.tag_check(words, self.category_name)    #change this later

            self.add_back_text_box_entry()
            self.tag_box_entry.clear()

    def tag_check(self, tag_name, category_name,):

        name = tag_name.lower().replace("_"," ")
        tag_name = name

        if (tag_name, category_name) not in self.tag_box_list:

            color = self.tag_color
            self.add_tagd(tag_name, category_name, color)

    def delete_tags(self):
        if self.tag_box_list:

            delete_list = [tag_name for (tag_name, _) in self.tag_box_list]
            self.booru_db.delete_tags(delete_list)

            self.clear_tag_box()
        #self.tag_manager.refresh_tag_list()

    def clear_tag_box(self):
        for i in range(len(self.tag_box_list)):
            self.remove_last()
        self.tag_box_list.clear()
        #elf.update_import_stats()

        if self.source == 1:
            self.tag_manager.tag_group_bottom_box.clear_tag_box()

    def get_tag_from_list(self, index):
     
        self.item = index.data(Qt.UserRole)

        tag_name = self.item["name"]
        tag_color = self.item["color"]
        category_name = self.item["category"]

        if (tag_name, category_name) not in self.tag_box_list:
            self.add_tagd(tag_name, category_name, tag_color)

        self.add_back_text_box_entry()
        #self.update_import_stats()

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
            #self.update_import_stats()

    def eventFilter(self, obj, event):

        if obj == self.tag_box_entry:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Space:
                    
                    if self.tag_box_entry.text().strip():
                        tag_name = self.tag_box_entry.text()
                 
                        print(self.category_name)

                        self.tag_check(tag_name, self.category_name)
                        self.add_back_text_box_entry()

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

        elif obj == self.tag_window_widget:
            if event.type() == QEvent.Enter:
                self.tag_window_widget.setCursor(Qt.IBeamCursor)
               
                return True
            elif event.type() == QEvent.Leave:
                self.tag_window_widget.setCursor(Qt.ArrowCursor)
                return True
            elif event.type() == QEvent.MouseButtonPress:
                self.tag_box_entry.setFocus()
                return True
            
        return super().eventFilter(obj, event)
    
    def refresh_category_right_list(self):
        self.widget.deleteLater()
        self.load_cat_list()
    
    def load_cat_list(self):
        if self.source == 0 or self.source == 1:
            self.category_info = self.booru_db.get_category_info()
            self.widget = CategoryList(self.category_info, tag_box=self)
            self.category_list_panel_layout.addWidget(self.widget)


    def update_list_color(self, name, color):  #list on right side
        self.widget.deleteLater()
        self.load_cat_list()
        
        if self.tag_box_list:
            for (_,  cat_name), icon in self.tag_box_list.items():
                if name == cat_name:
                    icon.update_color(color)

        self.tag_manager.refresh_tag_list()

    def set_category(self, name, color):
        self.tag_color = color
        self.category_name = name

        self.tag_box_entry.set_color(self.tag_color)

        if self.source == 1: #set properties of bottom box from category list of top box
            self.tag_manager.tag_group_bottom_box.tag_box_entry.set_color(self.tag_color)
            self.tag_manager.tag_group_bottom_box.category_name = self.category_name
            self.tag_manager.tag_group_bottom_box.tag_color = self.tag_color

    def import_items(self):
        if self.source == 0:
            self.tag_manager.tag_tab.import_tag_list(self.tag_box_list)
        elif self.source == 1:
            child_tags = self.tag_manager.tag_group_bottom_box.tag_box_list
            self.tag_manager.tag_groups.import_group_list(parent_list=self.tag_box_list, child_list=child_tags)

       #self.tag_box_list

    def initUI(self):
        self.import_widget = QWidget()
        self.import_widget.setMinimumHeight(70)
        self.import_widget.setMaximumHeight(90)
        self.import_widget.setStyleSheet("background-color: none;")
        self.import_widget_layout = QHBoxLayout(self.import_widget)

        self.clear_tag_box_btn = QPushButton("-")
        self.clear_tag_box_btn.setCursor(Qt.PointingHandCursor)
        self.clear_tag_box_btn.setFixedSize(60,60)
        self.clear_tag_box_btn.setStyleSheet("background-color: purple;")
        self.clear_tag_box_btn.clicked.connect(self.clear_tag_box)
        self.import_widget_layout.addWidget(self.clear_tag_box_btn, Qt.AlignLeft)

        self.import_entities = QPushButton("+")
        self.import_entities.setMinimumWidth(60)
        self.import_entities.setMinimumHeight(60)
        self.import_entities.setCursor(Qt.PointingHandCursor)
        self.import_entities.setStyleSheet("QPushButton { font-size: 40px; background-color: #444; color: white; border: 2px solid #888; border-radius: 8px; } QPushButton:hover { background-color: #666; }")
        self.import_entities.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.import_widget_layout.addWidget(self.import_entities, Qt.AlignCenter)
        self.import_entities.clicked.connect(self.import_items)

        self.delete_button = QPushButton("-")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setFixedSize(60,60)
        self.delete_button.setStyleSheet("QPushButton { font-size: 40px; background-color: red; color: white; border: 2px solid #888; border-radius: 8px; } QPushButton:hover { background-color: red; }")
        self.import_widget_layout.addWidget(self.delete_button, Qt.AlignRight)
        self.delete_button.clicked.connect(self.delete_tags)

class TagIcon(QPushButton):
    def __init__(self, name, cat_name, color, restore, border_color):

        tag_name = name

        if border_color is None:
            border_color = "#2C3539"

        super().__init__(f"{tag_name} x")

        restore_tag = restore 
        self.update_color(color, border_color)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda checked, tag_name=tag_name, category_name=cat_name, widget=self: restore_tag(tag_name, category_name, widget))

    def update_color(self, tag_color, border_color):

        self.setStyleSheet(f"""
        background-color: #2C3539;
        color: {tag_color};
        border: 1px solid;
        border-color: {border_color};
        border-radius: 6px;
        font-size: 20px;
        padding: 6px 10px;
        
    """)
    
class TagEntry(QLineEdit):
    def __init__(self, tm, s, parent=None):
        super().__init__(parent)

        self.tag_manager = tm
        self.source = s
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

        #self.textChanged.connect(self.adjust_width)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        
        self.tag_manager.set_curr_source(self.source)

    def set_color(self, color):
        self.setStyleSheet(f"""
                QLineEdit {{
                    background-color: #0d1117;
                    color: {color};                 
                    border: none;
                    
                }}
            """)
        
class CategoryList(QListWidget):
    def __init__(self, categories, tag_box):
        super().__init__()
        self.setSelectionMode(QListWidget.SingleSelection)

        self.tag_box = tag_box

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
                self.tag_box.set_category(name, color)

        super().mousePressEvent(event)
    
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



