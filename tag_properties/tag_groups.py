from PyQt5.QtWidgets import (QVBoxLayout, QDialog, QDesktopWidget, QToolButton, QMessageBox,
                             QMenu, QAction, QPushButton, QStackedLayout, QTabWidget, QListView, 
                             QHBoxLayout, QLineEdit, QWidget, QSizePolicy, QColorDialog, QLayout, QListWidget, QListWidgetItem, QTableView, QAbstractItemView)

from PyQt5.QtGui import (QFont, QColor, QPainter, QPen, QFontMetrics, QPixmap, QPalette, QBrush)

from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QSize, QSortFilterProxyModel, QAbstractListModel, QVariant, QModelIndex, QEvent

from tag_properties.tagbox import TagBox

class TagGroups():
    def __init__(self, tm, db):

        self.booru_db = db

        self.tag_manager = tm

        self.category_page = QWidget()
        self.category_page.setMinimumHeight(100)
        self.category_page.setStyleSheet("background-color: black;")
   
        self.category_page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.category_page_layout = QVBoxLayout(self.category_page)
        self.category_page_layout.setContentsMargins(0,10,0,0)

        self.category_page_layout.addStretch()

        self.tag_manager.right_widget.addTab(self.category_page, "groups")

     
       
        self.load = True

        print('is true')

        


    def show_page(self):
            
            if self.load == True:

                self.category_page_layout.addWidget(self.tag_manager.tag_group_top_box.tag_window_widget, stretch=12)
                self.category_page_layout.addWidget(self.tag_manager.tag_group_top_box.import_widget, stretch=3)
                self.category_page_layout.addWidget(self.tag_manager.tag_group_bottom_box.tag_window_widget, stretch=13)

            self.load = False

    #TO DO: Still add new tags to db if created in tag_groups. check if tag is in db and add new before making parent/child
    #TO DO: Still add new tags to db if created in tag_groups. check if tag is in db and add new before making parent/child
    #TO DO: Still add new tags to db if created in tag_groups. check if tag is in db and add new before making parent/child
    #TO DO: Still add new tags to db if created in tag_groups. check if tag is in db and add new before making parent/child


    def import_group_list(self, parent_list, child_list):
 
        parent_name_list = [name for (name, _) in parent_list.keys()]
        child_name_list = [name for (name, _) in child_list.keys()]

        full_list = parent_name_list + child_name_list
     #implement later "if tag name is not in tag list, create new tag"

        tag_name_list_ids = self.booru_db.get_tag_id(full_list)
     
        tag_name_to_id = {tag_name: tag_id for tag_id, tag_name in tag_name_list_ids}

        parent_id_list = [tag_name_to_id[name] for name in parent_name_list if name in tag_name_to_id]
        child_id_list  = [tag_name_to_id[name] for name in child_name_list if name in tag_name_to_id]
                  
        group_list = [(parent_tag_id, child_tag_id) for parent_tag_id in parent_id_list for child_tag_id in child_id_list]

        
        
        self.booru_db.add_group(group_list)

  
      
        