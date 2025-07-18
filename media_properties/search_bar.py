
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListView, QLineEdit, QSizePolicy, QDesktopWidget)

from PyQt5.QtCore import Qt, QPoint, QEvent
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor

class SearchBar(QWidget):
    def __init__(self, media_viewer, search_bar_widget):
        super().__init__()


        self.tag_data = {}

        self.current_user = None
        self.text_box = QLineEdit(search_bar_widget)
        self.media_viewer = media_viewer

        
      

        self.text_box.setPlaceholderText("Search Example: black_cat")
        self.text_box.setMinimumHeight(30)
        self.text_box.setMinimumWidth(700)
        self.text_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.text_box.installEventFilter(self)
        self.text_box.setFocusPolicy(Qt.StrongFocus)
    
        self.list = QListView(self)
        self.model = QStandardItemModel()
        self.list.installEventFilter(self)
        
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        
       
    
        
        self.setStyleSheet("background-color: #010c1c; border: 2px solid #1f618d; border-radius: 10px;")
        layout.addWidget(self.list)
        self.new_entry = 0

        self.list.setStyleSheet("""QListView::item:hover {background-color: #274c7a; color: white;}""")

        

        self.list.setModel(self.model)
        
    def search_dropdown(self, text):
       
        if text != '':  
            self.show_under(self.text_box)
        else:
            self.close()

    def show_under(self, widget):
        global_pos = widget.mapToGlobal(QPoint(0, widget.height()))

        self.move(global_pos)
        self.show()

    def load_tag_list(self, tag_name_data):
        self.tag_data = {}
        self.tag_data = tag_name_data
     
 
    def insert_tag_name(self, tag_name):

        result = [tag_name]
        print(f"inputting {result}")

        search_from_tag_widget = tag_name.replace(" ", "_")
        self.text_box.setText(f"{search_from_tag_widget} ")
        self.media_viewer.search(result)

        self.close()

    def add_to_search_bar(self, tag_name):

        search_from_tag_widget = tag_name.replace(" ", "_")
        self.text_box.insert(f"{search_from_tag_widget} ")
        self.text_box.setFocus()

        self.close()
   
    def search(self, text):
        last_word = text.split()[-1] if text.strip() else ''
        self.model.clear()

        starts_with = []
        contains = []

        for tag in self.tag_data:
            if last_word.lower() in tag:
                if tag.lower().startswith(last_word.lower()):
                    starts_with.append(tag)
                else:
                    contains.append(tag)

        filtered_tags = starts_with + contains
        self.filter_text = filtered_tags
        longest = 0

        for tag in filtered_tags:
            
            if len(tag) >= longest:
                longest = len(tag)
         

            color = self.tag_data[tag]["color"]
            count = self.tag_data[tag]["count"]

            display_text = f"{tag} ({count})"
            item = QStandardItem(display_text)
            item.setForeground(QColor(color))
            self.model.appendRow(item)

        if filtered_tags:
            self.first_item = filtered_tags[0]
            length = len(filtered_tags)
           
            window_width = longest * 20
            if window_width < 150:
                window_width = 200
           
            window_height = length * 40
            if window_height < 150:
                window_height = 200
            elif window_height >= 900:
                window_height = 900
            
            self.resize(window_width, window_height)
            #print(f"height is {window_height}")
        
        else:
            self.close()

    def insert_text(self, tag):
       
        current_text = self.text_box.text()
        parts = current_text.rstrip().split(' ')
      
        parts[-1] = tag  
        self.new_entry = ' '.join(parts) + ' '  
        self.text_box.setText(self.new_entry)  
        self.text_box.setCursorPosition(len(self.new_entry))  

    def on_item_clicked(self, index):
     
        item_text = self.model.itemFromIndex(index).text()
        tag = item_text.split(" (")[0]  

        new_tag = tag.replace(" ", "_")
        self.insert_text(new_tag)

        self.close()  
    
    #gonna change this, this is so dumb
    def eventFilter(self, source, event):
        if source == self.text_box:
            if event.type() == QEvent.KeyRelease:
                if event.key() == Qt.Key_Down:
                    self.list.window().activateWindow()
                    self.list.setFocus()
                    if self.model.rowCount() > 0:
                        first_index = self.model.index(0, 0)
                        self.list.setCurrentIndex(first_index)
                      
               
    
                elif event.key() == Qt.Key_Backspace or event.text().isprintable():
                    text = self.text_box.text()
                    self.search_dropdown(text)
                    self.search(text)

                

            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Tab:
                
                       
                    if self.text_box.text().strip() != "":
                      
                        
                        event.accept()
            
                        first_index = self.model.index(0, 0)
                        self.list.setCurrentIndex(first_index)

                        selected_index = self.list.selectedIndexes()
                      
                        if selected_index:
                            self.on_item_clicked(selected_index[0])
                      
                            self.text_box.setFocus()
                            self.text_box.update()

                

                    return True
                
                if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            
                    print(self.text_box.text())

                    result = [word.replace('_', ' ') for word in self.text_box.text().split()]
                    print(f"inputting {result}")
                    
                    self.media_viewer.search(result)
                    self.close()
              

                    
                  
                     

        elif source == self.list:
            if event.type() == QEvent.KeyPress:
             
                if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
                    self.insert_selected_text()
                    

                elif event.key() == Qt.Key_Up:
                    
                    selected_index = self.list.selectedIndexes()
                  
                    if selected_index:
                        row = selected_index[0].row()
                        if row == 0:
                          
                            self.close()

                elif event.key() == Qt.Key_Tab:
                    self.insert_selected_text()

                 
                elif event.key() in [Qt.Key_Up, Qt.Key_Down]:
                    self.list.window().activateWindow()
                   
                elif event.key() == Qt.Key_Backspace:
                    self.text_box.window().activateWindow()

                elif event.key() == Qt.Key_Escape:
                    self.close()
                

        return super().eventFilter(source, event)
    
    def insert_selected_text(self):

        selected_index = self.list.selectedIndexes()
                   
        if selected_index:
            self.on_item_clicked(selected_index[0])

    

