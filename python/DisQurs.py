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

        self.contradicting = False
        self.currentSpeaker = None

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

        self.speakersListModel.appendSpeaker(speaker)
        if self.currentSpeaker is None:
            self.start_speech()

        # if it is second speaker color him!
        if len(self.speakersListModel.speakers) == 2:
            self.speakersListModel.speakers[1].changeColor("lightgreen")


    def on_speaker_contradicts(self, index):
        oldContradictor = None
        if len(self.contradictorsListModel.speakers) > 0:
            oldContradictor = self.contradictorsListModel.speakers[0]

        contradictor = self.allSpeakers[index]
        if contradictor in self.contradictorsListModel.speakers:
            print("cannot contradict more than once")
            return

        speakersList = self.speakersListModel.speakers
        if self.currentSpeaker is None:
            print("Nobody speaks")
            return

        if contradictor is self.currentSpeaker:
            print("nobody can contradict himself")
            return

        if not followUpSpeakerCanContradict and len(speakersList) > 1 and contradictor is speakersList[1]:
            print("follow-up speaker cannot contradict")
            return

        if self.contradicting :
            print("Cannot contradict a contradictor!")
            return

        self.contradictorsListModel.appendSpeaker(self.allSpeakers[index])
        #TODO: Sort contradictors
        if oldContradictor is not None :
            oldContradictor.changeColor("gray")
        newContradictor = self.contradictorsListModel.speakers[0]
        newContradictor.changeColor("lightred")


    def start_timer(self):
        self.timeEdit.setTime(QtCore.QTime(0, 0, 0))
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def tick(self):
        self.timeEdit.setTime(self.timeEdit.time().addSecs(1))

    def stop_timer(self):
        self.timer.stop()


    def start_speech(self):
        assert len(self.speakersListModel.speakers) > 0
        assert self.currentSpeaker is None
        speaker = self.speakersListModel.speakers[0]
        speaker.changeColor("green")
        self.currentSpeaker = speaker
        self.contradicting = False
        self.start_timer()
        # color next speaker
        if len(self.speakersListModel.speakers) > 1:
            self.speakersListModel.speakers[1].changeColor("lightgreen")

    def stop_speech(self):
        speaker = self.speakersListModel.popSpeaker()
        assert speaker is self.currentSpeaker is not None
        self.currentSpeaker.changeColor("gray")
        self.currentSpeaker = None
        self.stop_timer()

    def start_contradiction(self):
        assert len(self.contradictorsListModel.speakers) > 0
        assert self.currentSpeaker is None
        advocat = self.contradictorsListModel.speakers[0]
        advocat.changeColor("red")
        self.currentSpeaker = advocat
        self.contradicting = True
        # remove contestants (only allow one contradictor)
        while len(self.contradictorsListModel.speakers) > 1:
            self.contradictorsListModel.popSpeaker(1)
        self.start_timer()
        # color next speaker
        if len(self.speakersListModel.speakers) > 0:
            self.speakersListModel.speakers[0].changeColor("lightgreen")

    def stop_contradiction(self):
        assert self.contradicting
        advocat = self.contradictorsListModel.popSpeaker()
        assert advocat is self.currentSpeaker is not None
        advocat.changeColor("gray")
        self.currentSpeaker = None
        self.contradicting = False
        self.stop_timer()


    def on_next_action(self):
        # redebeitrag abschließen
        if self.currentSpeaker is not None :
            if self.contradicting :
                self.stop_contradiction()
            else:
                self.stop_speech()

        if len(self.contradictorsListModel.speakers) > 0:
            # Gegenrede starten
            self.start_contradiction()
        elif len(self.speakersListModel.speakers) > 0:
            # nächsten redebeitrag beginnen
            self.start_speech()


def main():
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
