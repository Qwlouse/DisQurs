#!/usr/bin/python
# encoding: utf-8
from __future__ import division, print_function, unicode_literals
import sys
from PyQt4 import QtGui, uic

base, form = uic.loadUiType("MainWindow.ui")
class MainWindow(base, form):
    def __init__(self, parent=None, *args, **kwargs):
        super(base, self).__init__(parent, *args, **kwargs)
        self.setupUi(self)


def main():
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
