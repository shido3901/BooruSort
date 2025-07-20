from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QDialog, QGridLayout, QStyledItemDelegate, QPushButton, 
                             QScrollArea, QListView, QHBoxLayout, QLineEdit, QWidget, QSizePolicy)

from PyQt5.QtCore import Qt, QEvent, QStringListModel, QObject
from PyQt5.QtGui import QColor, QCursor, QMouseEvent

from config.ui_config import MessageBox

class TagCategories(QObject):
    def __init__(self, tm, db):
        super().__init__()

        self.booru_db = db
        self.tag_manager = tm

        self.categories_page = QWidget()
        self.categories_page.setMinimumHeight(100)
        self.categories_page.setStyleSheet("background-color: grey; border: none;")
        self.categories_page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        categories_page_layout = QVBoxLayout(self.categories_page)
        categories_page_layout.setContentsMargins(5,5,5,5)
        categories_page_layout.addStretch()

        self.tag_manager.right_widget.addTab(self.categories_page, "categories")
        self.tag_manager.right_widget.currentChanged.connect(self.tag_manager.change_page)
        self.load = True

    def hide_page(self):
            self.category_widget.hide()

    def show_page(self):

        if self.load == True:

            self.category_widget = QWidget()
            self.category_widget.setMinimumHeight(30)
            self.category_widget.setStyleSheet("background-color: cyan")
            self.category_widget_layout = QVBoxLayout(self.category_widget)
            self.category_widget_layout.setContentsMargins(0,0,0,0)

            self.tag_manager.left_widget_layout.addWidget(self.category_widget, stretch=1)
            self.category_widget.installEventFilter(self)
            
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setStyleSheet("""
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
            
            self.option_widget = QWidget()
            self.option_widget.setStyleSheet("background-color: #112233;")
            self.option_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

            self.option_widget_layout = QVBoxLayout(self.option_widget)
            self.option_widget_layout.addStretch(0)

            self.scroll_area.setWidget(self.option_widget)
            self.category_widget_layout.addWidget(self.scroll_area)

            category_info = self.booru_db.get_category_info()
            self.category_list = (dict(category_info))

            add_category = QPushButton("add category+")
            add_category.setStyleSheet("background-color: #112233; color: white;")
            add_category.setFixedHeight(60)
            self.category_widget_layout.insertWidget(0, add_category)
            add_category.clicked.connect(lambda: self.add_new())

            self.category_panels = []

            count = len(self.category_list)

            for name, color in self.category_list.items():

                category_name = name
                color = self.category_list[category_name]

                self.add_new_category(count=count, category_name=category_name, color=color, move=None)

            self.load = False

        self.category_widget.show()

    def add_new_category(self, count, category_name, color, move):

        category_panel = CategoryPanel(cnt=count, cl=self.category_list, tmc=self,
                                       color=color, db=self.booru_db, name=category_name, 
                                       tm=self.tag_manager)
        
        if move is not None:
            self.option_widget_layout.insertWidget(move, category_panel)
         
        elif category_name is None:
            #"tags" is always at the bottom so insert on top of it
            self.option_widget_layout.insertWidget(len(self.category_list) - 1, category_panel)
        else:

            self.option_widget_layout.insertWidget(0, category_panel)

        self.category_panels.append(category_panel)
        self.option_widget_layout.setAlignment(Qt.AlignTop)
      
    def add_new(self):

        new_count = len(self.category_list) + 1

        if len(self.category_panels) < new_count:
            self.add_new_category(new_count, category_name=None, color="white", move=None)

        self.update_panel_count(new_count)

        self.scroll_area.ensureWidgetVisible(self.category_panels[0])

    def update_panel_count(self, count):

        for panel in self.category_panels:
                panel.update_count(count)

    def eventFilter(self, obj, event):
        if obj == self.category_widget:
            if event.type() == QEvent.MouseButtonPress:
                if isinstance(event, QMouseEvent) and event.button() == Qt.LeftButton:
                    print("Left click detected on category_widget")
                    return True
    
        return False
    
class CategoryPanel(QWidget):
    def __init__(self, cnt, cl, tmc, color, db, tm, name=None):
        super().__init__()

        self.count = cnt
        self.category_list = cl
        self.tmc = tmc
        self.current_color = color
        self.booru_db = db
        self.tag_manager = tm
        self.name = name

        self.rename = False
        self.append_color = "#FFFFFF"
    
        self.setMinimumHeight(10)
        self.setStyleSheet("background-color: #112233;")
        self.setContentsMargins(1,1,1,1)

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(1)

        order_select = QWidget()
        order_select.setMaximumWidth(20)
        order_select.setStyleSheet("background-color: #112233;")
        order_select.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        order_select_layout = QVBoxLayout(order_select)
        order_select_layout.addStretch()
        order_select_layout.setContentsMargins(0,0,0,0)
        
        if name != "tags":

            move_up = QPushButton("^")
            move_up.setFixedSize(30, 20)
            move_up.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            move_up.setStyleSheet("background-color: none;")
            order_select_layout.addWidget(move_up, Qt.AlignTop)
            move_up.clicked.connect(lambda: self.move_panel("up"))

            move_down = QPushButton("v")
            move_down.setFixedSize(30, 20)
            move_down.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            move_down.setStyleSheet("background-color: none;")
            move_down.clicked.connect(lambda: self.move_panel("down"))
            order_select_layout.addWidget(move_down, Qt.AlignBottom)

            order_select_layout.addWidget(move_up, alignment=Qt.AlignTop)
            order_select_layout.addStretch(1)
            order_select_layout.addWidget(move_down, alignment=Qt.AlignBottom)
         
        self.layout.addWidget(order_select)
        
        self.info_widget = QWidget()
        self.info_widget.setMinimumHeight(20)
        self.info_widget.setStyleSheet("color: purple;")
        self.info_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.info_widget_layout = QVBoxLayout(self.info_widget)

        self.layout.addWidget(self.info_widget)

        self.create_label(self.name)
        self.installEventFilter(self)
        
        self.list_view = QListView()
        self.list_view.setStyleSheet("border: none;")
        self.info_widget_layout.addWidget(self.list_view)
        
        self._populate_tags(color)

    def create_label(self, name):

        self.category_name = name

        self.category_info = QWidget()
        self.category_info.setMinimumHeight(20)
        self.category_info.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.category_info_layout = QHBoxLayout(self.category_info)
        self.category_info_layout.setContentsMargins(0,0,0,0)
        self.category_info_layout.setSpacing(0)
       
        if self.category_name:
            self.category_name_widget = QLabel(self.category_name)
            self.category_name_widget.setStyleSheet("font-size:30px; color: white;")

            if name != "tags":
                edit_name = QPushButton("edit")
                edit_name.setFixedSize(40,20)
                edit_name.setStyleSheet("color: white;")
                edit_name.clicked.connect(self.change_name)

                delete_category = QPushButton("del")
                delete_category.setFixedSize(40,20)
                delete_category.setStyleSheet("color: white;")
                delete_category.clicked.connect(self.delete_categories)
                
        else:
            self.category_name_widget = QLineEdit()
            self.category_name_widget.setStyleSheet("font-size:30px; color: white;")
            
        self.category_name_widget.setFixedHeight(35)
        self.category_name_widget.installEventFilter(self)
        self.category_info_layout.insertWidget(0, self.category_name_widget)
       
        if name != "tags" and self.category_name:
            self.category_info_layout.addWidget(edit_name)
            self.category_info_layout.addWidget(delete_category)
            

        color_picker = QPushButton("color")
        color_picker.setFixedSize(40,20)
        color_picker.setStyleSheet("color: white;")
        color_picker.clicked.connect(self.open_color_picker)

        self.category_info_layout.addWidget(color_picker)

        self.info_widget_layout.insertWidget(0, self.category_info)

    def change_name(self):
        self.category_info.deleteLater()
        self.create_label(name=None)
        self.rename = True
        self.old_name = self.name
        
    def _populate_tags(self, color):
       
        tag_amount = 5 if self.count >= 4 else 7 if self.count >= 3 else 10
       
        self.tag_list = [f"example_tag_{i+1}" for i in range(tag_amount)]
        
        self.model = QStringListModel(self.tag_list)
        self.list_view.setModel(self.model)

        if color:
         self.list_view.setItemDelegate(ColorDelegate(QColor(color)))

        rows = self.model.rowCount()
        row_height = self.list_view.sizeHintForRow(0) if rows > 0 else 0
        self.list_view.setFixedHeight(row_height * rows + 2 * self.list_view.frameWidth())

        self.category_name_widget.setFocus()

    def update_count(self, new_count):
      
        self.count = new_count
        self._populate_tags(color=None)

    def create_new_category(self):
        
        new_category_name = self.category_name_widget.text().lower()
        

        if new_category_name:
            if self.rename != True:
                if new_category_name not in self.category_list:
                    self.name = new_category_name
            
                    self.current_color = self.append_color

                    temp_list = {}
                    for key, value in self.category_list.items():
                        temp_list[key] = value
                        if key == "tags":
                            temp_list[new_category_name] = self.current_color

                    self.category_list.clear()
                    self.category_list.update(temp_list)

                    self.booru_db.add_category(new_category_name, self.current_color, temp_list)

                    self.category_info.deleteLater()
                    self.create_label(new_category_name)
                    self.tag_manager.refresh_category_right_list()

                else:
                    empty_name = MessageBox(f"{new_category_name} already exists!", "warning", "BooruSort")
                    empty_name.show()
            else:
                self.rename_confirm(new_category_name)

        else:
                empty_name = MessageBox(f"invalid: empty name", "warning", "BooruSort")
                empty_name.show()    
            
    
    def rename_confirm(self, name):
        if name in self.category_list and name != self.old_name:
            empty_name = MessageBox(f"{name} already exists!", "warning", "BooruSort")
            empty_name.show()
            self.category_name_widget.clear()
            return
        
        if name == self.old_name:
            name = self.old_name
            self.name = self.old_name

        if name not in self.category_list:

            new_dict = {}
            for k, v in self.category_list.items():
                if k == self.old_name:
                    new_dict[name] = v  
                else:
                    new_dict[k] = v  

            self.category_list.clear()
            self.category_list.update(new_dict)
           
            self.name = name

            self.booru_db.update_category_info(category_name=name, new_list=new_dict, new_color=self.old_name)

        self.category_info.deleteLater()
        self.create_label(name)

        self.rename = False

    def move_panel(self, pos):
       
        temp_list = list(self.category_list)

        index = temp_list.index(self.name)
        moved_value = self.category_list[self.name]

        if pos == "up":
            new_pos = index+1
        elif pos == "down" and index > 1:
            new_pos = index-1

        else:
            new_pos = 0
    
        if new_pos >= 1:
            del temp_list[index]
            temp_list.insert(new_pos, self.name)

            del self.category_list[self.name]

            temp_dict = {}
            for key in temp_list:
                if key == self.name:
                    temp_dict[key] = moved_value
                else:
                    temp_dict[key] = self.category_list[key]

            self.category_list.clear()
            self.category_list.update(temp_dict)

            self.booru_db.update_category_info(new_color=self.category_list, category_name=None, new_list=None)

            temp_list.reverse()
            new_index = temp_list.index(self.name)

            self.setParent(None)
            self.deleteLater() 
            self.tmc.category_panels.remove(self)        

            self.tmc.add_new_category(count=self.count, category_name=self.name, color=self.current_color, move=new_index)

    def eventFilter(self, obj, event):
        if obj == self.category_name_widget:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Return:
                    self.create_new_category()

        return super().eventFilter(obj, event)
    
    def open_color_picker(self):

        colors = [
                "#FFFFFF", "#989898",
                "#FF3B3B", "#a20b00",
                "#FF00EE", "#9D0095",
                "#00FFD1", "#0076f5",
                "#63FF63", "#378937",
                "#B855FF", "#7E5899",
                "#FFF200", "#FF9500"
                ]

        dialog = ColorPickerDialog(colors, category_panel=self)
        mouse_pos = QCursor.pos()
    
        dialog.move(mouse_pos.x() + 10, mouse_pos.y())
        
        dialog.exec_()
        self.category_name_widget.setFocus()

    def set_color(self, color):
        prev_color = self.current_color

        self.list_view.setItemDelegate(ColorDelegate(QColor(color)))

        if self.category_name is not None:

            count = self.booru_db.get_category_count(self.category_name)

            if count > 0:

                confirmed, delete_tag_confirm = MessageBox.confirm(f"change color? this will change {count} tags", "color", checkbox_text="do not show again")

                if confirmed:

                    self.update_color(color)

                else: 
                    self.list_view.setItemDelegate(ColorDelegate(QColor(prev_color)))

                if delete_tag_confirm:
                    print("Checkbox was checked")

            else: 
                self.update_color(color)

        elif self.category_name is None:
            self.append_color = color

    def update_color(self, color):

        self.current_color = color

        self.booru_db.update_category_info(self.category_name, self.current_color, new_list=None)
        self.category_list[self.category_name] = self.current_color

        self.tag_manager.update_list_color(self.category_name, self.current_color)

    def delete_categories(self):

        confirmed, delete_tag_confirm = MessageBox.confirm(f"delete '{self.category_name}'?", "delete category", checkbox_text="delete tags")

        if confirmed:
    
            self.booru_db.delete_category(self.category_name)
            del self.category_list[self.category_name]

            self.tmc.category_panels.remove(self)
            
            self.setParent(None)
            self.deleteLater() 

            self.tmc.update_panel_count(len(self.category_list))
            self.tag_manager.refresh_tag_list()
            self.tag_manager.refresh_category_right_list()

        if delete_tag_confirm:
            print("Checkbox was checked")
        
class ColorDelegate(QStyledItemDelegate):
    def __init__(self, color=QColor("white"), parent=None):
        super().__init__(parent)
        self.color = color

    def paint(self, painter, option, index):
        painter.save()
        painter.setPen(self.color)
        painter.drawText(option.rect, Qt.AlignVCenter, index.data())
        painter.restore()

class ColorPickerDialog(QDialog):
    def __init__(self, colors, category_panel):
        super().__init__()

        self.category_panel = category_panel

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setFixedSize(140, 330)
        self.setStyleSheet("background-color: #112233; border: 1px solid white;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        top_bar = QHBoxLayout()
        top_bar.addStretch()

        close_btn = QPushButton("X")
        close_btn.setFixedSize(17, 17)
        close_btn.setStyleSheet(
            "QPushButton { border: none; color: white; background: none;}"
            "QPushButton:hover { color: red; }"
        )
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)

        main_layout.addLayout(top_bar)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)

        for i, color in enumerate(colors):
            btn = QPushButton()
            btn.setFixedSize(35,35)
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid #aaa; border-radius: 5px;")
            btn.clicked.connect(lambda checked, c=color: self.select_color(c))
            grid_layout.addWidget(btn, i // 2, i % 2)

        main_layout.addLayout(grid_layout)

    def select_color(self, color):
        self.category_panel.set_color(color)
        self.accept()