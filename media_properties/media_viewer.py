
from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget, QApplication, QApplication, QVBoxLayout, QLayout, QScrollArea, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, QUrl, QMimeData, QSize, QObject, QThreadPool, QRunnable, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QImage, QDrag, QDragEnterEvent, QDropEvent

from config.booru_ui import DragSelectionBox, Scroll

class MediaViewer(QWidget):
    def __init__(self, media_area):
        super().__init__()

        self.media_area = media_area

        self.installEventFilter(self)
        self.media_area.installEventFilter(self)
        


        
        
   

        self.init_ui()

    def init_ui(self):
        self.drag_box = DragSelectionBox(self.media_area)
        self.scroll_area = Scroll()
        
        main_layout = QWidget()
        main_layout.setStyleSheet("background-color: red")
        main_layout.setMinimumSize(10,10)
      
        self.scroll_area.setWidget(main_layout)

        main_layout_layout = QVBoxLayout(main_layout)
  



        container = QWidget()
        container.setMinimumSize(10,10)
        container.setStyleSheet("background-color: red")
        #self.media_layout = FlowLayout(container, spacing=20, justify_rows=True)
       
        #container.setLayout(self.media_layout)

        main_layout_layout.addWidget(container)

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

                elif event.key() == Qt.Key_Delete:
                    self.delete_media()

                elif event.key() == Qt.Key_Control:
                    self.set_ctrl(type=True)
                return True

            elif event.type() == QEvent.KeyRelease:
                if event.key() == Qt.Key_Control:
                    
                    self.set_ctrl(type=False)

        elif source == self.media_area:
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self.setFocus()
                    self.start_pos = event.pos()

                 
                        
                    pos_in_main = self.mapFrom(self, event.pos())
                        
                    self.drag_box.setGeometry(self.media_area.rect())
                    self.drag_box.start_point = self.drag_box.mapFromParent(pos_in_main)
                    self.drag_box.end_point = self.drag_box.start_point
                    
                    self.drag_box.show()
                    self.drag_box.raise_()
                    self.drag_box.update()

                      
                    
                    return True

            if event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    self.drag_box.hide()
                    return True

            if event.type() == QEvent.MouseMove:
                
                #if self.drag_box.isVisible():
                    
                    pos_in_main = self.mapFrom(self, event.pos())
                    
                    self.drag_box.end_point = self.drag_box.mapFromParent(pos_in_main)
                    self.drag_box.update()
                    
                    rect = self.drag_box.get_rect()
                    rect_in_main = QRect(self.drag_box.mapToParent(rect.topLeft()), rect.size())

                    #viewport = self.scroll_area.viewport()
                    #top_left_in_viewport = viewport.mapFrom(self.media_area, rect_in_main.topLeft())
                    #bottom_right_in_viewport = viewport.mapFrom(self.media_area, rect_in_main.bottomRight())
                    
                    #h_scroll = self.scroll_area.horizontalScrollBar().value()
                    #v_scroll = self.scroll_area.verticalScrollBar().value()

                    #top_left_in_viewport += QPoint(h_scroll, v_scroll)
                    #bottom_right_in_viewport += QPoint(h_scroll, v_scroll)

                    #rect_in_viewport = QRect(top_left_in_viewport, bottom_right_in_viewport)

                
                
                    """if event.buttons() == Qt.LeftButton:
                        if (event.pos() - self.start_pos).manhattanLength() < QApplication.startDragDistance():
                            return False

                        drag = QDrag(self)
                        drag.setMimeData(self.mime_data)
                        drag.setPixmap(self.preview_image)
                        drag.setHotSpot(event.pos() - self.start_pos)
                        drag.exec_(Qt.CopyAction | Qt.MoveAction)

                        return True"""

        return super().eventFilter(source, event)
        