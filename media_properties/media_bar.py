from PyQt5.QtWidgets import QWidget, QSizePolicy, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton
from config.booru_ui import SearchBar

class MediaBar(QWidget):
    def __init__(self, parent, media_viewer):
        super().__init__(parent)

        
        self.setMinimumHeight(25)
        self.setMaximumHeight(40)

        media_bar_layout = QHBoxLayout(self)
        media_bar_layout.setContentsMargins(0,0,0,0)
        media_bar_layout.setSpacing(2)

        tag_button = QPushButton("tags")
        tag_button.setStyleSheet("color:white;")

        search_button = QPushButton("search")
        search_button.setStyleSheet("color:white;")


        change_size = QPushButton("size")
        change_size.setStyleSheet("color:white;")


        change_layout = QPushButton("layout")
        change_layout.setStyleSheet("color:white;")
        

        line_edit = SearchBar(parent)
        media_bar_layout.addWidget(tag_button)

        media_bar_layout.addWidget(line_edit)

        media_bar_layout.addWidget(search_button)
        
        media_bar_layout.addWidget(change_size)
        media_bar_layout.addWidget(change_layout)

     
        
        




        