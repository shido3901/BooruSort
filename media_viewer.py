from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget, QGridLayout, QApplication, QApplication, QVBoxLayout, QLayout, QScrollArea
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QPoint, QRect, QUrl, QMimeData, QSize, QThread, QObject, QTimer, QThreadPool, QRunnable
from PyQt5.QtGui import QPixmap, QCursor, QPainter, QColor, QPen, QImageReader, QImage

from media_properties.media_display import MediaDisplayWindow
import time




import os, json, sqlite3

class MediaManager(QWidget):
    changeSize = pyqtSignal()
    def __init__(self, booru_db, main_area):
        super().__init__()

        self.current_page = 1
        self.total = 0
        self.total_pages = 0
        self.total_items = 0
        self.current_layout = 1


        self.booru_db = booru_db
        self.main_area = main_area

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)


        container = QWidget()
        container.setMinimumSize(10,10)
        self.media_layout = FlowLayout(container, spacing=20, justify_rows=True)
        container.setLayout(self.media_layout)
      

        self.scroll_area.setWidget(container)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        self.setMinimumWidth(10)
        self.setStyleSheet("border-color: green;")
             
     
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.installEventFilter(self)

        self.selection_box = DragSelectionBox(self)

    

        self.thumbnail_sizes = [128, 256, 384, 512]  
        self.current_size_index = 1
        self.img_size = 256

        self.items_per_page = 25
        self.amount_per_page = [25, 50, 75, 100]  
        self.current_amount_index = 4

        self.selected_file_paths = []
        self.selected_entities = []

        self.thumbnail_list = []

        self.search_queue = []

        self.windows = []

        self.crtl_a = False
        self.enter = False
        self.click = None

        

        self.timer_start = None
        self.timer_end = None


        self.previous_name = None
        self.search_results = None

        self.page_count = 0
      
        self.threadpool = QThreadPool()

    def search(self, list):
        self.load_tag_name(list) 

    def set_amount(self):

        self.current_amount_index = (self.current_amount_index + 1) % len(self.thumbnail_sizes)
        self.items_per_page = self.amount_per_page[self.current_amount_index]

        self.refresh_layout()

        #print(self.amount)

    def set_image_size(self):
        
        self.current_size_index = (self.current_size_index + 1) % len(self.thumbnail_sizes)
        self.img_size = self.thumbnail_sizes[self.current_size_index]
    
        for page_key in ("current", "next", "previous"):
            for thumbnail in self.search_results.thumbnails[page_key]:
                thumbnail.change_size(self.img_size)

    def set_layout(self):
        if self.current_layout == 0:

            self.current_layout = 1
            self.media_layout.justify_rows=True
            
            for page_key in ("current", "next", "previous"):
                for thumbnail in self.search_results.thumbnails[page_key]:
                    thumbnail.change_size(self.img_size)

            

        else:

            self.current_layout = 0
            self.media_layout.justify_rows=False

            for page_key in ("current", "next", "previous"):
                for thumbnail in self.search_results.thumbnails[page_key]:
                    thumbnail.set_grid()


    def load_tag_name(self, tag_names):

        file_list = self.booru_db.files.load_file_info(tag_names)

        self.batch_size = 25
        self.current_batch_index = 0     

        if file_list:

            self.load_thumbnails(tag_names, file_list)

        else:
            self.previous_name = None
            self.clear_layout()
            print('implement empty box message')

    def left_click(self, key):
        original_file_path = key

        tag_name = None

        if original_file_path not in self.selected_file_paths:
            self.viewer = MediaDisplayWindow(original_file_path, tag_name, self.booru_db)
           
            self.windows.append(self.viewer)
            self.viewer.show()

            #self.refresh_image_area(self.media_layout)

    def refresh_layout(self):

        self.clear_layout()
        self.loaded = True
        self.display_thumbnails()

    def clear_layout(self):

        while self.media_layout.count():
                item = self.media_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)

   
    def load_thumbnails(self, tag_names, file_list):

        if self.search_results is not None:
            self.search_results.thumbnails.clear()

        self.file_info = file_list

        self.current_page = 1
        self.thumbnail_directory = f"{self.booru_db.current_profile}/thumbnails/"
        
        class SearchResults(QObject):
            def __init__(self, file_list, media_manager):
                super().__init__()

                self.file_list = file_list
                self.media_manager = media_manager

                self.total = len(file_list)
                
                self.thumbnails = {
                    "previous": [],
                    "current": [],
                    "next": []
                }
            
                self.create_batch(thumbnail_page_type=["current", "next", "previous"])

            def create_batch(self, thumbnail_page_type):

                render_batch = self.media_manager.get_pagination_ranges(
                    total=self.total, 
                    items_per_page=self.media_manager.items_per_page, 
                    current_page=self.media_manager.current_page
                    )
                
                for self.page_key in thumbnail_page_type:
                    page_range = render_batch[self.page_key]

                    if page_range is None:
                        continue

                    self.start, self.end = page_range
                    self.batch = []

                    self.thumbnail_directory = self.media_manager.thumbnail_directory

                    for path, thumbnail_name, length, media_type in self.file_list[self.start:self.end]:
                        thumbnail_path = self.thumbnail_directory + thumbnail_name
                        self.batch.append((path, thumbnail_path, length, media_type))

                    worker = ImageWorker(self.batch, self.page_key, parent=self)
                    worker.signals.images_ready.connect(self.display_thumbnails)
                    self.timer_start = time.perf_counter()
                
                    self.media_manager.threadpool.start(worker)

            def display_thumbnails(self, thumbnail_list, key): 
                
                for path, thumbnail_img, length, media_type in thumbnail_list:

                    pixmap = QPixmap.fromImage(thumbnail_img)
                    thumbnail_icon = ThumbnailIcon(path, pixmap, length, media_type, size=self.media_manager.img_size, left_click=self.media_manager.left_click)
                    self.thumbnails[key].append(thumbnail_icon)

                if key == "current":
                    self.media_manager.clear_layout()

                    for thumbnails in self.thumbnails["current"]:
                        self.media_manager.media_layout.addWidget(thumbnails)
                        
                    elapsed = time.perf_counter() - self.timer_start

                    print(f"{key} generated and displayed in {elapsed}s")

                else:
                    self.loaded = True

                        

                #print(f" LENGTH OF PREVIOUS: {len(self.thumbnails["previous"])}")
                #print(f" LENGTH OF CURRENT: {len(self.thumbnails["current"])}")
                #print(f" LENGTH OF NEXT: {len(self.thumbnails["next"])}")

            def load_page(self, page):
                printed = 0   


                #0 = load previous, else load next page

                if self.loaded is True:
                    print('locked')
                    self.loaded = False

                    load_page = "previous" if page==0 else "next"
                    shift_page = "next" if page==0 else "previous"

                    for thumbnails in self.thumbnails[load_page]:
                        self.media_manager.media_layout.addWidget(thumbnails)
                        printed += 1
                        

                    self.thumbnails[shift_page] = self.thumbnails["current"].copy()
                    self.thumbnails["current"].clear()

                    self.thumbnails["current"] = self.thumbnails[load_page].copy()
                    self.thumbnails[load_page].clear()

                    self.create_batch(thumbnail_page_type=[load_page])

                    self.media_manager.set_page_count(self.media_manager.page_count_label)
                    print(f"loaded {printed} imgs")

                        
        class ImageWorkerSignals(QObject):
            images_ready = pyqtSignal(object, str)

        class ImageWorker(QRunnable):
            def __init__(self, batch_info, page_key, parent=None):
                super().__init__()

                self.signals = ImageWorkerSignals(parent)
                self.batch_info = batch_info
                self.key = page_key

                self.thumbnail_info = []

            def run(self):

                for path, thumbnail_path, length, media_type in self.batch_info:
                    thumbnail_img = QImage(thumbnail_path)
                    self.thumbnail_info.append((path, thumbnail_img, length, media_type))

                self.signals.images_ready.emit(self.thumbnail_info, self.key)
        
        self.search_results = SearchResults(file_list, media_manager=self)
        
    def get_pagination_ranges(self, total, items_per_page, current_page):
        self.page_count = (total + items_per_page - 1) // items_per_page
        self.total_items = total

        self.set_page_count(self.page_count_label)


        def get_page_range(page):
            
            start_index = (page - 1) * items_per_page
            end_index = min(start_index + items_per_page, total)
            return start_index, end_index
    
        current_range = get_page_range(current_page)

        previous_page = current_page - 1 if current_page > 1 else self.page_count
        next_page = current_page + 1 if current_page < self.page_count else 1

        previous_range = get_page_range(previous_page)
        next_range = get_page_range(next_page)

        return {
            "previous": None if previous_range == current_range else previous_range,
            "current": current_range,
            "next": None if next_range == current_range else next_range
        }
        

    
        

    def set_page(self, page):
        page_select = page

        if page_select == 0 and self.current_page > 1: #previous
            self.current_page -= 1
            self.clear_layout()
            self.search_results.load_page(0)

        elif page_select == 1 and self.current_page < self.page_count: #next
            self.current_page += 1

            self.clear_layout()
            self.search_results.load_page(2)

        elif page_select == 2:
            self.current_page = 1 #beginning

        elif page_select == 3:
            self.current_page = self.page_count #last page

        self.set_page_count(self.page_count_label)
       
    def skip_to_last(self):
            pass

    def skip_to_previous(self):
        pass

    def set_page_count(self, page_count):
        self.page_count_label = page_count 
      
        self.page_count_label.setText(f"Page {self.current_page} of {self.page_count}, {self.total_items} items")

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


        print('HIIIIIIIIIIIIIIIIII')

        #print(f"Finished QImages in {elapsed}s")


class ThumbnailIcon(QLabel):

    clicked = pyqtSignal(str)

    def __init__(self, path, pixmap, length, media_type, size, left_click, parent=None):

        super().__init__(parent)

        self.original_pixmap = pixmap

        self.path = path
        self.type = media_type
        self.length = length
        self.left_click = left_click

        self.img_size = size

        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border: none;")

        self.change_size(size)

    def change_size(self, size):
        self.img_size = size

        scaled = self.original_pixmap.scaledToHeight(size, Qt.SmoothTransformation)

        self.setPixmap(scaled)
        self.setFixedSize(scaled.size())

    def set_grid(self):
        scaled_pixmap = self.original_pixmap.scaled(
            self.img_size, self.img_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # Create a new square pixmap with transparent background
        square_pixmap = QPixmap(self.img_size, self.img_size)
        square_pixmap.fill(Qt.transparent)

        painter = QPainter(square_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Draw the scaled pixmap centered
        x = (self.img_size - scaled_pixmap.width()) // 2
        y = (self.img_size - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)

        # Prepare semi-transparent white pen for border
        semi_white = QColor(255, 255, 255, 180)  # White with alpha transparency
        pen_width = 4  # Adjust thickness of border here
        pen = QPen(semi_white)
        pen.setWidth(pen_width)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)  # No fill for border

        # Draw the border rectangle inside the pixmap edges,
        # subtracting half pen width to fully show border inside pixmap
        offset = pen_width // 2
        rect_size = self.img_size - pen_width
        painter.drawRect(offset, offset, rect_size, rect_size)

        painter.end()

        self.setPixmap(square_pixmap)
        self.setFixedSize(square_pixmap.size())



    def paintEvent(self, event):
        super().paintEvent(event)

        if self.type == "video":
            painter = QPainter(self)
            
            pen = QPen(QColor("blue"), 6)
            painter.setPen(pen)
            painter.drawRect(self.rect().adjusted(0, 0, 0, 0))

            if self.length:
             
                margin = 6
                rect_width = 60
                rect_height = 25
                bg_rect = QRect(
                    self.width() - rect_width - margin,
                    margin,
                    rect_width,
                    rect_height
                )

               
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(0, 0, 0, 180))
                painter.drawRect(bg_rect)

              
                painter.setPen(QColor("white"))
                painter.drawText(
                    bg_rect,
                    Qt.AlignCenter,
                    self.length
                )



    def mousePressEvent(self, event):
        self.clicked.emit(self.path)
        self.left_click(self.path)
        print(self.path)
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



class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=25, justify_rows=False):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.item_list = []
        self.justify_rows = justify_rows 

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
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
        min_spacing = self.spacing()

        for item in self.item_list:
            item_width = item.sizeHint().width()
            if x + item_width > rect.right() and row_items:
                # Layout current row
                x_row = rect.x()
                if self.justify_rows and len(row_items) > 1:
                    total_width = sum(i.sizeHint().width() for i in row_items)
                    leftover = rect.width() - total_width - min_spacing * (len(row_items) - 1)
                    leftover = max(0, leftover)  # avoid negative leftover
                    extra_spacing = leftover // (len(row_items) - 1)
                else:
                    extra_spacing = 0

                for i, row_item in enumerate(row_items):
                    if not testOnly:
                        row_item.setGeometry(QRect(QPoint(x_row, y), row_item.sizeHint()))
                    x_row += row_item.sizeHint().width()
                    if i < len(row_items) - 1:
                        x_row += min_spacing + extra_spacing

                y += lineHeight + min_spacing

                # Start new row
                row_items = []
                lineHeight = 0
                x = rect.x()

            row_items.append(item)
            x += item_width + min_spacing
            lineHeight = max(lineHeight, item.sizeHint().height())

        # Layout last row (never justify last row)
        x_row = rect.x()
        for i, row_item in enumerate(row_items):
            if not testOnly:
                row_item.setGeometry(QRect(QPoint(x_row, y), row_item.sizeHint()))
            x_row += row_item.sizeHint().width()
            if i < len(row_items) - 1:
                x_row += min_spacing

        return y + lineHeight - rect.y()



