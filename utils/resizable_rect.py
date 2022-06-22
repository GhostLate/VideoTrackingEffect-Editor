import operator

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QSize, QPoint, Qt
from PySide6.QtGui import QCursor


class ResizableRect(QtWidgets.QWidget):
    mousePressPos: QPoint

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.onBorder = False
        self.resizing = False
        self.moving = False
        self.setMouseTracking(True)
        self.show()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.drawRoundedRect(0, 0, self.size().width(), self.size().height(), 2, 2)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            self.mousePressPos = event.position().toPoint()
            self.moving = True
        elif event.button() == QtCore.Qt.MouseButton.LeftButton and self.onBorder:
            self.resizing = True

    def mouseMoveEvent(self, event):
        onLeftBorder = abs(event.position().toPoint().x()) < 10
        onRightBorder = abs(event.position().toPoint().x() - self.size().width()) < 10
        onTopBorder = abs(event.position().toPoint().y()) < 10
        onBottomBorder = abs(event.position().toPoint().y() - self.size().height()) < 10
        self.onBorder = onLeftBorder or onRightBorder or onTopBorder or onBottomBorder

        if (onLeftBorder and onBottomBorder) or (onRightBorder and onTopBorder):
            self.setCursor(QCursor(Qt.SizeBDiagCursor))
        elif (onRightBorder and onBottomBorder) or (onLeftBorder and onTopBorder):
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        elif onLeftBorder or onRightBorder:
            self.setCursor(QCursor(Qt.SizeHorCursor))
        elif onTopBorder or onBottomBorder:
            self.setCursor(QCursor(Qt.SizeVerCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

        if event.buttons() & QtCore.Qt.MouseButton.RightButton and self.moving:
            self.move_save(event, event.position().toPoint() - self.mousePressPos + self.pos())

        elif event.buttons() & QtCore.Qt.MouseButton.LeftButton and self.resizing:
            mouseMovePos = event.position().toPoint()
            point_1, point_2 = QPoint(0, 0), QPoint(*self.size().toTuple())
            if abs(self.size().width() - mouseMovePos.x()) > abs(mouseMovePos.x()):
                point_1.setX(mouseMovePos.x())
            else:
                point_2.setX(mouseMovePos.x())

            if abs(self.size().height() - mouseMovePos.y()) > abs(mouseMovePos.y()):
                point_1.setY(mouseMovePos.y())
            else:
                point_2.setY(mouseMovePos.y())

            if (onLeftBorder or onRightBorder) and not (onBottomBorder or onTopBorder):
                point_1 = QPoint(point_1.x(), 0)
                point_2 = QPoint(point_2.x(), self.size().height())
            elif (onTopBorder or onBottomBorder) and not (onLeftBorder or onRightBorder):
                point_1 = QPoint(0, point_1.y())
                point_2 = QPoint(self.size().width(), point_2.y())
            self.resize_save(event, self.pos() + point_1, self.pos() + point_2)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.resizing = False
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.moving = False

    def get_pix_cords(self) -> [[int, int], [int, int]]:
        return [list(self.pos().toTuple()), list(map(operator.add, self.pos().toTuple(), self.size().toTuple()))]

    def fix_cords(self, cords):
        if 0 < cords[1][0] < self.parent.size().width() and 0 < cords[1][1] < self.parent.size().height():
            if cords[0][0] < 0:
                cords[0][0] = 0
            if cords[0][1] < 0:
                cords[0][1] = 0
            return cords
        return None

    def set_pix_cords(self, cords: [[int, int], [int, int]]):
        cords = self.fix_cords(cords)
        if cords:
            self.move(QPoint(*cords[0]))
            self.resize(QSize(cords[1][0] - cords[0][0], cords[1][1] - cords[0][1]))

    def resize_save(self, event, point_1: QPoint, point_2: QPoint) -> None:
        if 0 <= point_1.x() < self.parent.size().width() and 0 <= point_1.y() < self.parent.size().height() and \
                0 <= point_2.x() < self.parent.size().width() and 0 <= point_2.y() < self.parent.size().height():
            self.move(point_1)
            self.resize(QSize(point_2.x() - point_1.x(), point_2.y() - point_1.y()))
        else:
            self.mousePressPos = event.position().toPoint()

    def move_save(self, event, point: QPoint) -> None:
        if 0 <= point.x() < self.parent.size().width() - self.size().width() and \
                0 <= point.y() < self.parent.size().height() - self.size().height():
            self.move(point)
        else:
            self.mousePressPos = event.position().toPoint()


