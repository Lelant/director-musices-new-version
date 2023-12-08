from input_parameter import DoubleInput
from rule_mainclass import Rule
from scoreAndPerformance import scoreAndPerformance, add_attribute, get_attribute, get_idx_of_last_obj, is_last_note, set_attribute

def init_final_ritardando(frame, row, column):
    return FinalRitardando(frame=frame, row=row, column=column)

class FinalRitardando(Rule):

    def __init__(self, frame, row, column):

        self.title = "Final Ritardando"

        super().__init__(frame=frame, row=row, column=column, rulename=self.title)

        upcountingColumn = 3

        self.qInput = DoubleInput(self.ruleFrame, upcountingColumn, 3.0, "Q")
        upcountingColumn = upcountingColumn + 2

        self.lengthInput = DoubleInput(self.ruleFrame, upcountingColumn, 0.0, "Length")
        upcountingColumn = upcountingColumn + 2

    def apply(self):
        
        length = 0
        if self.lengthInput.value.get():
            length = self.lengthInput.value.get()
        else:
            length = abs(self.quantValue.get()) * 1300.0

        vend = 1.0 / ((3 * self.quantValue.get()) + 1.0)

        for voice in scoreAndPerformance.getVoices():
            collection = scoreAndPerformance.getNotesOfVoice(voice)
            for idx, note in enumerate(collection):
                if is_last_note(idx, collection):

                    istart = idx
                    ndrtot = 0

                    while ndrtot < length and istart > 0:
                        istart -= 1
                        if get_attribute(collection[istart], 'nominal_duration') != None:
                            ndrtot += get_attribute(collection[istart], 'nominal_duration')

                    xoff = 0
                    exponent = (self.qInput.value.get() - 1.0) / self.qInput.value.get()
                    k = (vend**self.qInput.value.get()) - 1
                    namnare = (self.qInput.value.get() - 1) * k
                    const = -(self.qInput.value.get() / ((self.qInput.value.get() - 1) * k)) # TODO: division by zero if quant is 0
                    ton = 0
                    toff = 0

                    for i in range(istart, idx):
                        if get_attribute(collection[i], 'nominal_duration') != None and get_attribute(collection[i], 'duration_sec') != None:
                            xoff = (get_attribute(collection[i], 'nominal_duration') / ndrtot) + xoff
                            ton = toff
                            toff = (((((k * xoff) + 1)**exponent) * self.qInput.value.get()) / namnare) + const

                            # TODO: get_attribute can return None, catch error somehow
                            # (happens when quant is too much in the negative)
                            addValue = get_attribute(collection[i], 'duration_sec') * ((ndrtot * (toff - ton)) / get_attribute(collection[i], 'nominal_duration'))
                            add_attribute(collection[i], 'duration_sec', addValue)

        self.final_ritardando_last_note()

        print("Finished applying rule {0}".format(self.title))

    def final_ritardando_last_note(self):
        factor = 1.25

        for voice in scoreAndPerformance.getVoices():
            collection = scoreAndPerformance.getNotesOfVoice(voice)
            for idx, note in enumerate(collection):
                idx = get_idx_of_last_obj(collection)

                if get_attribute(collection[idx], 'duration_sec') != None and get_attribute(collection[idx-1], 'duration_sec') != None:
                    if (get_attribute(collection[idx], 'duration_sec') * factor) < get_attribute(collection[idx-1], 'duration_sec'):
                        set_attribute(collection[idx], 'duration_sec', get_attribute(collection[idx-1], 'duration_sec') * factor)