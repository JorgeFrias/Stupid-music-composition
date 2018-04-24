import mido
import os, sys
import time
import numpy as np
from classifier import train, predict

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

def initialSecuence(file:str, numberOfNotes):
    try:
        mid = mido.MidiFile(file)  # MIDI info
        notes = readTrack(mid, False)
        notes = notes[:numberOfNotes]

        return notes
    except AttributeError:
        print('Initial sequence error')

def generateDataSet(notes, dataSize):
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

    track.append(mido.Message('program_change', program=0, time=0))
    for notex in notes:
        track.append(mido.Message('note_on', note=int(notex.note), velocity=int(notex.velocity), time=int(notex.time)))

    # I think is not needed
    # track.append(mido.Message('note_off', note=64, velocity=127, time=32))
    timeStr = time.strftime("%Y%m%d-%H%M%S")
    songName = 'generatedSongs/gen_' + timeStr + '.mid'
    mid.save(songName)
    return songName

def trainModels(dataDict, models = []):
    notesMdls = []
    velMdls = []
    timeMdls = []
    if(len(models) == 0):
        notesMdl = train(dataDict['dataNotes'], dataDict['targetNotes'])
        velMdl = train(dataDict['dataNotes'], dataDict['targetVelocity'])
        timeMdl = train(dataDict['dataNotes'], dataDict['targetTime'])
        notesMdls.append(notesMdl)
        velMdls.append(velMdl)
        timeMdls.append(timeMdl)
    elif(len(models) == 1):
        notesMdl = train(dataDict['dataNotes'], dataDict['targetNotes'], model=models)
        velMdl = train(dataDict['dataNotes'], dataDict['targetVelocity'], model=models)
        timeMdl = train(dataDict['dataNotes'], dataDict['targetTime'], model=models)
        notesMdls.append(notesMdl)
        velMdls.append(velMdl)
        timeMdls.append(timeMdl)
    else:
        for model in models:
            notesMdl = train(dataDict['dataNotes'], dataDict['targetNotes'], model=model)
            velMdl = train(dataDict['dataNotes'], dataDict['targetVelocity'], model=model)
            timeMdl = train(dataDict['dataNotes'], dataDict['targetTime'], model=model)
            notesMdls.append(notesMdl)
            velMdls.append(velMdl)
            timeMdls.append(timeMdl)
    return notesMdls, velMdls, timeMdls

"""
Params: - Mdls = Bayesian prediction models
        - length = length of the song we want
        - initNotes = initial notes of the song, it has to be the same
                      size as the accepted input size of the model
        - size = in case a random sequence of initial notes is wanted
                 the size of the accepted input will be specified here
        - multiModel = Use random model from list of models
"""

def generateNotes(notesMdls, velMdls, timeMdls, length, initNotes, multiModel=False):

    newNotes = []
    if(len(initNotes) != 0):
        size = len(initNotes)
        for notex in initNotes:
            newNotes.append(notex)
        for i in range(length):
            unlabelled = []
            for j in range(i, i+size):
                unlabelled.append(newNotes[j].note)
                unlabelled.append(newNotes[j].velocity)
                unlabelled.append(newNotes[j].time)

            npUnlabelled = np.array(unlabelled).reshape(1, -1)
            if(multiModel):
                velMdl = velMdls[np.random.randint(len(velMdls))]
                notesMdl = notesMdls[np.random.randint(len(notesMdls))]
                timeMdl = timeMdls[np.random.randint(len(timeMdls))]
                n = note(predict(velMdl, npUnlabelled),
                         predict(notesMdl, npUnlabelled),
                         predict(timeMdl, npUnlabelled))
            else:
                n = note(predict(velMdls[0], npUnlabelled),
                         predict(notesMdls[0], npUnlabelled),
                         predict(timeMdls[0], npUnlabelled))
            newNotes.append(n)
    else:
        # Generate a random sequence of initial notes.
        print("Error!")

    return newNotes[len(initNotes):]

def run(dataSet=["Beethoven"], length=100, windowSize=20, models=["gnb"], seed="random"):
    allSongsNotes = []
    notesInInput = windowSize

    ''' Fetch all '''
    midiDB = 'Midi_full'
    midiSeeds = 'Midi_seed'

    cwd = os.getcwd()  # Current working directory
    composerDir = os.path.join(cwd, midiDB)
    for composer in dataSet:                    # iterate over artists
        compSongs = os.path.join(cwd, midiDB, composer)
        for song in os.listdir(compSongs):                      # iterate over songs
            songPath = os.path.join(cwd, midiDB, composer, song)
            print('> Reading ' + composer + ': ' + song)
            mid = mido.MidiFile(songPath)                       # MIDI info
            allSongsNotes.extend(readTrack(mid, False))         # Append new notes

    # Get random seed
    seedSongs = os.path.join(cwd, midiSeeds)
    seedSongList = os.listdir(seedSongs)
    if(seed == "random"):
        songIndex = np.random.randint(len(seedSongList))                     # Ge random song
        song = seedSongList[songIndex]
        songPath = os.path.join(cwd, midiSeeds, song)
    else:
        songPath = os.path.join(cwd, midiSeeds, seed)
    baseSecuence = initialSecuence(songPath, notesInInput)


    '''Buld datasets '''                                           # To select how many previous notes to use
    dataDict = generateDataSet(allSongsNotes, notesInInput)
    notesMdl, velMdl, timeMdl = trainModels(dataDict, models=models)
    song = generateNotes(notesMdl, velMdl, timeMdl, length, baseSecuence)
    realSong = saveMidi(song)
    return realSong

if __name__ == "__main__":
    if(len(sys.argv) < 6):
        print("\n--- Wrong number of args ---\n")
        print("Usage:\n- 1st arg: Training datasets separated by underscores\n- 2nd arg: Song length\n" +  
              "- 3rd arg: Window size\n- 4th arg: Models separated by underscores\n" + 
              "- 5th arg: Seed\n\nAvailable models are:\n   gnb, dte, dtg, bnb, rdm, mnb\n" + 
              "\nAvailable datasets are:")
        cwd = os.getcwd()  # Current working directory
        composerDir = os.path.join(cwd, "Midi_full")
        for composer in os.listdir(composerDir):                    # iterate over artists
            print(composer, end=" ")
        print("\n\nAvailable seeds are:")
        composerDir = os.path.join(cwd, "Midi_seed")
        for composer in os.listdir(composerDir):                    # iterate over artists
            print(composer, end=" ")
        print("random")
        quit()
    else:
        dataSet = sys.argv[1].split("_")
        models = sys.argv[4].split("_")
        songName=run(dataSet, int(sys.argv[2]), int(sys.argv[3]), models, sys.argv[5])
        print("Your new song is " + songName + ". Enjoy it mai fren!")

