from rule_mainclass import Rule
from scoreAndPerformance import scoreAndPerformance, add_attribute, add_duration, get_attribute
from util_functions import mapValue

def init_highloud(frame, row, column):
    return HighLoud(frame=frame, row=row, column=column)

class HighLoud(Rule):

    def __init__(self, frame, row, column):

        self.title = "High Loud"

        super().__init__(frame=frame, row=row, column=column, rulename=self.title)

    def apply(self):

        for voice in scoreAndPerformance.getVoices():

            i = 0
            midiPitchSum = 0.0
            midiPitchMean = 60

            for note in scoreAndPerformance.getNotesOfVoice(voice):

                if get_attribute(note, "midi_pitch") != None:

                    i += 1
                    midiPitchSum += get_attribute(note, "midi_pitch")

            midiPitchMean = midiPitchSum / i

            for note in scoreAndPerformance.getNotesOfVoice(voice):

                if get_attribute(note, "midi_pitch") != None and get_attribute(note, "sound_level") != None:

                    addValue = self.quantValue.get() * ((get_attribute(note, "midi_pitch") - midiPitchMean) / 4.0)
                    add_attribute(note, "sound_level", addValue)

        print("Finished applying rule {0}".format(self.title))



def init_highlong(frame, row, column):
    return HighLong(frame=frame, row=row, column=column)

class HighLong(Rule):

    def __init__(self, frame, row, column):

        self.title = "High Long"

        super().__init__(frame=frame, row=row, column=column, rulename=self.title)

    def apply(self):

        for voice in scoreAndPerformance.getVoices():

            i = 0
            midiPitchSum = 0.0
            midiPitchMean = 60

            for note in scoreAndPerformance.getNotesOfVoice(voice):
                i += 1
                midiPitchSum += note.midi_pitch

            midiPitchMean = midiPitchSum / i
        
            collection = scoreAndPerformance.getNotesOfVoice(voice)
            for idx, note in enumerate(collection):
                addDuration = mapValue(self.quantValue.get() * ((note.midi_pitch - midiPitchMean) / 4.0), -3.0, 3.0, 0.1, 1.0)
                add_duration(note, addDuration, idx, collection)

        print("Finished applying rule {0}".format(self.title))

