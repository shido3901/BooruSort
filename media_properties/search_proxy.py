from PyQt5.QtWidgets import QStyledItemDelegate, QStyle

from PyQt5.QtGui import QColor, QFontMetrics

from PyQt5.QtCore import (Qt, QRect, QSortFilterProxyModel, QEvent, QVariant, 
                          QModelIndex, QAbstractListModel, pyqtSignal, QRegExp)      



class ItemModel(QAbstractListModel):
    def __init__(self, tag_dict=None):
        super().__init__()
        self._items = list(tag_dict.items()) if tag_dict else []

    def refresh(self, new_data):
       
        self.beginResetModel()
        self._items = list(new_data.items())
        self.endResetModel()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._items)):
            return QVariant()

        tag, data = self._items[index.row()]

        if role == Qt.DisplayRole:
            return f"{tag} ({data['count']})"

        elif role == Qt.TextColorRole:
            return QColor(data["color"])

        elif role == Qt.UserRole:
            return {"name": tag, **data}
        
        return QVariant()

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

class FilterProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def filterAcceptsRow(self, row, parent):
        index = self.sourceModel().index(row, 0, parent)
        item = self.sourceModel().data(index, Qt.UserRole)
     
        self.filter_text = self.filterRegExp().pattern().lower().replace("_", " ")
        name = item["name"].lower().replace("_", " ")

        return self.filter_text in name
    
    def lessThan(self, left, right):
        left_data = self.sourceModel().data(left, Qt.UserRole)
        right_data = self.sourceModel().data(right, Qt.UserRole)


        left_name = left_data["name"].lower()
        right_name = right_data["name"].lower()

        # prioritize items that start with the filter text
        left_starts = left_name.startswith(self.filter_text)
        right_starts = right_name.startswith(self.filter_text)

        if left_starts and not right_starts:
            return True
        if right_starts and not left_starts:
            return False

        # a-z sort
        return left_name < right_name


class ItemDelegate(QStyledItemDelegate):
    tagModified = pyqtSignal(str, int)


    def __init__(self, show_buttons=True):
        super().__init__()

        self.show_buttons = show_buttons
        self.last_button_rects = {}


    def paint(self, painter, option, index):

        
        item = index.data(Qt.UserRole)
        if not item:
            return

        painter.save()

        if option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, QColor("#446688"))
           

        rect = option.rect
        name = item["name"]
        count = str(item["count"])
        color = QColor(item["color"])

        font = option.font
        font.setPointSize(10)
        painter.setFont(font)
        metrics = QFontMetrics(font)

        padding = 8
        x = rect.left() + padding
        center_y = rect.center().y() + metrics.ascent() // 2

        if self.show_buttons:
            plus_width = metrics.horizontalAdvance("+")
            minus_width = metrics.horizontalAdvance("-")
            
            plus_rect = QRect(x, rect.top(), plus_width + 6, rect.height())
            painter.setPen(color)
            painter.drawText(plus_rect, Qt.AlignVCenter, "+")
            x += plus_width + padding

            minus_rect = QRect(x, rect.top(), minus_width + 6, rect.height())
            painter.setPen(color)
            painter.drawText(minus_rect, Qt.AlignVCenter, "-")
            x += minus_width + padding

            name_rect = QRect(x, rect.top(), rect.right() - x, rect.height())

            self.last_button_rects[index] = {
                "plus": plus_rect,
                "minus": minus_rect,
                "name": name_rect,
            }
            
        painter.setPen(color)
        painter.drawText(x, center_y, name)
        x += metrics.horizontalAdvance(name) + padding

        painter.setPen(Qt.gray)
        painter.drawText(rect.right() - metrics.horizontalAdvance(count) - padding, center_y, count)

        painter.restore()
       

    def editorEvent(self, event, model, option, index):

        if not self.show_buttons or event.type() != event.MouseButtonRelease:
            return False

        if index not in self.last_button_rects:
            return False

        tag_name = index.data(Qt.UserRole)["name"]
        click_pos = event.pos()
        rects = self.last_button_rects[index]

        if rects["plus"].contains(click_pos):
            self.ignore_index = index
            self.tagModified.emit(tag_name, +1)
            return True
        elif rects["minus"].contains(click_pos):
            self.tagModified.emit(tag_name, -1)
            return True
        elif rects["name"].contains(click_pos):
            self.tagModified.emit(tag_name, 0)
            return True
            

        return False
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            pos = event.pos()
            view = obj.parent()

            index = view.indexAt(pos)
            if index.isValid() and index in self.last_button_rects:
                rects = self.last_button_rects[index]
                if rects:
                    if rects["plus"].contains(pos) or rects["minus"].contains(pos):
                        view.viewport().setCursor(Qt.PointingHandCursor)
                        return False

            view.viewport().unsetCursor()
        return super().eventFilter(obj, event)

