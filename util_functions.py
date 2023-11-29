import numpy as np

graphTitles = ['Volume', 'Duration', 'Duration Difference']
graphYlabels = ['velocity', 'duration in sec', 'duration difference']

def findNextNoteOn(currentNoteOn, listOfDicts):
    for dict in listOfDicts:
        if dict['note_on'] > currentNoteOn:
            return dict['note_on']

noteNames = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# returns pitch name and octave as string
def midiToPitch(midiNumber):
    octave = int (midiNumber / 12) - 1
    pitch = noteNames[midiNumber % 12]
    return pitch + str(octave)

# returns midi number, input needs to be string of pitch name and octave
def pitchToMidi(pitch: str):
    letter = pitch[:-1]
    answer = -1
    i = 0
    for note in noteNames:
        if letter == note:
            answer = i
            break
        i += 1

    if (answer == -1):
        print("Note name not found in list when converting note name to midi number: {0}".format(pitch))
        return

    answer += ((int(pitch[-1]))*12)+12
    return answer

# returns note number (not regarding octave), input needs to be string of pitch name and octave
def pitchToNoteNumber(pitch: str):
    return pitchToMidi(pitch) % 12

def midiToNoteNumber(midi: int):
    return midi % 12

def mapValue(value, minIn, maxIn, minOut, maxOut):
    inRange = maxIn - minIn
    outRange = maxOut - minOut

    if inRange <= 0.0:
        return value
    
    valueScaled = float(value - minIn) / float(inRange)
    return minOut + (valueScaled * outRange)

def velocity_to_sound_level(velocity):
    return mapValue(velocity, 1, 127, -10.0, 10.0)

def sound_level_to_velocity(sound_level):
    if sound_level < -10.0 or sound_level > 10.0:
        print("WARNING: sound_level out of bounds!")
    
    velocity = int(mapValue(sound_level, -10.0, 10.0, 1, 127))
    return np.clip(velocity, 0, 127)

# returns False on the first condition that is false
# the arguments should be lambda functions (without arguments) that return true or false
def checkConditions(*conditions):
    for cond in conditions:
        if not cond():
            return False
    return True

# input a string like "20, 30, 40"
# output: ["20", "30", "40"]
def stringToStringList(string: str):
    return string.replace(" ", "").split(",")

# the same but output is list of int
def stringToIntList(string: str):
    if string == "":
        return []
    else:
        return list(map(int, string.replace(" ", "").split(",")))

# the same but output is list of float
def stringToFloatList(string: str):
    if string == "":
        return []
    else:
        return list(map(float, string.replace(" ", "").split(",")))
