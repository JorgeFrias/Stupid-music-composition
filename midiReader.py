import mido
import os
import numpy as np

class note():
    def __init__(self, note : int, velocity : int, time : int):
        self.velocity = velocity
        self.note = note
        self.time = time

def readTrack(mid : mido.MidiFile, printInfo = True):
    notes = []
    for i, track in enumerate(mid.tracks):
        if printInfo:
            print('Track {}: {}'.format(i, track.name))
        for msg in track:
            if not msg.is_meta:
                # Read content
                try:
                    tmpNote = note(msg.note, msg.velocity, msg.time)
                    notes.append(tmpNote)

                except AttributeError:
                    print('> No attribute channel, note or velocity')

    return notes

def genertateDataSet(notes, dataSize):
    '''
    Creates the nunmpy arrays for sklearn naive_bayes
    :param notes: The array with notes obj
    :param dataSize: Number of notes to build the training data set
    :return:
    '''
    currentPos = 0                                              # Note to start getting dataSize notes. Next target size notes
    npDataNotes = np.array([])
    npTargetNotes = np.array([])
    npTargetVelocity = np.array([])
    npTargetTime = np.array([])

    for i in range(len(notes) - (dataSize + 1)):                # Not to go over the end
        # Get data positions
        for i in range(dataSize):
            # dataPositions.append(currentPos + i)
            tmpPos = currentPos + i
            # dataNotes.append(notes[tmpPos])
            np.append(npDataNotes, [notes[tmpPos].note, notes[tmpPos].velocity, notes[tmpPos].time])

        # Get target note, vel and time
        targetPos = currentPos + dataSize
        np.append(npTargetNotes, notes[targetPos].note)
        np.append(npTargetVelocity, notes[targetPos].velocity)
        np.append(npTargetTime, notes[targetPos].time)

    return {'dataNotes':npDataNotes, 'targetNotes':npTargetNotes,'targetVelocity':npTargetVelocity, 'targetTime':npTargetTime}

''' Fetch all '''
cwd = os.getcwd()                                               # Current working directory
midiDB = 'Midi'
composerDir = os.path.join(cwd, midiDB)
for composer in os.listdir(composerDir):                        # iterate over artists
    compSongs = os.path.join(cwd, midiDB, composer)
    for song in os.listdir(compSongs):                          # iterate over songs
        songPath = os.path.join(cwd, midiDB, composer, song)
        print(composer + ': ' + song)

        mid = mido.MidiFile(songPath)                           # MIDI info
        readTrack(mid)




