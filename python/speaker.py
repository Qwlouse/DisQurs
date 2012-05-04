#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals

from PyQt4 import QtCore, QtGui

class Speaker(QtGui.QGraphicsItemGroup):
    def __init__(self, name, parent = None):
        super(Speaker, self).__init__(parent)

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.text = QtGui.QGraphicsTextItem(name)
        self.portrait = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("res/Person.png"))

        self.portrait.setY(-35)
        self.addToGroup(self.text)
        self.addToGroup(self.portrait)
