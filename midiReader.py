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
                    if printInfo:
                        print('> No attribute channel, note or velocity')
    return notes

def run(test=False):
    allSongsNotes = []

    ''' Fetch all '''
    cwd = os.getcwd()  # Current working directory
    midiDB = 'Midi_full'
    if test:
        midiDB = 'Midi_test'
    composerDir = os.path.join(cwd, midiDB)
    for composer in os.listdir(composerDir):                    # iterate over artists
        compSongs = os.path.join(cwd, midiDB, composer)
        for song in os.listdir(compSongs):                      # iterate over songs
            songPath = os.path.join(cwd, midiDB, composer, song)
            print('> Reading ' + composer + ': ' + song)
            mid = mido.MidiFile(songPath)                       # MIDI info
            allSongsNotes.extend(readTrack(mid, False))                # Append new notes

    '''Buld datasets '''
    notesInInput = 3                                            # To select how many previous notes to use
    genertateDataSet(allSongsNotes, notesInInput)

def genertateDataSet(notes, dataSize):
    '''
    Creates the nunmpy arrays for sklearn naive_bayes
    :param notes: The array with notes obj
    :param dataSize: Number of notes to build the training data set
    :return: Dict dataNotes, targetNotes, targetVelocity, targetTime
    '''
    dataNotes = []
    targetNotes = []
    targetVelocity = []
    targetTime = []

    for i in range(len(notes) - (dataSize + 1)):                # Not to go over the end
        # Get data notes
        tmpNotes = []
        for j in range(dataSize):
            tmpPos = i + j
            tmpNotes.append(notes[tmpPos].note)
            tmpNotes.append(notes[tmpPos].velocity)
            tmpNotes.append(notes[tmpPos].time)
        dataNotes.append(tmpNotes)

        # Get target note, vel and time
        targetPos = i + dataSize
        targetNotes.append(notes[targetPos].note)
        targetVelocity.append(notes[targetPos].velocity)
        targetTime.append(notes[targetPos].time)

    npDataNotes = np.array(dataNotes)
    npTargetNotes = np.array(targetNotes)
    npTargetVelocity = np.array(targetVelocity)
    npTargetTime = np.array(targetTime)

    return {'dataNotes':npDataNotes, 'targetNotes':npTargetNotes,'targetVelocity':npTargetVelocity, 'targetTime':npTargetTime}

def saveMidi(notes):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.Message('program_change', program=12, time=0))
    for note in notes:
        track.append(mido.Message('note_on', note=note.note, velocity=note.velocity, time=note.time))

    # I think is not needed
    # track.append(mido.Message('note_off', note=64, velocity=127, time=32))
    import time
    timeStr = time.strftime("%Y%m%d-%H%M%S")
    mid.save('generatedSongs/gen_' + timeStr + '.mid')

run(True)
