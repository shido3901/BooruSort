from PyQt5.QtWidgets import QMessageBox, QCheckBox, QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QWidget, QLayout, QSizePolicy, QHBoxLayout, QLineEdit, QProgressBar, QGridLayout, QScrollArea
from PyQt5.QtCore import Qt, QRect, QTimer, QPoint
from PyQt5.QtGui import QGuiApplication, QPainter, QColor, QPen, QFontMetrics

import json, os



class Theme:
    _instance = None  

    def __new__(cls, theme="booru"):  
        if cls._instance is None:
            cls._instance = super(Theme, cls).__new__(cls)
            cls._instance.theme = theme  
            cls._instance._set_colors() 
        return cls._instance

    def _set_colors(self):
        
        match self.theme:
            case "booru":
                self.light_color  = "#112233"
                self.dark_color   = "#010c1c"
                self.border_color = "#1f618d"

            case "dark":
                self.light_color  = "#333333"
                self.dark_color   = "#111111"
                self.border_color = "#555555"

            case "debug":
                self.light_color  = "yellow"
                self.dark_color   = "green"
                self.border_color = "red"

        self.background_color_light = f"background-color: {self.light_color};"
        self.background_color_dark = f"background-color: {self.dark_color};"
        self.border_color_style = f"border: 1px solid {self.border_color};"

    def get_theme(self):
        
        return self.theme

    def set_theme(self, theme):
       
        self.theme = theme
        self._set_colors()



class BooruWidget(QWidget):
    def __init__(self, layout_type, bg_color, border_color, border_radius=False):
        super().__init__()

        self.setStyleSheet(
            bg_color +
            border_color +
            ("border-radius: 8px;" if border_radius else "")
        )

        match layout_type:
            case "QVBox":
                layout = QVBoxLayout(self)
            case "QHBox":
                layout = QHBoxLayout(self)
            case "QGrid":
                layout = QGridLayout(self)
                self.setStyleSheet("background-color: None;")

        self.setContentsMargins(0,0,0,0)

       

        self.BooruLayout = layout

        WIDGET = QWidget(self)
        self._layout=QVBoxLayout(WIDGET)
        

        self.BooruLayout.addWidget(WIDGET)

class LightWidget(BooruWidget):
    def __init__(self, layout_type, border_radius=False):
        theme = Theme()
        super().__init__(
            layout_type,
            theme.background_color_light,
            theme.border_color_style,
            border_radius
        )


class DarkWidget(BooruWidget):
    def __init__(self, layout_type, border_radius=False):
        theme = Theme()
        super().__init__(
            layout_type,
            theme.background_color_dark,
            theme.border_color_style,
            border_radius
        )
        
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

class SearchBar(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent_widget = parent
       
        self.setPlaceholderText("search tags... ex: black_cat")
        self.setStyleSheet("color:white;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.search_results = QWidget(self.parent_widget)
        self.search_results.setStyleSheet("background-color: lightblue; padding: 10px; border-radius: 3px;")
        self.search_results.setFixedSize(200,300)
        self.search_results.hide()

        self.textChanged.connect(self.on_text_changed)

    def on_text_changed(self, text):
       
        if text:
            search_bar_position = self.mapTo(self.parent_widget, QPoint(0, 0))

            self.search_results.move(search_bar_position.x(), search_bar_position.y() + self.height())
            self.setStyleSheet("color:white; border-color: white;")

            self.search_results.show()
        else:
            self.setStyleSheet("color:white;")
            self.search_results.hide()

    def eventFilter(self, a0, a1):


        return super().eventFilter(a0, a1)

class Scroll(QScrollArea):
    def __init__(self):
        super().__init__()

        self.setWidgetResizable(True)
        self.setStyleSheet("""
        
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

 
        


       

     
