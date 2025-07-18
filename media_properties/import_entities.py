from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QObject, QThread, QTimer
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout, QProgressBar, QPushButton, QDesktopWidget, QSizePolicy, QMessageBox

from PIL import Image, ImageOps


import os, json, hashlib, ffmpeg, sqlite3
import subprocess
from datetime import datetime

from config.ui_config import ErrorDialog

class ImportEntities(QWidget):
    def __init__(self, tag_manager):
        super().__init__()
   
        self.tag_manager = tag_manager
        self.new_tag_list = self.tag_manager.new_tag_list
        self.initUI()

        self.import_queue = []

    def initUI(self):

        self.import_widget = QLabel()
        self.import_widget.setMinimumHeight(100)
        self.import_widget.setStyleSheet("background-color: #112233; border: 2px solid #1f618d; border-radius: 20px;")
        self.import_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.import_widget.setContentsMargins(30, 30, 30, 30)
        self.import_widget.setAcceptDrops(True)
        self.import_widget_layout = QVBoxLayout(self.import_widget)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap("import.png"))  # Set your image here later
        self.icon_label.setScaledContents(True)
        self.icon_label.setFixedSize(200, 150)  # Will expand later if needed
        self.icon_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icon_label.setStyleSheet("background-color: rgba(255,255,255,0.1);")
        self.import_widget_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        self.text_label = QLabel("drag and drop here\n or")
        self.text_label.setStyleSheet("color: white; font-size: 23px; border: none;")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.import_widget_layout.addWidget(self.text_label)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setFixedWidth(150)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.import_widget_layout.addWidget(self.browse_button, alignment=Qt.AlignCenter)

        self.import_widget.dragEnterEvent = self.dragEnterEvent
        self.import_widget.dropEvent = self.dropEvent

        self.tag_manager.tag_page_layout.addWidget(self.import_widget, stretch=13)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
           
            valid_files = [url for url in urls if self.is_image_or_video(url)]
            if valid_files: 
                event.acceptProposedAction()
            else:
                event.ignore()  
        else:
            event.ignore() 
  
    def is_image_or_video(self, url: QUrl) -> bool:
      
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
        
        file_path = url.toLocalFile()
        if file_path:
        
            file_extension = file_path.split('.')[-1].lower()
            if f'.{file_extension}' in image_extensions or f'.{file_extension}' in video_extensions:
                return True
        return False
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
      
            self.valid_files = [url for url in urls if self.is_image_or_video(url)]
            new_files = [url for url in self.valid_files if url not in self.import_queue]
            
            self.import_queue.extend(new_files)
        
            self.tag_manager.update_import_stats()
        
        else:
            event.ignore()

    def retrieve_import_length(self):
      
        length = len(self.import_queue)
        return length

    def retrieve_tag_list(self, tag_list):

        self.tag_list = tag_list

        if len(self.import_queue) > 0:
            
            self.final_import()

    def final_import(self):

        self.thumbnail_creation_thread = ThumbnailCreation(self.import_queue, self.tag_list)
        self.thumbnail_creation_thread.load_list.connect(self.tag_manager.load_list)
        self.thumbnail_creation_thread.load_list.connect(self.tag_manager.refresh_model)
        self.thumbnail_creation_thread.error_signal.connect(self.show_error_dialog)
        #self.thumbnail_creation_thread.refresh_list.connect(self.new_tag_list.load_new_tag_buttons)
        self.thumbnail_creation_thread.start()
        self.thumbnail_creation_thread.stop_timer.connect(self.stop_timer)

        self.elapsed_seconds = 0

        self.timer = QTimer()
        self.timer.setInterval(1000)  
        self.timer.timeout.connect(self.update_time)
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()
        print(f"imported in {self.elapsed_seconds} seconds")

    def update_time(self):
        self.elapsed_seconds += 1

    def show_error_dialog(self, error_list):
        summary = f"Failed to import {len(error_list)} files."
        dlg = ErrorDialog(summary, error_list)
        dlg.exec_()



class ThumbnailCreation(QThread):
    refresh_list = pyqtSignal()
    update_progress = pyqtSignal(int, int, str)
    stop_timer = pyqtSignal()
   
    load_list = pyqtSignal()

    error_signal = pyqtSignal(list)


    def __init__(self, entity_list, tag_list):
        super().__init__()

        self.entity_list = entity_list
        self.tag_list = tag_list

        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        self.video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']

    def run(self):

        with open('profiles.json', 'r') as f:

            selected_user = json.load(f)
            self.current_user = selected_user["current_profile"]

            self.nested_directory = f"{self.current_user}"
            os.makedirs(self.nested_directory, exist_ok=True)
                   
        thumbnail_directory = f"{self.current_user}/thumbnails"

        try:
            os.makedirs(thumbnail_directory)
        except FileExistsError:
            print('Directory already exists')

        self.conn = sqlite3.connect("booru.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT id FROM profiles WHERE profile_name = ?", (self.current_user,))
        user = self.cursor.fetchone()

        self.user_id = user[0]
        self.files = []
        self.invalid_files_list = []

        self.img_auto_tag = []
        self.video_auto_tag = []
        self.resolution_auto_tag = {}

        self.auto_tag_settings = {
            "auto_tag": True,
            "img_tag": True,
            "video_tag": True,

            "resolution": True,
            "highres": True,
            "4k": True,
            "hd": True,

            "orientation": True,
            "vertical": True,
            "horizontal": True,
            "square": True
        }

        self.files_length = len(self.entity_list)

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        invalid_files = 0
        MAX_SIZE = (256,256)

        for url in self.entity_list:

            temp_path = url.toLocalFile()
            file_path = os.path.abspath(temp_path)

            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()
            
            thumbnail_name = self.hash_filename(file_path, file_name)
            thumbnail_path = os.path.join(thumbnail_directory, thumbnail_name)

            try:
                if file_ext.lower() in self.image_extensions:
               
                    with Image.open(file_path) as img:
                        
                        if self.auto_tag_settings.get("auto_tag"):

                            self.img_auto_tag.append(file_name)

                            if self.auto_tag_settings.get("resolution"):
                                self.get_resolution(img, file_path)
                                
                        img = ImageOps.exif_transpose(img)
                        img.thumbnail(MAX_SIZE)
                        img.save(thumbnail_path)

                        type = "img"
                        length = 0

                elif file_ext.lower() in self.video_extensions:
                        
                    (
                    ffmpeg
                    .input(file_path, ss=1)
                    .filter('scale', MAX_SIZE[0], -1)
                    .output(thumbnail_path, vframes=1)
                    .run(quiet=True, overwrite_output=True)
                    )

                    video_metadata = self.get_video_info(file_path)
                    length = f"{int(video_metadata[2]) // 60:02d}:{int(video_metadata[2]) % 60:02d}"
                    type = "video"

                    print('saved thumbnail')

                    if self.auto_tag_settings.get("auto_tag"):
                        self.video_auto_tag.append(file_path)

                        if self.auto_tag_settings.get("resolution"):

                            resolution = [video_metadata[0], video_metadata[1]]
                            self.get_resolution(resolution, file_path)

                self.files.append((self.user_id, file_path, thumbnail_name, type, length, date_str))

            except Exception as e:
                print(f"Error for {file_path}: {e}")

                invalid_files += 1
                
                self.invalid_files_list.append((file_path, e))
                


        with self.conn:
            self.cursor.executemany("INSERT OR IGNORE INTO files (profile_id, path, thumbnail_name, type, length, date) VALUES (?, ?, ?, ?, ?, ?)", self.files)
            self.paths = [file[1] for file in self.files]

            placeholders = ','.join('?' for _ in self.paths)
            params = self.paths + [self.user_id]
            query = f"SELECT id, type FROM files WHERE path IN ({placeholders}) AND profile_id = ?"

            self.cursor.execute(query, params)
            self.rows = self.cursor.fetchall()
            self.file_ids = [row[0] for row in self.rows]

            placeholders = ','.join('?' for _ in self.tag_list)
            query = f"SELECT id FROM tags WHERE name IN ({placeholders}) AND profile_id = ?"
            params = self.tag_list + [self.user_id]

            self.cursor.execute(query, params)
            self.tag_ids = [row[0] for row in self.cursor.fetchall()]

            self.file_tag_pairs = [(file_id, tag_id) for file_id in self.file_ids for tag_id in self.tag_ids]
            self.insert_file_tags(self.file_tag_pairs)

            if self.auto_tag_settings.get("auto_tag"):
                self.check_auto_tag()
    
            placeholders = ','.join('?' for _ in self.tag_ids)
            self.cursor.execute(f"UPDATE tags SET count = (SELECT COUNT(*) FROM file_tags WHERE file_tags.tag_id = tags.id) WHERE id IN ({placeholders})", self.tag_ids)

            #print(f"RESOLUTION STATS IS GOING TO BE: {self.resolution_auto_tag}")

            if self.invalid_files_list:
                self.error_signal.emit(self.invalid_files_list)



                



        self.conn.close()
        self.stop_timer.emit()

        self.load_list.emit()
        self.refresh_list.emit()

    def insert_file_tags(self, pairs):
        self.cursor.executemany("INSERT OR IGNORE INTO file_tags (file_id, tag_id) VALUES (?, ?)", pairs)

    def check_auto_tag(self):
        
            #INTEGERS ARE TAMPORARY FOR NOW, THESE ARE TEMPORARY TAG IDS: 
            # 1	image  # 4 1080p       # 7 square
            # 2	video  # 5 vertical    # 8 highres
            # 3	4k     # 6 horizontal   
            
            tag_type = {
                "img_tag": ("img", 1),
                "video_tag": ("video", 2)
            }

            for setting_key, (type_str, tag_id) in tag_type.items():

                if self.auto_tag_settings.get(setting_key):
                    tag_file_ids = [(row[0], tag_id) for row in self.rows if row[1] == type_str]

                    if tag_file_ids:
                        self.insert_file_tags(tag_file_ids)
                        self.tag_ids.append(tag_id)

            tag_config = [
                ("4k",         3, "4k"),
                ("hd",         4, "hd"),
                ("vertical",   5, "v"),
                ("horizontal", 6, "h"),
                ("square",     7, "s"),
                ("highres",    8, "hr")
            ]

            for setting, tag_id, res in tag_config:
                if self.auto_tag_settings.get(setting):
                    file_list = self.resolution_auto_tag.get(res, [])

                    if file_list:
                        self.get_file_id(tag_id, file_list)

    def get_file_id(self, tag_id, file_list): #this also just sends to the db

        placeholders = ','.join('?' for _ in file_list)
        params = file_list + [self.user_id]
        query = f"SELECT id FROM files WHERE path IN ({placeholders}) AND profile_id = ?"

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        file_ids = [(row[0], tag_id) for row in rows]

        self.insert_file_tags(file_ids)
        self.tag_ids.append(tag_id)

    @staticmethod
    def hash_filename(file_path, original_name):
        base_name = os.path.splitext(original_name)[0]
        hash_object = hashlib.md5(file_path.encode('utf-8')).hexdigest()[:7]
        new_filename = f"{base_name}_{hash_object}.png"
        
        return new_filename
    
    def get_video_info(self, file_path):

            try:
                ffprobe_path = os.path.join("ffmpeg", "ffprobe.exe")
                cmd = [
                        ffprobe_path,
                        "-v", "error",
                        "-select_streams", "v:0",
                        "-show_entries", "stream=width,height",
                        "-show_entries", "format=duration",
                        "-of", "json",
                        file_path
                    ]

                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if result.returncode != 0:
                    print("Error:", result.stderr)
                    return None

                data = json.loads(result.stdout)

                try:
                    width = int(data["streams"][0]["width"])
                    height = int(data["streams"][0]["height"])
                    duration = float(data["format"]["duration"])
                    return width, height, duration
                except (KeyError, IndexError, ValueError) as e:
                    print("Failed to extract video metadata:", e)
                    return None
                
            except Exception as e:
                print(e)

    def get_resolution(self, img_or_res, file_path):
        #skip exif if img_or_res is a list (from video output) ex: img_or_res = [1920, 1080] ~line 265
        if isinstance(img_or_res, list):
            
            width, height = img_or_res
        else:

            #process image
            img = img_or_res
            img = ImageOps.exif_transpose(img)

            try:
                exif = img.getexif()
                orientation = exif.get(274) #orientation tag ID

                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
            except:
                pass
                    
            width, height = img.size

        if self.auto_tag_settings.get("resolution"):

            resolutions = [
                ("hr", 1600, 1200),
                ("4k", 3840, 2160),
                ("hd", 1920, 1080)
                
            ]

            for tag, w, h in resolutions:
                if tag == "hr" and width >= w and height >= h:
                    self.resolution_auto_tag.setdefault(tag, []).append(file_path)
                if width == w and height == h:
                    self.resolution_auto_tag.setdefault(tag, []).append(file_path)
                    break 

        if self.auto_tag_settings.get("orientation"):

            TOLERANCE = 0.125
            aspect_ratio = width / height

            if abs(aspect_ratio - 1.0) <= TOLERANCE:
                tag = "s"  #square
            elif aspect_ratio < 1.0:
                tag = "v"  #vertical
            else:
                tag = "h" #horizontal

            self.resolution_auto_tag.setdefault(tag, []).append(file_path)            

class ProgressBar(QWidget):
    def __init__(self, file_count):

        self.total_count = file_count
        super().__init__()
      
        self.setGeometry(500, 300, 400, 160)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")
        self.center()

        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 16px;")

        self.progress = QProgressBar()
        self.progress.setMaximum(self.total_count)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #00BCD4;
                width: 20px;
            }
        """)

        self.cancel_button = QPushButton("cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_progress)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()                  
        cp = QDesktopWidget().availableGeometry().center() 
        qr.moveCenter(cp)                           
        self.move(qr.topLeft())                    

    def update_progress(self, count, total, file_path_name):
            file_count = count
            total_count = total
       
            self.progress.setValue(file_count)
            self.progress.setFormat(f"{file_count}/{total_count}")
            self.label.setText(f"importing from\n{file_path_name}")
          
            if file_count == total_count:
                self.close()
   
    def cancel_progress(self):
       
        self.label.setText("Canceled")