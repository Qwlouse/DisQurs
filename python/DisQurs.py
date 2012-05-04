#!/usr/bin/python
# encoding: utf-8
from __future__ import division, print_function, unicode_literals
import sys

from PyQt4 import QtCore, QtGui, uic

from speaker import Speaker, SpeakerListModel

base, form = uic.loadUiType("MainWindow.ui")
class MainWindow(base, form):
    def __init__(self, parent=None, *args, **kwargs):
        super(base, self).__init__(parent, *args, **kwargs)
        self.setupUi(self)
        self.scene = QtGui.QGraphicsScene()
        self.speakersView.setScene(self.scene)
        self.speakersListModel = SpeakerListModel()
        self.contradictorsListModel = SpeakerListModel()
        self.speakersList.setModel(self.speakersListModel)
        self.contradictorsList.setModel(self.contradictorsListModel)

        self.populateScene(["Andreas", "Birgit", "Cherubim", "Dragon", "Enavigo"])

        self.actionAdd_Speaker.triggered.connect(self.on_add_speaker)

    def populateScene(self, speakers):
        self.allSpeakers = []
        self.queueSignalMapper = QtCore.QSignalMapper(self)
        self.contradictSignalMapper = QtCore.QSignalMapper(self)
        for i, s in enumerate(speakers):
            speaker = Speaker(s)
            self.allSpeakers.append(speaker)
            self.queueSignalMapper.setMapping(speaker.signals, i)
            self.contradictSignalMapper.setMapping(speaker.signals, i)
            speaker.signals.queuedUp.connect(self.queueSignalMapper.map)
            speaker.signals.contradicts.connect(self.contradictSignalMapper.map)
            self.scene.addItem(speaker)
            speaker.translate(100*i, 0)
        self.queueSignalMapper.mapped.connect(self.on_speaker_queues_up)
        self.contradictSignalMapper.mapped.connect(self.on_speaker_contradicts)
        self.update()

    def on_add_speaker(self):
        speaker = Speaker("Unnamed")
        self.scene.addItem(speaker)
        self.update()

    def on_speaker_queues_up(self, index):
        self.speakersListModel.appendSpeaker(self.allSpeakers[index])

    def on_speaker_contradicts(self, index):
        self.contradictorsListModel.appendSpeaker(self.allSpeakers[index])

def main():
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
