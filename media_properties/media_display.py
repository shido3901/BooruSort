from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget, QDesktopWidget, QApplication, QSizePolicy, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QPixmap, QFontMetrics, QFont
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QTimer
from PIL import Image, ImageOps
import os, cv2

dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "booru_mpv")
os.environ["PATH"] = dll_path + os.pathsep + os.environ["PATH"]

import mpv

class MediaDisplayWindow(QWidget):

    load_images = pyqtSignal(str)
    def __init__(self, file_path, tag_name, booru_db):
        super().__init__()

        self.file_path = file_path

        print(f"TRYING TO DISPLAY {self.file_path}")

        self.booru_db = booru_db
        self.font = QFont('Roboto')
        self.setWindowTitle(f"{tag_name} - {file_path}")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.is_video = False
        self.font = QFont('Roboto')

        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        self.max_window_width = int(screen_width)
        self.min_window_width = int(screen_width * 0.20)
        self.window_height = int(screen_height * 0.60)

        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        self.video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
        
     
        file_ext = os.path.splitext(self.file_path)[1].lower()

        if file_ext in self.image_extensions:
            try:

                self.img = Image.open(self.file_path)
                self.img = ImageOps.exif_transpose(self.img)
           
                self.img_width = self.img.width
                self.img_height = self.img.height

            except Exception as e:
                self.img_width = "?"
                self.img_height = "?"

                print(e)

        elif file_ext in self.video_extensions:
            try:
                cap = cv2.VideoCapture(file_path)
                self.img_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.img_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            except:
                self.img_width = "?"
                self.img_height = "?"

        else:
            self.img_width = "?"
            self.img_height = "?"

        self.scale = self.window_height / self.img_height
        self.scaled_width = int(self.img_width * self.scale)

        x = (screen_width - self.scaled_width) // 2
        y = (screen_height - self.window_height) // 2

        self.setGeometry(x, y, self.min_window_width, self.window_height)
        self.setMaximumHeight(self.window_height)
        self.setStyleSheet("background-color: #112233;")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)


        self.tag_list = QWidget()
        self.tag_list.setMaximumHeight(self.window_height)
        self.tag_list.setMinimumWidth(250)
    
        self.tag_list.setStyleSheet("background-color: #112233;")
        self.layout.addWidget(self.tag_list, stretch=1)
        self.tag_list_layout = QVBoxLayout()
        
        self.tag_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.tag_list.setLayout(self.tag_list_layout)
        self.tag_list_layout.addStretch()

        self.entity_area = QWidget()
        self.entity_area_layout = QVBoxLayout()
        self.entity_area.setLayout(self.entity_area_layout)
        self.entity_area.setStyleSheet("background-color: #112233;")
        self.entity_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.entity_area_layout.addStretch()
        self.layout.addWidget(self.entity_area)

    
        result = self.booru_db.get_item_info(file_path)
        #remember to attatch profile id under here ======vvvvvvvv====
        
        
        if result:
            print("File exists:", result)
        else:
            print("No file found with that path.")

        file_tags = self.booru_db.get_file_tag_info(file_path)

        color = "#FFFFFF"
        if file_tags:

            print(f"file tags are: {file_tags}")
            for tag_id, name, count in file_tags:
                self.create_new_tag_buttons(name, color, count)

        self.entity_options = QWidget()
        self.entity_options.setMinimumHeight(45)

        self.entity_options.setStyleSheet("background-color: green;")
        self.entity_options_layout = QHBoxLayout()
        self.entity_options.setLayout(self.entity_options_layout)
        self.entity_area_layout.addWidget(self.entity_options)
      
        self.open_in_player = QPushButton("Open in player")
        self.open_in_player.setMaximumWidth(100)
        self.open_in_player.setMinimumHeight(20)
        self.open_in_player.clicked.connect(lambda: self.open_to_player(file_path))
        self.entity_options_layout.addWidget(self.open_in_player)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.save_text)

        

        self.media_info = QLabel(f"added:\n{result[4]}")
        self.media_info.setStyleSheet("color: white;" "font-size: 25px")
        self.media_info.setMinimumWidth(80)
        self.media_info.setMaximumHeight(100)
        self.tag_list_layout.addWidget(self.media_info, Qt.AlignBottom)
        

        self.resolution_widget = QLabel(f"resolution:\n{self.img_width}x{self.img_height}")
        self.resolution_widget.setStyleSheet("color: white;" "font-size: 25px")
        self.resolution_widget.setMinimumWidth(80)
        self.resolution_widget.setMaximumHeight(100)
        self.tag_list_layout.addWidget(self.resolution_widget, Qt.AlignBottom)

        self.notes_box = QTextEdit()
        self.notes_box.setStyleSheet("color: white;")
        self.notes_box.setMinimumWidth(100)
        self.notes_box.setMaximumHeight(400)
        self.notes_box.textChanged.connect(self.on_text_changed)

        notes = result[5]
        if notes:
            self.notes_box.setText(notes)

        self.notes_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        self.tag_list_layout.addWidget(self.notes_box, stretch=1)

        



        if file_ext in self.image_extensions:

            pixmap = QPixmap(self.file_path)
            scaled_pixmap = pixmap.scaled(self.max_window_width, self.window_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            label = QLabel()
            label.setPixmap(scaled_pixmap)
            label.setMinimumHeight(self.window_height)
            label.setMaximumWidth(self.max_window_width)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            label.setCursor(Qt.PointingHandCursor)
            self.entity_area_layout.addWidget(label)

        elif file_ext in self.video_extensions:
            self.is_video = True
        
            self.video_widget = QWidget(self)
            self.video_widget.setStyleSheet("background-color: white;")
            self.video_widget.setAttribute(Qt.WA_DontCreateNativeAncestors)
            self.video_widget.setAttribute(Qt.WA_NativeWindow)
            
            self.video_widget.setMinimumHeight(self.window_height)
            self.video_widget.setMinimumWidth(self.scaled_width)
            self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.video_widget.installEventFilter(self)
        
            self.video_widget.setMouseTracking(True)
            self.entity_area_layout.addWidget(self.video_widget, Qt.AlignTop)

            self.player = mpv.MPV(
                                wid=str(int(self.video_widget.winId())), 
                                osc=True,
                                input_default_bindings=True,
                                loop='inf',
                                loglevel='debug',
                                )
            
            self.player.play(file_path)


        else:
            print('Not found?')


    def on_text_changed(self):
        self.timer.start(1000)

    def save_text(self): #Finish this later
       
        self.booru_db.update_notes_box(self.notes_box.toPlainText(), self.file_path)


    def open_to_player(self, file_path):
     
        os.startfile(file_path)
        self.close()
            
    def eventFilter(self, source, event):
        if source == self.video_widget and event.type() == QEvent.MouseMove:
            x = event.x()
            y = event.y()
            self.player.command('mouse', x, y)
        return super().eventFilter(source, event)

    def mousePressEvent(self, event):

            if self.is_video == True:
                if event.button() == Qt.LeftButton:
                    self.player.command("keydown", "MOUSE_BTN0")
                elif event.button() == Qt.RightButton:
                    self.player.command("keydown", "MOUSE_BTN2")
                else:
                    super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.is_video == True:
            if event.button() == Qt.LeftButton:
                self.player.command("keyup", "MOUSE_BTN0")  
            elif event.button() == Qt.RightButton:
                self.player.command("keyup", "MOUSE_BTN2")
            else:
                super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if self.is_video == True:
            if event.angleDelta().y() > 0:
                self.player.command("keypress", "MOUSE_BTN3")  
            else:
                self.player.command("keypress", "MOUSE_BTN4")


    def closeEvent(self, event):
        if self.is_video == True:
            if hasattr(self, 'player') and self.player is not None:
                try:
                    self.player.terminate()
                except Exception as e:
                    print(f"Error terminating MPV: {e}")
            event.accept()

    def create_new_tag_buttons(self, tag_name, color, count):
                
        self.tag_name = tag_name
       
        tag_button_widget = QWidget()
        tag_button_widget.setFixedHeight(38)
        tag_button_widget.setStyleSheet(
                                        "background-color: #112233")
        
        tag_button_layout = QHBoxLayout()
        tag_button_layout.setContentsMargins(0,0,0,5)
        tag_button_widget.setLayout(tag_button_layout)

        tag_button = QPushButton(self.tag_name)
        tag_button.setCursor(Qt.PointingHandCursor)
        tag_button.setFont(self.font)
        tag_button.setFixedHeight(34)
        tag_button.setMinimumWidth(150)
        tag_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tag_button_layout.addWidget(tag_button, alignment=Qt.AlignLeft)

        self.tag_list_layout.insertWidget(0, tag_button_widget)

        metrics = QFontMetrics(tag_button.font())
        elided_text = metrics.elidedText(tag_name, Qt.ElideRight, tag_button.width() - 50)
        tag_button.setText(elided_text)
        tag_button.setStyleSheet(f"""
                            QPushButton {{
                                color: {color};
                                background-color: #112233;
                                border: none;
                                max-width: 100px;
                                text-align: left;
                                font-size: 25px;
                            }}
                            QPushButton:hover {{
                                color: #00FFFF;
                            }}
                        """)

        tag_button_layout.addWidget(tag_button, alignment=Qt.AlignLeft)
        tag_button_layout.addStretch()
                
        #tag_button.clicked.connect(lambda checked=False, t=tag_name: self.add_to_recent(t))
        tag_button.clicked.connect(lambda: self.load_images.emit(tag_name))
        #tag_button.rightClicked.connect(lambda t=tag_name: self.delete_tag(t, entity_count))

        if count >= 1000:
                entity_display = f"{count / 1000:.1f}k"
        else: 
            entity_display = count

        tag_entity_count = QLabel(str(entity_display))
        tag_entity_count.setFont(self.font)
        tag_entity_count.setMinimumWidth(15)
        tag_entity_count.setFixedHeight(40)
        tag_entity_count.setStyleSheet("color: #B0B0B0; background-color: #112233; border: none; font-size: 23px; }")
        tag_button_layout.addWidget(tag_entity_count, alignment=Qt.AlignRight)


 