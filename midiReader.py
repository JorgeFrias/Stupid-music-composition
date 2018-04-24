import mido
import os


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




