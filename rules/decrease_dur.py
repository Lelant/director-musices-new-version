from scoreAndPerformance import add_attribute, add_duration, get_attribute, get_measure_number, remove_all, set_all, scoreAndPerformance
from input_parameter import DoubleInput, StringInput
from rule_mainclass import Rule
import math
from rules.rule_utils import add_ritardando_in_front, cycle_to_bar_fraction, get_lenth_per_cent, get_note_value_fraction, make_list_ramp_x2_decimal_last, meter_to_number
from util_functions import stringToFloatList, stringToIntList, stringToStringList
from rules.curve_functions import curve_functions

def init_decrease_dur(frame, row, column):
    return DecreaseDur(frame=frame, row=row, column=column)

class DecreaseDur(Rule):

    def __init__(self, frame, row, column):

        self.title = "Decrease Dur"

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

        set_all("decrease_value_dur", 0.0)

        self.set_decrease_dur()
        self.apply_decrease_dur()

        remove_all("decrease_value_dur")

        print("Finished applying rule {0}".format(self.title))

    def set_decrease_dur(self):
        
        ack_value = 0 # ackumulation value (in fractions)
        bar_fraction = 0 # duration of one cycle in fractions
        lengths_in_fraction = [] # lengths of the restart ritardandos in fractions
        standard_length = 1
        length_percentage = 1
        list_curve_values = []
        num_notes_per_cycle = 0
        num_notes_in_curve = 0
        smallest_fraction = 1/128
        smallest_fraction_found = 100000
        nominal_duration_of_smallest_fraction = 0

        # get beats with [0] and beat_type with [1]
        current_time_signature = [None, None]

        curve_fn_acc = curve_functions[self.curveFunctionInput.value.get() + "_acc"]
        curve_fn_dec = curve_functions[self.curveFunctionInput.value.get() + "_dec"]

        for noteRest in scoreAndPerformance.part.notes:
            if get_note_value_fraction(noteRest) < smallest_fraction_found:
                smallest_fraction_found = get_note_value_fraction(noteRest)
                if get_attribute(noteRest, "nominal_duration") != None:
                    ndr_of_smallest_found = get_attribute(noteRest, "nominal_duration")

        nominal_duration_of_smallest_fraction = ndr_of_smallest_found / (smallest_fraction_found / smallest_fraction)

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

                num_notes_per_cycle = bar_fraction / smallest_fraction
                num_notes_in_curve = length_percentage * num_notes_per_cycle

                # apply the curve function for the number of notes in the curve and put them in a list
                list_curve_values = make_list_ramp_x2_decimal_last(num_notes_in_curve, self.weightInput.value.get() * self.quantValue.get() * 100, 0.0, self.powerInput.value.get(), curve_fn_acc, curve_fn_dec, nominal_duration_of_smallest_fraction)

                # add zeros at the end of the list for the notes in the cycle that are not in the curve
                while len(list_curve_values) < num_notes_per_cycle:
                    list_curve_values.append(0.0)

                note_length = get_note_value_fraction(noteRest) / smallest_fraction
                sum_value = 0.0
                start_point = math.floor((ack_value % bar_fraction) / smallest_fraction)

                for i in range(start_point, int(start_point + (note_length - 1))):
                    sum_value = sum_value + list_curve_values[i % len(list_curve_values)]

                # vielleicht muss man hier die summe durch die anzahl der noten teilen?
                # aber die werte sind immer noch nicht ganz gleich, aber schon viel besser
                sum_value = sum_value / num_notes_in_curve

                add_attribute(noteRest, "decrease_value_dur", sum_value)

                # increase ackumulation value by fraction of the note
                ack_value = ack_value + get_note_value_fraction(noteRest)

    def apply_decrease_dur(self):
        for voice in scoreAndPerformance.getVoices():
            notesAndRests = scoreAndPerformance.getNotesAndRestsOfVoice(voice)
            for idx, noteRest in enumerate(notesAndRests):
                if get_attribute(noteRest, "decrease_value_dur") != None:
                    # changed: not adding to 'decrease-dur, this is just for the reset function (see DM)

                    add_duration(noteRest, get_attribute(noteRest, "decrease_value_dur"), idx, notesAndRests)
