from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget, QGridLayout, QApplication, QApplication, QVBoxLayout, QLayout, QScrollArea, QHBoxLayout
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QPoint, QRect, QUrl, QMimeData, QSize, QThread, QObject, QTimer, QThreadPool, QRunnable
from PyQt5.QtGui import QPixmap, QCursor, QPainter, QColor, QPen, QImageReader, QImage

from media_properties.media_display import MediaDisplayWindow
import time




import os, json, sqlite3

class MediaManager(QWidget):
    changeSize = pyqtSignal()
    def __init__(self, booru_db, main_area, main_area_layout):
        super().__init__()

        self.current_page = 1
        self.total = 0
        self.total_pages = 0
        self.total_items = 0
        self.current_layout = 1


        self.booru_db = booru_db

        self.main_area = main_area
        self.main_area_layout = main_area_layout
        

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
        self.setStyleSheet("color: transparent; border-color: none;")
     
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
       
    
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

        self.mouse_clicked = False
        self.hover = False

        self.crtl = False

        self.page_count = 0
      
        self.threadpool = QThreadPool()


    def on_hover(self, type):

        if type == 1:
            self.hover = True
           
        else:
            self.hover = False


    def set_preview(self, preview_img, file_path):

        preview_img = preview_img.scaledToHeight(self.img_size, Qt.SmoothTransformation)

        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(6,6,6,6)
        layout.setSpacing(12)

        img_label = QLabel()
        img_label.setPixmap(preview_img)
        img_label.setFixedSize(preview_img.size())
        layout.addWidget(img_label)

        if file_path not in self.selected_file_paths or len(self.selected_file_paths) <= 1:
            file_urls = [QUrl.fromLocalFile(file_path)]

            if self.crtl is False:

                self.unselect_all()
            
        else:

            file_urls = [QUrl.fromLocalFile(path) for path in self.selected_file_paths if os.path.exists(path)]

            

            # Text label
            text_label = QLabel(f"+{len(self.selected_file_paths) - 1}")
            layout.addWidget(text_label)

            
            # Render widget to pixmap
            
            

        widget.setLayout(layout)
        widget.adjustSize()

        self.preview_image = widget.grab()


        if file_urls:

            self.mime_data = QMimeData()
            self.mime_data.setUrls(file_urls)

    
       

    def search(self, list):
        self.load_tag_name(list) 

    def set_amount(self):

        self.current_amount_index = (self.current_amount_index + 1) % len(self.thumbnail_sizes)
        self.items_per_page = self.amount_per_page[self.current_amount_index]

        self.search_results.thumbnails.clear()


        self.load_thumbnails(self.file_info)

        

        #print(self.amount)

    def set_image_size(self):
        
        self.current_size_index = (self.current_size_index + 1) % len(self.thumbnail_sizes)
        self.img_size = self.thumbnail_sizes[self.current_size_index]
    
        for page_key in ("current", "next", "previous"):
            for thumbnail in self.search_results.thumbnails[page_key]:
                thumbnail.change_size(self.img_size)


    def load_tag_name(self, tag_names):

        file_list = self.booru_db.files.load_file_info(tag_names)

        self.batch_size = 25
        self.current_batch_index = 0     

        if file_list:

            self.load_thumbnails(file_list)

        else:
            self.previous_name = None
            self.clear_layout()
            print('implement empty box message')

    def set_ctrl(self, type):
        self.crtl = type

        print(self.crtl)


    def left_click(self, file_paths):
            
        tag_name = None

        self.viewer = MediaDisplayWindow(file_paths, tag_name, self.booru_db)
        
        self.windows.append(self.viewer)
        self.viewer.show()

        self.selected_file_paths.clear()

        self.unselect_all()

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

    def unselect_all(self):
        for page_key in ("current", "next", "previous"):
            for thumbnail in self.search_results.thumbnails[page_key]:
                thumbnail.unselect()

   
    def load_thumbnails(self, file_list):

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

                    # this is a crime
                    thumbnail_icon = ThumbnailIcon(path, pixmap, length, media_type, size=self.media_manager.img_size, 
                                                   left_click=self.media_manager.left_click, file_paths=self.media_manager.selected_file_paths, 
                                                   on_hover=self.media_manager.on_hover, pre_loaded_thumbs=self.thumbnails, preview=self.media_manager.set_preview,
                                                   media_manager=self.media_manager)
                    

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

            print(f"copied {len(file_urls)} files")



    


class ThumbnailIcon(QLabel):

    clicked = pyqtSignal(str)

    def __init__(self, path, pixmap, length, media_type, size, left_click, file_paths, on_hover, pre_loaded_thumbs, preview, media_manager, parent=None):

        super().__init__(parent)

        self._highlight = False

        self.media_manager = media_manager

        self.original_pixmap = pixmap

        self.path = path
        self.type = media_type
        self.length = length
        self.left_click = left_click

        self.file_paths = file_paths

        self.on_hover = on_hover

        self.thumbnail_list = pre_loaded_thumbs

        self.set_preview = preview


        self.img_size = size

       

        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border: none;")

        self.change_size(size)

    def change_size(self, size):
        self.img_size = size

        scaled = self.original_pixmap.scaledToHeight(size, Qt.SmoothTransformation)

        self.setPixmap(scaled)
        self.setFixedSize(scaled.size())

  
    def paintEvent(self, event):
        super().paintEvent(event)
        

        if self.type == "video":
            
            painter = QPainter(self)

            if self._highlight is False:
                pen = QPen(QColor("blue"), 6)
            else:
                pen = QPen(QColor("cyan"), 6)
                
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

        if self._highlight is True:
            if self.type != "video":
                painter = QPainter(self)
                pen = QPen(Qt.cyan, 6)  
                painter.setPen(pen)
                rect = self.rect().adjusted(1, 1, -1, -1)  
                painter.drawRect(rect)

    def selected(self):
        if not self._highlight:
            self._highlight = True
            self.file_paths.append(self.path)
          
            self.update()

    def unselect(self):
        if self._highlight:
            self._highlight = False
            if self.path in self.file_paths:
                self.file_paths.remove(self.path)
             
            self.update()


    def enterEvent(self, a0):
        self.on_hover(1)
        

        return super().enterEvent(a0)
    
    def leaveEvent(self, a0):
        self.on_hover(0)
        return super().leaveEvent(a0)
    
    
    def mousePressEvent(self, ev):

        self.set_preview(self.original_pixmap, self.path)

        if self.media_manager.crtl is True and self._highlight is False:
            
            self.selected()
           

        elif self.media_manager.crtl is True and self._highlight is True:
            self.unselect()
          

        return super().mousePressEvent(ev)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:

            if self.media_manager.crtl is False:
            
                self.left_click(self.path)


        event.ignore()

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
               
                x_row = rect.x()
                if self.justify_rows and len(row_items) > 1:
                    total_width = sum(i.sizeHint().width() for i in row_items)
                    leftover = rect.width() - total_width - min_spacing * (len(row_items) - 1)
                    leftover = max(0, leftover)  
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

               
                row_items = []
                lineHeight = 0
                x = rect.x()

            row_items.append(item)
            x += item_width + min_spacing
            lineHeight = max(lineHeight, item.sizeHint().height())

        x_row = rect.x()
        for i, row_item in enumerate(row_items):
            if not testOnly:
                row_item.setGeometry(QRect(QPoint(x_row, y), row_item.sizeHint()))
            x_row += row_item.sizeHint().width()
            if i < len(row_items) - 1:
                x_row += min_spacing

        return y + lineHeight - rect.y()



