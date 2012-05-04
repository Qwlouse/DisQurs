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
