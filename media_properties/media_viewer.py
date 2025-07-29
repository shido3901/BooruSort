from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget, QApplication, QApplication, QVBoxLayout, QLayout, QScrollArea, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, QUrl, QMimeData, QSize, QObject, QThreadPool, QRunnable, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QImage, QDrag, QCursor, QDragEnterEvent, QDropEvent

from media_properties.media_display import MediaDisplayWindow

import os, time

class MediaManager(QWidget):
    changeSize = pyqtSignal()
    def __init__(self, booru_db, main_area, main_area_layout):
        super().__init__()

        self.booru_db = booru_db

        self.main_area = main_area
        self.main_area_layout = main_area_layout
        self.main_area.setMouseTracking(True)
        self.main_area.setAcceptDrops(True)

        self.installEventFilter(self)
        self.main_area.installEventFilter(self)

        self.drag_box = DragSelectionBox(self.main_area)
        self.start_point = None
        self.drag_box.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.drag_box.hide()

        self.page_count = 0
        self.current_page = 1
        self.total_pages = 0
        self.total_items = 0

        self.thumbnail_sizes = [128, 256, 384, 512]  
        self.current_size_index = 1
        self.img_size = 256

        self.items_per_page = 25
        self.amount_per_page = [25, 50, 75, 100]  
        self.current_amount_index = 4

        self.selected_thumbnails = set()
        self.selected_file_paths = []
        self.windows = []

        self.search_results = None
        self.hover = False
        self.ctrl = False

        self.threadpool = QThreadPool()

        self.initUI()  

    def initUI(self):

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

        self.setAcceptDrops(True)
        
        self.setMinimumWidth(10)
        self.setStyleSheet("color: transparent; border-color: none;")
     
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def search(self, list):
        self.load_tag_name(list) 

    def load_tag_name(self, tag_names):

        file_list = self.booru_db.files.load_file_info(tag_names)

        self.current_batch_index = 0     

        if file_list:
            self.load_thumbnails(file_list)

        else:
            self.clear_layout()
            print('implement empty box message')      

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
                    worker.signals.processed.connect(self.display_thumbnails)
                    self.timer_start = time.perf_counter()
                
                    self.media_manager.threadpool.start(worker)

            def display_thumbnails(self, thumbnail_list, key): 
                
                for path, thumbnail_img, length, media_type in thumbnail_list:

                    pixmap = QPixmap.fromImage(thumbnail_img)

                    thumbnail_icon = ThumbnailIcon(path, pixmap, length, media_type, media_manager=self.media_manager)
                    
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
                printed = 0   #0 = load previous, else load next page
                
                if self.loaded is True:
                    print('locked')
                    self.loaded = False

                    load_page = "previous" if page==0 else "next"
                    shift_page = "next" if page==0 else "previous"

                    self.media_manager.clear_layout()

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
            processed = pyqtSignal(object, str)

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

                self.signals.processed.emit(self.thumbnail_info, self.key)
        
        self.search_results = SearchResults(file_list, media_manager=self)

    def clear_layout(self):

        while self.media_layout.count():
                item = self.media_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)

    def display_media(self, file_paths):
            
        self.viewer = MediaDisplayWindow(file_paths, self.booru_db)
        
        self.windows.append(self.viewer)
        self.viewer.show()

        self.selected_file_paths.clear()

        self.unselect_all()

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
            self.search_results.load_page(0)

        elif page_select == 1 and self.current_page < self.page_count: #next
            self.current_page += 1
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

    def set_amount(self):

        self.current_amount_index = (self.current_amount_index + 1) % len(self.thumbnail_sizes)
        self.items_per_page = self.amount_per_page[self.current_amount_index]

        self.search_results.thumbnails.clear()

        self.load_thumbnails(self.file_info)

    def set_image_size(self):
        
        self.current_size_index = (self.current_size_index + 1) % len(self.thumbnail_sizes)
        self.img_size = self.thumbnail_sizes[self.current_size_index]
    
        for page_key in ("current", "next", "previous"):
            for thumbnail in self.search_results.thumbnails[page_key]:
                thumbnail.change_size(self.img_size)

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

    def unselect_all(self):
        try:
            for page_key in ("current", "next", "previous"):
                for thumbnail in self.search_results.thumbnails[page_key]:
                    thumbnail.update_highlight(highlight=False)
        except:
            pass

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

            if self.ctrl is False:
                self.unselect_all()
            
        else:

            file_urls = [QUrl.fromLocalFile(path) for path in self.selected_file_paths if os.path.exists(path)]

            text_label = QLabel(f"+{len(self.selected_file_paths) - 1}")
            layout.addWidget(text_label)

        widget.setLayout(layout)
        widget.adjustSize()

        self.preview_image = widget.grab()

        if file_urls:

            self.mime_data = QMimeData()
            self.mime_data.setUrls(file_urls)

    def set_ctrl(self, type):
        self.ctrl = type

    def eventFilter(self, source, event):
        if source == self:
            if event.type() == QEvent.KeyPress:
                if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
                    self.copy_media()

                elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_A:
                    try:
                        for thumb in self.search_results.thumbnails["current"]:
                                    thumb.update_highlight(highlight=True)
                    except:
                        pass

                elif event.key() == Qt.Key_Control:
                    self.set_ctrl(type=True)
                return True

            elif event.type() == QEvent.KeyRelease:
                if event.key() == Qt.Key_Control:
                    
                    self.set_ctrl(type=False)
                    print(len(self.selected_thumbnails))

        elif source == self.main_area:
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self.start_pos = event.pos()

                    if self.hover is False:
                        
                        pos_in_main = self.mapFrom(self, event.pos())
                           
                        self.drag_box.setGeometry(self.main_area.rect())
                        self.drag_box.start_point = self.drag_box.mapFromParent(pos_in_main)
                        self.drag_box.end_point = self.drag_box.start_point
                       
                        self.drag_box.show()
                        self.drag_box.raise_()
                        self.drag_box.update()

                        if self.ctrl is False:
                            self.selected_thumbnails.clear()
                            
                            self.unselect_all()

                        try:         
                            for thumb in self.search_results.thumbnails["current"]:
                                    thumb.toggle_ctrl()
                        except:
                            pass
                    
                    return True

            if event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    self.drag_box.hide()
                    return True

            if event.type() == QEvent.MouseMove:
                if self.hover is False:
                    if self.drag_box.isVisible():
                        
                        pos_in_main = self.mapFrom(self, event.pos())
                        
                        self.drag_box.end_point = self.drag_box.mapFromParent(pos_in_main)
                        self.drag_box.update()
                        
                        rect = self.drag_box.get_rect()
                        rect_in_main = QRect(self.drag_box.mapToParent(rect.topLeft()), rect.size())

                        viewport = self.scroll_area.viewport()
                        top_left_in_viewport = viewport.mapFrom(self.main_area, rect_in_main.topLeft())
                        bottom_right_in_viewport = viewport.mapFrom(self.main_area, rect_in_main.bottomRight())
                        
                        h_scroll = self.scroll_area.horizontalScrollBar().value()
                        v_scroll = self.scroll_area.verticalScrollBar().value()

                        top_left_in_viewport += QPoint(h_scroll, v_scroll)
                        bottom_right_in_viewport += QPoint(h_scroll, v_scroll)

                        rect_in_viewport = QRect(top_left_in_viewport, bottom_right_in_viewport)

                        try:
                            for thumb in self.search_results.thumbnails["current"]:
                                thumb_rect = thumb.geometry()

                                if rect_in_viewport.intersects(thumb_rect):
                                    thumb.intersect(intersect=True)
                                else:
                                    thumb.intersect(intersect=False)
                        except:
                            pass
                
                elif self.ctrl is False:
                    if event.buttons() == Qt.LeftButton:
                        if (event.pos() - self.start_pos).manhattanLength() < QApplication.startDragDistance():
                            return False

                        drag = QDrag(self)
                        drag.setMimeData(self.mime_data)
                        drag.setPixmap(self.preview_image)
                        drag.setHotSpot(event.pos() - self.start_pos)
                        drag.exec_(Qt.CopyAction | Qt.MoveAction)

                        return True

        return super().eventFilter(source, event)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        event.acceptProposedAction()

class ThumbnailIcon(QLabel):
    def __init__(self, path, pixmap, length, media_type, media_manager, parent=None):
        super().__init__(parent)

        self.path = path
        self.original_pixmap = pixmap
        self.length = length
        self.type = media_type

        self.media_manager = media_manager

        self._highlight = False
        self.toggle_state = False

        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border: none;")

        self.change_size(self.media_manager.img_size)

    def change_size(self, size):
        self.media_manager.img_size = size

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
                bg_rect = QRect(self.width() - rect_width - margin, margin,rect_width, rect_height)

                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(0, 0, 0, 180))
                painter.drawRect(bg_rect)
              
                painter.setPen(QColor("white"))
                painter.drawText(bg_rect, Qt.AlignCenter, self.length)

        if self._highlight is True:
            if self.type != "video":
                painter = QPainter(self)
                pen = QPen(Qt.cyan, 6)  
                painter.setPen(pen)
                rect = self.rect().adjusted(1, 1, -1, -1)  
                painter.drawRect(rect)

    def update_highlight(self, highlight=True):
       
        if highlight:
            if not self._highlight:
                self._highlight = True
                if self.path not in self.media_manager.selected_file_paths:
                    self.media_manager.selected_file_paths.append(self.path)
                self.update()

          
            if self not in self.media_manager.selected_thumbnails:
                self.media_manager.selected_thumbnails.add(self)
                print(len(self.media_manager.selected_thumbnails))

        else:
            if self._highlight:
                self._highlight = False
                if self.path in self.media_manager.selected_file_paths:
                    self.media_manager.selected_file_paths.remove(self.path)
                self.update()

            if self in self.media_manager.selected_thumbnails:
                self.media_manager.selected_thumbnails.remove(self)
                print(len(self.media_manager.selected_thumbnails))


    def intersect(self, intersect):

        highlight = (self.toggle_state is False) if intersect else (self.toggle_state is True)

        self.update_highlight(highlight=highlight)

    def toggle_ctrl(self):

        if self in self.media_manager.selected_thumbnails:

            self.toggle_state = True
        else:
            self.toggle_state = False

    def enterEvent(self, a0):
        self.media_manager.on_hover(1)
        return super().enterEvent(a0)
    
    def leaveEvent(self, a0):
        self.media_manager.on_hover(0)
        return super().leaveEvent(a0)
    
    def mousePressEvent(self, ev):

        self.media_manager.set_preview(self.original_pixmap, self.path)

        if self.media_manager.ctrl:

            if self._highlight:

                self.update_highlight(highlight=False)
            else:
                self.update_highlight(highlight=True)
                    
        return super().mousePressEvent(ev)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:

            if self.media_manager.ctrl is False:
            
                self.media_manager.display_media(self.path)

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
    
class DragSelectionBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_point = None
        self.end_point = None
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
  
    def get_rect(self):
        if self.start_point and self.end_point:
            return QRect(self.start_point, self.end_point).normalized()
        return QRect()

    def paintEvent(self, event):
        if self.start_point and self.end_point:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            rect = QRect(self.start_point, self.end_point).normalized()
            pen = QPen(QColor("white"), 1)
            brush = QColor(255, 255, 255, 80)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(rect)