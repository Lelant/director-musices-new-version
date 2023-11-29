from scoreAndPerformance import add_attribute, get_attribute, get_idx_of_last_obj, get_measure_number, remove_all, set_all, scoreAndPerformance
from input_parameter import StringInput, DoubleInput
from rule_mainclass import Rule
from rules.curve_functions import curve_functions
from rules.rule_utils import add_ritardando_in_front, cycle_to_bar_fraction, get_lenth_per_cent, get_note_value_fraction, iadd_ramp_x2_decimal_last, meter_to_number
from util_functions import stringToFloatList, stringToIntList, stringToStringList

def init_decrease_amp(frame, row, column):
    return DecreaseAmp(frame=frame, row=row, column=column)

class DecreaseAmp(Rule):

    def __init__(self, frame, row, column):

        self.title = "Decrease Amp"

        super().__init__(frame=frame, row=row, column=column, rulename=self.title)

        upcountingColumn = 3

        self.levelInput = StringInput(self.ruleFrame, upcountingColumn, "1", "Level")
        upcountingColumn = upcountingColumn + 2
        self.weightInput = DoubleInput(self.ruleFrame, upcountingColumn, 1, "Weight")
        upcountingColumn = upcountingColumn + 2

        self.powerInput = DoubleInput(self.ruleFrame, upcountingColumn, 3, "Power")
        upcountingColumn = upcountingColumn + 2
        self.lengthInput = DoubleInput(self.ruleFrame, upcountingColumn, 1, "Length")
        upcountingColumn = upcountingColumn + 2
        self.curveFunctionInput = StringInput(self.ruleFrame, upcountingColumn, "power_fn", "Curve Function")
        upcountingColumn = upcountingColumn + 2

        self.restartBarsInput = StringInput(self.ruleFrame, upcountingColumn, "", "Restart Bars")
        upcountingColumn = upcountingColumn + 2
        self.restartLengthsInput = StringInput(self.ruleFrame, upcountingColumn, "", "Restart Lengths")
        upcountingColumn = upcountingColumn + 2
        self.restartPowersInput = StringInput(self.ruleFrame, upcountingColumn, "", "Restart Powers")
        upcountingColumn = upcountingColumn + 2
        self.restartFunctionsInput = StringInput(self.ruleFrame, upcountingColumn, "", "Restart Functions")
        upcountingColumn = upcountingColumn + 2
        self.restartIntensitiesInput = StringInput(self.ruleFrame, upcountingColumn, "", "Restart Intensities")
        upcountingColumn = upcountingColumn + 2

    def apply(self):

        self.restartBars = stringToIntList(self.restartBarsInput.value.get())
        self.restartLengths = stringToFloatList(self.restartLengthsInput.value.get())
        self.restartPowers = stringToFloatList(self.restartPowersInput.value.get())
        self.restartFunctions = stringToStringList(self.restartFunctionsInput.value.get())
        self.restartIntensities = stringToFloatList(self.restartIntensitiesInput.value.get())

        set_all("decrease_value_amp", 0.0)

        self.set_decrease_amp()
        self.apply_decrease_amp()

        remove_all("decrease_value_amp")

        print("Finished applying rule {0}".format(self.title))

    def set_decrease_amp(self):
        
        ack_value = 0 # ackumulation value (in fractions)
        bar_fraction = 0 # duration of one cycle in fractions
        lengths_in_fraction = [] # lengths of the restart ritardandos in fractions
        standard_length = 1
        length_percentage = 1

        # get beats with [0] and beat_type with [1]
        current_time_signature = [None, None]

        curve_fn_acc = curve_functions[self.curveFunctionInput.value.get() + "_acc"]
        curve_fn_dec = curve_functions[self.curveFunctionInput.value.get() + "_dec"]

        for voice in scoreAndPerformance.getVoices():

            # on starting a new voice, reset the ackumulation variable
            ack_value = 0

            notesAndRests = scoreAndPerformance.getNotesAndRestsOfVoice(voice)
            for idx, noteRest in enumerate(notesAndRests):
                
                # if there is a new time signature, set some variables
                new_time_signature = scoreAndPerformance.part.time_signature_map(noteRest.start.t)
                if current_time_signature[0] != new_time_signature[0] or current_time_signature[1] != new_time_signature[1]:
                    current_time_signature = new_time_signature
                
                    bar_fraction = cycle_to_bar_fraction(self.levelInput.value.get(), current_time_signature) # level = cycle

                    # calculate the length in percentage based on bar-fraction and user input length
                    length_percentage = get_lenth_per_cent(bar_fraction, self.lengthInput.value.get(), current_time_signature)
                    lengths_in_fraction = list(map(lambda x: x * meter_to_number(current_time_signature), self.restartLengths))
                    standard_length = standard_length * meter_to_number(current_time_signature)

                # if we are at a restart point, reset the ackumulation variable
                # and call the function for adding a ritardando in front
                new_bar = get_measure_number(noteRest)
                if new_bar != None:
                    if new_bar in self.restartBars:
                        ack_value = 0
                        add_ritardando_in_front(notesAndRests, idx, self.restartBars.index(new_bar), lengths_in_fraction, standard_length, self.restartIntensities, self.restartPowers, self.restartFunctions)

                # for every start point of the level...
                if (ack_value % bar_fraction) == 0:
                    # calc the index of the last note in the curve and apply the curve
                    end_note_index = idx
                    fraction_value_loop = 0
                    
                    while fraction_value_loop < (bar_fraction * length_percentage) and end_note_index <= get_idx_of_last_obj(notesAndRests):
                        fraction_value_loop = fraction_value_loop + get_note_value_fraction(notesAndRests[end_note_index])
                        end_note_index = end_note_index + 1
                    # problem with last note. The last ramp is not cut off but going directly down to the last note.
                    # maybe set the end-value (eval) different here, so the curve is not going down but is cut off instead.

                    if end_note_index > get_idx_of_last_obj(notesAndRests):
                        end_note_index = get_idx_of_last_obj(notesAndRests)

                    if idx == end_note_index:
                        print("WARNING: Start and end note are the same!")

                    iadd_ramp_x2_decimal_last(notesAndRests, idx, end_note_index, 0.0, 0.0, self.weightInput.value.get() * self.quantValue.get(), 0.0, "decrease_value_amp", self.powerInput.value.get(), curve_fn_acc, curve_fn_dec)

                # increase ackumulation value by fraction of the note
                ack_value = ack_value + get_note_value_fraction(noteRest)

    def apply_decrease_amp(self):
        for voice in scoreAndPerformance.getVoices():
            for note in scoreAndPerformance.getNotesOfVoice(voice):
                if get_attribute(note, "decrease_value_amp") != None:
                    # changed: not checking if it is rest
                    # changed: not adding to 'decrease-amp, this is just for the reset function (see DM)
                    add_attribute(note, "sound_level", get_attribute(note, "decrease_value_amp"))
