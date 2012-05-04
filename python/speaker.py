#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals

from PyQt4 import QtCore, QtGui

class SpeakerSignalDummy(QtCore.QObject):
    """
    This class is a QObject that can be used by the Speaker class to emit signals.
    It is a workaround, because QGraphicItemGroup cannot emit signals and
    it is not possible to multiple-inherit from two PyQt classes.
    """
    nameChanged = QtCore.pyqtSignal(str)
    queuedUp = QtCore.pyqtSignal()
    contradicts = QtCore.pyqtSignal()


class Speaker(QtGui.QGraphicsItemGroup):
    def __init__(self, name, parent=None):
        QtGui.QGraphicsItemGroup.__init__(self, parent)
        # subobject for handling signals
        self.signals = SpeakerSignalDummy()

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.text = QtGui.QGraphicsTextItem(name)
        self.text.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.addToGroup(self.text)
        self.portrait = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("res/Person.png"))
        self.portrait.setY(-35)
        self.addToGroup(self.portrait)

        self.editing = False
        self.dragging = False
        self.leftButtonDown = None

    @property
    def name(self):
        return str(self.text.toPlainText())

    @name.setter
    @QtCore.pyqtSlot(int, name="setName")
    def set_name(self, value):
        if nval != self.name:
            self.text.setPlainText(value)
            self.signals.nameChanged.emit(value)


    def mousePressEvent(self, event):
        if self.editing :
            self.text.mousePressEvent(event)
        else :
            if event.button() == 1:
                self.leftButtonDown = event.screenPos()
            super(Speaker, self).mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if self.editing :
            self.text.mouseMoveEvent(event)
        else :
            super(Speaker, self).mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        if self.editing :
            self.text.mouseReleaseEvent(event)
        else:
            if event.button() == 1 and \
               self.leftButtonDown is not None and \
               self.portrait.contains(event.pos() + QtCore.QPointF(0, 35)):
                movedDistance = (self.leftButtonDown - event.screenPos()).manhattanLength()
                if movedDistance < 2:
                    self.signals.queuedUp.emit()
                self.leftButtonDown = None
            elif event.button() == 2 and \
                 self.portrait.contains(event.pos() + QtCore.QPointF(0, 35)):
                self.signals.contradicts.emit()
            super(Speaker, self).mouseReleaseEvent(event)


    def mouseDoubleClickEvent(self, event):
        if event.button() == 1 and self.text.boundingRect().contains(event.pos()):
            self.editing = True
            self.noCursor = self.text.textCursor()
            self.text.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)


    def keyPressEvent(self, QKeyEvent):
        if self.editing and QKeyEvent.key() != 16777220:  # return
            self.text.keyPressEvent(QKeyEvent)
        else:
            self.editing = False
            self.text.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            self.text.setTextCursor(self.noCursor)
            self.signals.nameChanged.emit(self.name)
            self.update()



class SpeakerListModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.speakers = []

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.speakers)

    def data(self, index, role=None):
        row = index.row()
        speaker = self.speakers[row]
        if role == QtCore.Qt.DisplayRole:
            return speaker.name

    def appendSpeaker(self, speaker):
        position = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        self.speakers.append(speaker)
        speaker.signals.nameChanged.connect(self.on_name_change)
        self.endInsertRows()
        return True

    def on_name_change(self, _):
        # hack: update all data if one of the names changed
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), 0))

    def popSpeaker(self, position = 0):
        if not (0 <= position <= len(self.speakers)) :
            return
        self.beginRemoveRows(QtCore.QModelIndex(), position, position)
        s = self.speakers.pop(position)
        s.signals.nameChanged.disconnect(self.on_name_change)
        self.endRemoveRows()
        return s
