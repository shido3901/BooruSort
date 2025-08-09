from PyQt5.QtWidgets import QWidget, QSizePolicy, QHBoxLayout, QVBoxLayout, QLineEdit
from config.booru_ui import SearchBar

class MediaBar(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)

        
        self.setMinimumHeight(30)
        self.setMaximumHeight(45)

        media_bar_layout = QVBoxLayout(self)
        media_bar_layout.setContentsMargins(0,0,0,0)

        self.line_edit = SearchBar(main_window)
        media_bar_layout.addWidget(self.line_edit)



        