from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget, QGridLayout, QApplication, QApplication, QVBoxLayout, QLayout
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QPoint, QRect, QUrl, QMimeData, QSize
from PyQt5.QtGui import QPixmap, QCursor, QPainter, QColor, QPen, QImageReader

from media_properties.media_display import MediaDisplayWindow


import os, json, sqlite3

class MediaManager(QWidget):
    changeSize = pyqtSignal()
    def __init__(self, booru_db, parent=None):
        super().__init__(parent)

        self.booru_db = booru_db

        self.media_layout = FlowLayout()
        self.setLayout(self.media_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.installEventFilter(self)

        self.selection_box = DragSelectionBox(self)
     
        self.image_size = 2

        self.windows = []

        self.image_cell_width = 300
        self.image_cell_height = 375

        self.cell_size_width = 315
        self.cell_size_height = 390
     
        self.num_cols = 0
        self.num_rows = 0

        self.max_column = 6
        self.row = 2

        self.starting_count = 0
        self.entity_count = 0
        
        self.current_page = 1
        self.page_count = 0
        
        self.amount_on_current_page = 0
        self.total_on_screen = 0 #images + blank frames

        self.image_size_selection = 2

        self.tag_name = None

        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        self.video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']

        self.selected_file_paths = []
        self.selected_entities = []
        self.widgets_list = []
        self.file_paths = []

        self.crtl_a = False
        self.enter = False
        self.click = None

    def search(self, list):
        self.load_tag_name(list)

        


       

    def set_image_size(self):
        print('yo')
        #self.changeSize.emit()
        self.thumbnail.change_size()

   
      

    def clear_image_area(self):

        while self.media_layout.count():
            child = self.media_layout.takeAt(0)
            if child.widget():
               child.widget().deleteLater()

        self.entity_count = 0
        self.page_count_text.setText("")

    def refresh_image_area(self, image_area_layout):

      
                        
              
            self.total_on_screen 
           
                        


            while image_area_layout.count():
                child = image_area_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            self.current_page = (self.starting_count // self.total_on_screen) + 1 if self.total_on_screen > 0 else 1
            self.page_count = (self.entity_count + self.total_on_screen - 1) // self.total_on_screen if self.total_on_screen else 1 

            if self.entity_count > 0:

                self.page_count_text.setText(f"Page {self.current_page} of {self.page_count}, {self.entity_count} item{'s' if self.entity_count != 1 else ''}")
            else:
                self.page_count_text.setText(f"no items found")

            self.add_image_to_area(image_area_layout)
    
    def set_page_count(self, text):
        self.page_count_text = text

    def load_tag_name(self, tag_names):

        #self.booru_db.load_items(tag_names)
       

        try:
            with open('profiles.json', 'r') as f:
                selected_user = json.load(f)
                self.current_user = selected_user["current_profile"]
        except FileNotFoundError:
           print("no json yet")

        if self.current_user != None:
            self.nested_directory = f"{self.current_user}"

            conn = sqlite3.connect("booru.db")
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM profiles WHERE profile_name = ?", (self.current_user,))
            user = cursor.fetchone()
            user_id = user[0]

            get_tags = ','.join(['?'] * len(tag_names))
            query = f"SELECT id FROM tags WHERE name IN ({get_tags}) AND profile_id = ?"

            params = tag_names + [user_id]
            cursor.execute(query, params)
            tag_ids = cursor.fetchall()

            tag_ids_flat = [row[0] for row in tag_ids]

            placeholders = ','.join(['?'] * len(tag_ids_flat))
            query = (f"SELECT file_id FROM file_tags WHERE tag_id IN ({placeholders}) GROUP BY file_id HAVING COUNT(DISTINCT tag_id) = ?")

            params = tag_ids_flat + [len(tag_ids_flat)]
            cursor.execute(query, params)
            file_ids = cursor.fetchall()

            file_id_list = [row[0] for row in file_ids]

            placeholders = ",".join("?" for _ in file_id_list)
            cursor.execute(f"SELECT path, thumbnail_name, length, type FROM files WHERE id IN ({placeholders})", file_id_list)
            self.file_paths_list = cursor.fetchall()


            self.entity_count = len(self.file_paths_list)
            print(self.entity_count)

            conn.close()

        self.starting_count = 0
   
        self.add_image_to_area(self.media_layout)

    def left_click(self, key):
        original_file_path = key

        tag_name = self.tag_name

        if original_file_path not in self.selected_file_paths:
            self.viewer = MediaDisplayWindow(original_file_path, tag_name, self.booru_db)
           
            self.windows.append(self.viewer)
            self.viewer.show()

            #self.refresh_image_area(self.media_layout)
            
    def right_click(self, key):
        print(f'delete {key}?')
        
    def add_image_to_area(self, image_area_layout):

        self.max_column = 3
       
        row = 0
        col = 0
        self.amount_on_current_page = 0
        
        if self.entity_count > 0: 

            path = f"{self.current_user}/thumbnails/"

            max_height = self.height()
            print(f"max height is {max_height}")

            count = 0

            for name, thumb_name, length, type in self.file_paths_list:

                thumbnail_path = path + thumb_name
               
                self.thumbnail = ThumbnailIcon(name, thumbnail_path, length, type)
                self.thumbnail.clicked.connect(self.left_click)

                count += 1
                self.media_layout.addWidget(self.thumbnail)
                if count == 50:
                    break

   
            

    def ctrl_a(self):

        self.crtl_a = True
      
    
    def eventFilter(self, source, event):
        if event.type() == QEvent.Wheel:
            delta = event.angleDelta().y()
            if delta > 0:
                self.previous_page()
            else:
                self.next_page()
            self.selection_box.end_point = event.pos()
            self.selection_box.update()
            self.selection_box.start_point = None
            self.selection_box.end_point = None
        
            return True
        return super().eventFilter(source, event)
    
    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            if self.enter == False:
                self.click = True
                self.selection_box.start_point = event.pos()  
                self.selection_box.end_point = event.pos() 
                self.selection_box.setGeometry(self.rect())
                self.refresh_image_area(self.media_layout) 

                self.selection_box.raise_()
                self.selection_box.setVisible(True) 
                self.selection_box.update()

                self.selected_entities = []
                self.selected_file_paths = []
                
    def mouseMoveEvent(self, event):

        if self.click == True:
           
            if self.selection_box.start_point:
                self.selection_box.end_point = event.pos()
                self.selection_box.update()  
            
    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.click = False
            self.selection_box.end_point = event.pos()
            self.selection_box.update()
            self.selection_box.start_point = None
            self.selection_box.end_point = None
           
           
    def copy_media(self):

        if len(self.selected_file_paths) != 0:

            file_paths = self.selected_file_paths
            file_urls = [QUrl.fromLocalFile(path) for path in file_paths if os.path.exists(path)]

            if file_urls:
                try:

                    mime_data = QMimeData()
                    mime_data.setUrls(file_urls)

                    clipboard = QApplication.clipboard()
                    clipboard.setMimeData(mime_data)
                
                except Exception as e:
                    print(f"Error: {e}")

            else:
                print("Copy error")

    def next_page(self):
     
        if self.starting_count + self.amount_on_current_page < self.entity_count:
            self.starting_count = self.amount_on_current_page + self.starting_count
            self.refresh_image_area(self.media_layout)
         
    def previous_page(self):
        self.starting_count -= self.total_on_screen
        if self.starting_count < 0:
            self.starting_count = 0 
              
        self.refresh_image_area(self.media_layout)

    def skip_to_last(self):
        self.starting_count = (self.page_count - 1) * self.total_on_screen
        self.refresh_image_area(self.media_layout)

    def skip_to_previous(self):
        self.starting_count = 0
        self.refresh_image_area(self.media_layout)

    
class ThumbnailClick(QLabel):
    leftClicked = pyqtSignal()
    rightClicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.leftClicked.emit()
        elif event.button() == Qt.RightButton:
            self.rightClicked.emit()
        super().mousePressEvent(event)

class DragSelectionBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_point = None
        self.end_point = None
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
  
    def get_rect(self):
        if self.start_point and self.end_point:
            return QRect(self.start_point, self.end_point).normalized()
        return QRect()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.start_point and self.end_point:

            pen = QPen(QColor("white"), 1, Qt.SolidLine)
            brush = QColor(255, 255, 255, 80)  
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(self.get_rect())


class ThumbnailIcon(QLabel):

    clicked = pyqtSignal(str)

    def __init__(self, path, thumbnail_path, length, media_type, parent=None):
        super().__init__(parent)
        self.path = path
        self.type = media_type
        self.length = length

        self.pixmap = QPixmap(thumbnail_path)

        # Scale so that height is at most 256, width adjusts proportionally
        scaled_pixmap = self.pixmap.scaledToHeight(256, Qt.SmoothTransformation)

        self.setPixmap(scaled_pixmap)
        self.setFixedSize(scaled_pixmap.size())
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border: none;")

    def change_size(self):
        scaled_pixmap = self.pixmap.scaledToHeight(128, Qt.SmoothTransformation)

        self.setPixmap(scaled_pixmap)
        print('working?')

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.type == "video":
            painter = QPainter(self)
            
            # Draw blue border
            pen = QPen(QColor("blue"), 6)
            painter.setPen(pen)
            painter.drawRect(self.rect().adjusted(0, 0, 0, 0))

            if self.length:
                # Inset from the edges (to not overlap border)
                margin = 6
                rect_width = 60
                rect_height = 25
                bg_rect = QRect(
                    self.width() - rect_width - margin,
                    margin,
                    rect_width,
                    rect_height
                )

                # Draw translucent black background
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(0, 0, 0, 180))
                painter.drawRect(bg_rect)

                # Draw white duration text
                painter.setPen(QColor("white"))
                painter.drawText(
                    bg_rect,
                    Qt.AlignCenter,
                    self.length
                )



    def mousePressEvent(self, event):
        self.clicked.emit(self.path)
        super().mousePressEvent(event)


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=25):
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
        row_items = []
        row_width = 0
        min_spacing = self.spacing()

        for item in self.item_list:
            item_width = item.sizeHint().width()
            if x + item_width > rect.right() and row_items:
                # Distribute leftover space as extra spacing between items in row
                leftover = rect.right() - x + min_spacing
                extra_spacing = leftover // max(len(row_items) - 1, 1)

                # Reset x to start of row
                x = rect.x()
                for i, row_item in enumerate(row_items):
                    if not testOnly:
                        row_item.setGeometry(QRect(QPoint(x, y), row_item.sizeHint()))
                    x += row_item.sizeHint().width() + min_spacing + extra_spacing
                y += lineHeight + min_spacing

                # Start new row
                row_items = []
                lineHeight = 0
                x = rect.x()

            row_items.append(item)
            x += item_width + min_spacing
            lineHeight = max(lineHeight, item.sizeHint().height())

        # Layout last row with no extra spacing
        x = rect.x()
        for row_item in row_items:
            if not testOnly:
                row_item.setGeometry(QRect(QPoint(x, y), row_item.sizeHint()))
            x += row_item.sizeHint().width() + min_spacing

        return y + lineHeight - rect.y()





    



