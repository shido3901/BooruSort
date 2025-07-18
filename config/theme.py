class Theme():
    def __init__(self, theme=1):

        self.theme = theme

        match self.theme:
            case 0:

                self.ui = "color: black; background-color: white; border: 2px dashed red;"
                self.left_panel_ui = "color: black; background-color: white; border: 2px dashed red;"
                self.widgets = "color: black; background-color: yellow; border: 2px dashed red; "
                self.widgets_next = "color: black; background-color: green; border: 2px dashed red;"
                self.buttons = "QPushButton { color: white; background-color: #112233; border: none; font-size: 25px; } QPushButton:hover { color: #00FFFF; }"
                self.qlabel = "color: black; background-color: yellow; border: 2px dashed red; "
        
            case 1:

                self.ui = "color: white; background-color: #112233; border: 2px solid #1f618d; border-radius: 10px;"
                self.left_panel_ui = "color: white; background-color;"
                self.widgets = "color: white; background-color: #112233; border: 2px solid #1f618d; border-radius: 10px; border: none;" #<--- Maybe keep?
                self.widgets_next = "color: white; background-color: #010c1c; border: 2px solid #1f618d; border-radius: 10px;"
                self.buttons = "QPushButton { color: white; background-color: #112233; border: none; font-size: 25px; } QPushButton:hover { color: #00FFFF; }"
                self.qlabel = "color: white; font-size: 24px; font-weight: bold;"
