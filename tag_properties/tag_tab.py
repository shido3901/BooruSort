from PyQt5.QtWidgets import (QVBoxLayout, QDialog, QDesktopWidget, QToolButton, QMessageBox,
                             QMenu, QAction, QPushButton, QStackedLayout, QTabWidget, QListView, 
                             QHBoxLayout, QLineEdit, QWidget, QSizePolicy, QColorDialog, QLayout, QListWidget, QListWidgetItem, QTableView, QAbstractItemView)

from PyQt5.QtGui import (QFont, QColor, QPainter, QPen, QFontMetrics, QPixmap, QPalette, QBrush)

from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QSize, QSortFilterProxyModel, QAbstractListModel, QVariant, QModelIndex, QEvent

class TagTab():
    def __init__(self, tm, db):

        self.tag_manager = tm
        self.booru_db = db

        self.tag_page = QWidget()
        self.tag_page.setMinimumHeight(100)
   
        self.tag_page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tag_page_layout = QVBoxLayout(self.tag_page)
        self.tag_page_layout.setContentsMargins(0,10,0,0)

        self.tag_page_layout.addStretch()

        self.tag_manager.right_widget.addTab(self.tag_page, "tags")

        self.initUI()

    def initUI(self):
        self.tag_page_layout.addWidget(self.tag_manager.tag_tab_box.tag_window_widget, stretch=12)
        self.tag_page_layout.addWidget(self.tag_manager.tag_tab_box.import_widget, stretch=3)

    def import_tag_list(self, tag_list):
   
        new_list = [(tag_name, category) for tag_name, category in tag_list]

        self.booru_db.add_tags(new_list)
        
        if new_list:

            import_list = [tag_name for tag_name, _ in tag_list]
            self.tag_manager.import_entities.retrieve_tag_list(import_list)


