from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton,  QHBoxLayout)
from PyQt5.QtCore import Qt

class TabBar(QWidget):
    def __init__(self, profile_config):
        super().__init__()

        self.profile_config = profile_config

        self.tab_list = []

        self.tab_layout = QHBoxLayout(self)

        self.ui_initiated = False

        self.init_ui()

    def clear(self):

        self.ui_initiated = False

        while self.tab_layout.count():
            item = self.tab_layout.takeAt(0)
            widget = item.widget()
            
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater() 

        self.tab_list.clear()

        self.init_ui()

    def load_tabs(self):

        self.profile_config_json = self.profile_config.load_json()

        current_tab = self.profile_config_json["tabs"]["current_tab"]

        if current_tab:

            tab_name, index = current_tab[0]

        tab_list = self.profile_config_json.get("tabs", {}).get("tab_list", [])

        for tab_name in tab_list:
            self.add_tab(text=tab_name)

        try:

            current_tab = self.tab_list[index]
            current_tab.update_ui()
            current_tab.highlight()

        except:
            pass

        self.ui_initiated = True

    def add_new_tab(self):

        if self.ui_initiated:

            text = "new tab"

            self.add_tab(text)
            
            self.profile_config_json["tabs"]["tab_list"].append(text)

            self.profile_config.dump_json(self.profile_config_json)

    def add_tab(self, text):

        self.new_tab = Tab(text, list=self.tab_list, profile_config=self.profile_config, json=self.profile_config_json)

        index = self.tab_layout.indexOf(self.create_tab)

        self.tab_layout.insertWidget(index, self.new_tab)
    
    def init_ui(self):

        self.create_tab = QPushButton("+")

        self.tab_layout.addWidget(self.create_tab)

        self.create_tab.setMinimumWidth(25)
        self.create_tab.setMinimumHeight(30)

        self.tab_layout.setContentsMargins(0, 0, 0, 0)

        self.tab_layout.addStretch()

        self.tab_layout.setSpacing(0)
     
        self.create_tab.clicked.connect(self.add_new_tab)
        self.create_tab.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: transparent;
                    border: none;
                    padding: 0 4px;
                    border-radius: 4px;   
                    margin: 0;
                    font-size: 14px;
                }
                QPushButton:hover {
                    color: cyan;
                    background-color: rgba(255, 255, 255, 60);  /* a bit more visible on hover */
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 80);  /* even more visible when clicked */
                }
            """)
        
class Tab(QWidget):
    def __init__(self, text, list, profile_config, json):
        super().__init__()

        self.text = text
        self.tab_list = list
   
        self.profile_config = profile_config
        self.profile_config_json = json

        self.setMaximumWidth(100)
        self.installEventFilter(self)
        
        self.tab_list.append(self)

        self.selected = True
        self.hover = False

        self.init_ui()
        
        
        self.update_ui()



    def update_ui(self):
        
       
        for tab in self.tab_list:
            
            tab.selected = (tab == self)
            tab.hover    = (tab == self)
            tab.highlight()

    def highlight(self):
            
        if self.selected:

            border_color = "1px solid cyan"
            border_right = "1px solid cyan"

            index = self.tab_list.index(self)

            self.profile_config_json["tabs"]["current_tab"].clear()
            self.profile_config_json["tabs"]["current_tab"].append((self.text, index))

            self.profile_config.dump_json(self.profile_config_json)

        else:
        
            border_color = "1px solid transparent"
            border_right = "1px solid rgba(255, 255, 255, 90)"

        self.tab.setStyleSheet(f"""
                color: white;
                background-color: rgba(255, 255, 255, {30 if self.hover else 0});
                padding: 4px;
                border-radius: 4px;
                border-top: {border_color};
                border-bottom: {border_color};
                border-left: {border_color};
                border-right: {border_right};
            """)
            
    def remove_tab(self):

        next_tab = None
        index = self.tab_list.index(self)

        if self.selected:

            if index + 1 < len(self.tab_list):
                next_tab = self.tab_list[index + 1]
                
            elif index + 1 > 1:
                next_tab = self.tab_list[index - 1]

            if next_tab and self.selected:
                next_tab.selected = True
                next_tab.hover    = True
                next_tab.highlight()
        
        self.profile_config_json["tabs"]["tab_list"].pop(index)
        
        self.profile_config.dump_json(self.profile_config_json)

        self.tab_list.remove(self)

        self.tab_layout.removeWidget(self)
        self.deleteLater()

    def mousePressEvent(self, a0):

        self.update_ui()
       
        print('clicked on', self.text)
        return super().mousePressEvent(a0)

    def enterEvent(self, a0):

        self.hover=True
        self.highlight()
    
        return super().enterEvent(a0)
    
    def leaveEvent(self, a0):

        if not self.selected:
            self.hover = False
            self.highlight()
      
        return super().leaveEvent(a0)
    
    def init_ui(self):

        self.tab  = QWidget()
        tab_icon  = QLabel("◯")
        tab_name  = QLabel(self.text)
        close_tab = QPushButton("x")

        self.tab_layout = QHBoxLayout(self.tab)
        layout          = QHBoxLayout(self)

        self.tab_layout.addWidget(tab_icon,  alignment=Qt.AlignLeft)
        self.tab_layout.addWidget(tab_name,  alignment=Qt.AlignLeft)
        self.tab_layout.addWidget(close_tab, alignment=Qt.AlignRight)
        layout         .addWidget(self.tab,  alignment=Qt.AlignLeft)
        
        self.tab_layout.setContentsMargins(0,0,5,0)
        layout         .setContentsMargins(0,0,0,0)
        
        self.tab_layout.setSpacing(3)
        layout         .setSpacing(0)

        tab_icon.setMaximumWidth(22)

        tab_icon.setStyleSheet("""
                background-color: transparent; 
                border-right: none; 
                border-top-right-radius: 0px; 
                border-bottom-right-radius: 0px;
            """)
        
        tab_name.setStyleSheet("""
                padding: 0px; 
                margin: 0px; 
                border-radius: 0px; 
                color: white; 
                background-color:transparent; 
                border-right: none; 
                border-left: none;
            """)

        close_tab.clicked.connect(self.remove_tab)
        close_tab.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: transparent;
                    border: none;
                    padding: 0 4px;
                    border-radius: 4px;
                    margin: 0;
                }
                QPushButton:hover {
                    color: cyan;
                    background-color: rgba(255, 255, 255, 60);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 80);
                }
            """)