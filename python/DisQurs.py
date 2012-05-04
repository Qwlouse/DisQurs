#!/usr/bin/python
# encoding: utf-8
from __future__ import division, print_function, unicode_literals
import sys

from PyQt4 import QtCore, QtGui, uic

from speaker import Speaker, SpeakerListModel

# Global configuration flags for speaker list logic
disallowMultipleQueueUps = True
followUpSpeakerCanContradict = False


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

        self.allSpeakers = []
        self.queueSignalMapper = QtCore.QSignalMapper(self)
        self.contradictSignalMapper = QtCore.QSignalMapper(self)
        self.queueSignalMapper.mapped.connect(self.on_speaker_queues_up)
        self.contradictSignalMapper.mapped.connect(self.on_speaker_contradicts)

        self.populateScene(["Andreas", "Birgit", "Cherubim", "Dragon", "Enavigo"])

        self.actionAdd_Speaker.triggered.connect(self.on_add_speaker)
        self.actionNext.triggered.connect(self.on_next_action)

    def populateScene(self, speakers):
        for i, s in enumerate(speakers):
            speaker = Speaker(s)
            self.add_speaker(speaker)
            speaker.translate(100*i, 0)

        self.update()

    def add_speaker(self, speaker):
        i = len(self.allSpeakers)
        self.allSpeakers.append(speaker)
        self.queueSignalMapper.setMapping(speaker.signals, i)
        self.contradictSignalMapper.setMapping(speaker.signals, i)
        speaker.signals.queuedUp.connect(self.queueSignalMapper.map)
        speaker.signals.contradicts.connect(self.contradictSignalMapper.map)
        self.scene.addItem(speaker)


    def on_add_speaker(self):
        speaker = Speaker("Unnamed")
        self.add_speaker(speaker)
        self.update()

    def on_speaker_queues_up(self, index):
        speaker = self.allSpeakers[index]
        if speaker in self.speakersListModel.speakers and disallowMultipleQueueUps:
            print("No multi-Queue-Ups")
            return

        speakersList = self.speakersListModel.speakers
        contradictorsList = self.contradictorsListModel.speakers
        if not followUpSpeakerCanContradict and len(speakersList) == 1 and \
           len(contradictorsList) > 0 and speaker is contradictorsList[0]:
            # turn contradictor into follow-up speaker
            self.contradictorsListModel.popSpeaker()

        if not len(speakersList):
            self.start_speech(speaker)
        self.speakersListModel.appendSpeaker(speaker)


    def on_speaker_contradicts(self, index):
        contradictor = self.allSpeakers[index]
        if contradictor in self.contradictorsListModel.speakers:
            print("cannot contradict more than once")
            return

        speakersList = self.speakersListModel.speakers
        if not len(speakersList):
            print("Nobody speaks")
            return

        if contradictor is speakersList[0]:
            print("nobody can contradict himself")
            return

        if not followUpSpeakerCanContradict and len(speakersList) > 1 and contradictor is speakersList[1]:
            print("follow-up speaker cannot contradict")
            return

        self.contradictorsListModel.appendSpeaker(self.allSpeakers[index])


    def start_speech(self, speaker):
        speaker.turnGreen()

    def stop_speech(self, speaker):
        speaker.turnGray()


    def on_next_action(self):
        # ersten redebeitrag abschließen
        # redner aus redeliste entfernen
        s = self.speakersListModel.popSpeaker()
        if s is None:
            return
        self.stop_speech(s)
        # Gegenrede starten

        # nächsten redebeitrag beginnen
        if len(self.speakersListModel.speakers) > 0:
            ns = self.speakersListModel.speakers[0]
            self.start_speech(ns)


def main():
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
