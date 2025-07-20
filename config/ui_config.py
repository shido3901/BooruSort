from PyQt5.QtWidgets import QMessageBox, QCheckBox, QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QWidget, QLayout, QSizePolicy, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt, QRect, QSize, QPoint, QEvent
from PyQt5.QtGui import QPalette, QColor

class MessageBox:
    ICONS = {
        "info": QMessageBox.Information,
        "warning": QMessageBox.Warning,
        "error": QMessageBox.Critical,
        "question": QMessageBox.Question,
        "none": QMessageBox.NoIcon,
    }

    def __init__(self, text, box_type="info", title="Message"):
        self.text = text
        self.title = title
        self.icon = self.ICONS.get(box_type.lower(), QMessageBox.Information)

    def show(self):
        msg = QMessageBox()
        msg.setWindowTitle(self.title)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setText(self.text)
        msg.setIcon(self.icon)
        msg.setStandardButtons(QMessageBox.Ok)
        return msg.exec_()
    
    @staticmethod
    def confirm(text="Are you sure?", title="Confirm", checkbox_text=None):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)

        checked = False
        if checkbox_text:
            checkbox = QCheckBox(checkbox_text)
            msg.setCheckBox(checkbox)

        result = msg.exec_()

        if checkbox_text:
            checked = msg.checkBox().isChecked()

        return result == QMessageBox.Yes, checked
    


class ErrorDialog(QDialog):
    def __init__(self, summary_text, error_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Errors")
        self.setMinimumSize(700, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)

        label = QLabel(summary_text)
        layout.addWidget(label)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)

        error_lines = [
        f'{i+1}. <span style="color:blue;">{file_path}</span>: &gt;{str(error)}&lt;'
        for i, (file_path, error) in enumerate(error_list)
        ]
        text_edit.setHtml("<br>".join(error_lines))


        layout.addWidget(text_edit)

        button = QPushButton("Close")
        button.clicked.connect(self.accept)
        layout.addWidget(button)

