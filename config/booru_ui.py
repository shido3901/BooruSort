from PyQt5.QtWidgets import QMessageBox, QCheckBox, QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QWidget, QLayout, QSizePolicy, QHBoxLayout, QLineEdit, QProgressBar
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
                self.light_color = "#112233"
                self.dark_color = "#010c1c"
                self.border_color = "#1f618d"
            case "dark":
                self.light_color = "#333333"
                self.dark_color = "#111111"
                self.border_color = "#555555"

            case "debug":
                self.light_color = "yellow"
                self.dark_color = "green"
                self.border_color = "red"

        self.background_color_light = f"background-color: {self.light_color};"
        self.background_color_dark = f"background-color: {self.dark_color};"
        self.border_color_style = f"border: 1px solid {self.border_color};"

    def get_theme(self):
        
        return self.theme

    def set_theme(self, theme):
       
        self.theme = theme
        self._set_colors()





class LightWidget(QWidget):
    def __init__(self, border_radius=False):
        super().__init__()

        theme = Theme()  
        self.setStyleSheet(theme.background_color_light + theme.border_color_style + (f"border-radius: 8px;" if border_radius is True else ""))


class DarkWidget(QWidget):
    def __init__(self, border_radius=False):
        super().__init__()

        theme = Theme()  
        self.setStyleSheet(theme.background_color_light + theme.border_color_style + (f"border-radius: 8px;" if border_radius is True else ""))

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
 
        


       

     

