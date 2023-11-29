from input_parameter import DoubleInput
from rule_mainclass import Rule
import customtkinter
from scoreAndPerformance import scoreAndPerformance, add_attribute, get_attribute, get_first_note, is_first_note, is_last_note, remove_attribute, set_attribute
from util_functions import midiToNoteNumber

def init_melodic_charge(frame, row, column):
    return MelodicCharge(frame=frame, row=row, column=column)

class MelodicCharge(Rule):

    def __init__(self, frame, row, column):

        self.title = "Melodic Charge"

        super().__init__(frame=frame, row=row, column=column, rulename=self.title)

        upcountingColumn = 3

        self.ampInput = DoubleInput(self.ruleFrame, upcountingColumn, 1.0, "Amp")
        upcountingColumn = upcountingColumn + 2

        self.durInput = DoubleInput(self.ruleFrame, upcountingColumn, 1.0, "Dur")
        upcountingColumn = upcountingColumn + 2

        self.vibampInput = DoubleInput(self.ruleFrame, upcountingColumn, 1.0, "Vib Amp")
        upcountingColumn = upcountingColumn + 2

    def apply(self):
        
        if get_attribute(get_first_note(), 'q') == None:
            print("Melodic-charge: no chord info on first note - skipping rule.")
        else:
            self.melodic_charge_dr(self.durInput.value.get() * self.quantValue.get())
            self.melodic_charge_amp()
            self.melodic_charge_smear()
            self.melodic_charge_vib(self.vibampInput.value.get() * self.quantValue.get())

            for voice in scoreAndPerformance.getVoices():
                for note in scoreAndPerformance.getNotesOfVoice(voice):
                    if get_attribute(note, 'msl') != None:
                        add_attribute(note, 'sound_level', self.ampInput.value.get() * self.quantValue.get() * get_attribute(note, 'msl'))
                        remove_attribute(note, 'msl')

        print("Finished applying rule {0}".format(self.title))

    def melodic_charge_amp(self):
        qnr = None

        for voice in scoreAndPerformance.getVoices():
            for note in scoreAndPerformance.getNotesOfVoice(voice):
                if get_attribute(note, 'q') != None:
                    # Info: das geht davon aus, dass q eine liste von midi pitches ist und der erste Wert der liste ist der Grundton des Akkords
                    qnr = midiToNoteNumber(get_attribute(note, 'q')[0])

                newVal = 0.2 * self.melodic_charge_fn((midiToNoteNumber(note.midi_pitch) - qnr) % 12)
                set_attribute(note, 'msl', newVal)

    def melodic_charge_smear(self):
        for voice in scoreAndPerformance.getVoices():
            collection = scoreAndPerformance.getNotesOfVoice(voice)
            for idx, note in enumerate(collection):
                
                if not is_first_note(idx):
                    if not is_last_note(idx, collection):
                        if get_attribute(note, 'msl') != None:
                            if get_attribute(collection[idx-1], 'msl') != None:
                                if get_attribute(collection[idx+1], 'msl') != None:
                                    if get_attribute(collection[idx-1], 'msl') < (get_attribute(note, 'msl') * 2):
                                        if abs(collection[idx-1].midi_pitch - note.midi_pitch) < 3:
                                            if not collection[idx-1].midi_pitch == note.midi_pitch:
                                                if get_attribute(collection[idx-1], 'nominal_duration') == get_attribute(note, 'nominal_duration'):
                                                    if get_attribute(collection[idx-1], 'nominal_duration') < 500:
                
                                                        set_attribute(collection[idx-1], 'msl', round(get_attribute(note, 'msl') * 0.75))

                                                        if get_attribute(note, 'msl') > (get_attribute(collection[idx+1], 'msl') * 2):
                                                            set_attribute(collection[idx+1], 'msl', round(0.55 * get_attribute(note, 'msl')))

    def melodic_charge_dr(self, quant):
        qnr = None

        for voice in scoreAndPerformance.getVoices():
            collection = scoreAndPerformance.getNotesOfVoice(voice)
            for idx, note in enumerate(collection):
                if get_attribute(note, 'q') != None:
                    qnr = midiToNoteNumber(get_attribute(note, 'q')[0])

                newVal = get_attribute(note, 'duration_sec') * (1 + (quant * (2.0 / 300.0) * self.melodic_charge_fn((midiToNoteNumber(note.midi_pitch) - qnr) % 12)))
                set_attribute(note, 'duration_sec', newVal)

    def melodic_charge_vib(self, quant):
        last_va = 0
        base_vib = 3

        for voice in scoreAndPerformance.getVoices():
            collection = scoreAndPerformance.getNotesOfVoice(voice)
            for idx, note in enumerate(collection):
                if get_attribute(note, 'msl') != None:
                
                    va = round(quant * 0.15 * 16.8 * get_attribute(note, 'msl'))

                    if is_first_note(collection[idx]):
                        set_attribute(note, 'va', base_vib)

                    if last_va != va:
                        set_attribute(note, 'va', va + base_vib)
                        last_va = va + base_vib

    def melodic_charge_fn(self, nr):
        values = [0, 6.5, 2, 4.5, 4, 2.5, 6, 1, 5.5, 3, 3.5, 5]
        return values[nr]