import mido

mid = mido.MidiFile('song.mid')
for msg in mid.play():
    port.send(msg)