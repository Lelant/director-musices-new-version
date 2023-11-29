from scoreAndPerformance import add_attribute, get_attribute, get_measure_number, remove_all, set_all, scoreAndPerformance
from rule_mainclass import Rule
from input_parameter import DoubleInput, StringInput
from rules.rule_utils import add_ritardando_in_front, apply_factors_to_list, check_list_length, get_note_value_fraction, level_to_bar_fraction, make_list_of_beats, meter_to_number
from util_functions import stringToFloatList, stringToIntList, stringToStringList

def init_metrical_amp(frame, row, column):
    return MetricalAmp(frame=frame, row=row, column=column)

class MetricalAmp(Rule):

    def __init__(self, frame, row, column):

        self.title = "Metrical Amp"

        super().__init__(frame=frame, row=row, column=column, rulename=self.title)

        upcountingColumn = 3

        self.levelInput = StringInput(self.ruleFrame, upcountingColumn, "4", "Level")
        upcountingColumn = upcountingColumn + 2
        self.weightInput = DoubleInput(self.ruleFrame, upcountingColumn, 1, "Weight")
        upcountingColumn = upcountingColumn + 2
        self.hierarchyInput = StringInput(self.ruleFrame, upcountingColumn, "100, 50, 75, 25", "Hierarchy")
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

        self.hierarchy = stringToFloatList(self.hierarchyInput.value.get())
        self.restartBars = stringToIntList(self.restartBarsInput.value.get())
        self.restartLengths = stringToFloatList(self.restartLengthsInput.value.get())
        self.restartPowers = stringToFloatList(self.restartPowersInput.value.get())
        self.restartFunctions = stringToStringList(self.restartFunctionsInput.value.get())
        self.restartIntensities = stringToFloatList(self.restartIntensitiesInput.value.get())

        set_all("metrical_value_amp", 0.0)

        # changed: giving global variables to function not necessary
        self.set_metrical_amp()
        self.apply_metrical_amp()

        remove_all("metrical_value_amp")

        print("Finished applying rule {0}".format(self.title))

    def set_metrical_amp(self):
        
        list_weights = self.hierarchy
        ack_value = 0 # ackumulation value (in fractions)
        list_of_beat_fractions = [] # list of the fractions of every beat
        bar_fraction = 0 # duration of one cycle in fractions
        lengths_in_fraction = [] # lengths of the restart ritardandos in fractions
        standard_length = 1

        # get beats with [0] and beat_type with [1]
        current_time_signature = [None, None]

        for voice in scoreAndPerformance.getVoices():

            # on starting a new voice, reset the ackumulation variable
            ack_value = 0

            notesAndRests = scoreAndPerformance.getNotesAndRestsOfVoice(voice)
            for idx, noteRest in enumerate(notesAndRests):

                # reset the list of weights
                list_weights = self.hierarchy

                # if there is a new time signature, set some variables
                new_time_signature = scoreAndPerformance.part.time_signature_map(noteRest.start.t)
                if current_time_signature[0] != new_time_signature[0] or current_time_signature[1] != new_time_signature[1]:
                    current_time_signature = new_time_signature

                    bar_fraction = level_to_bar_fraction(self.levelInput.value.get(), current_time_signature)
                    lengths_in_fraction = list(map(lambda x: x * meter_to_number(current_time_signature), self.restartLengths))
                    standard_length = standard_length * meter_to_number(current_time_signature)

                # if we are at a restart point, reset the ackumulation variable
                # and call the function for adding a ritardando in front
                new_bar = get_measure_number(noteRest)
                if new_bar != None:
                    if new_bar in self.restartBars:
                        ack_value = 0
                        add_ritardando_in_front(notesAndRests, idx, self.restartBars.index(new_bar), lengths_in_fraction, standard_length, self.restartIntensities, self.restartPowers, self.restartFunctions)

                # if the level and meter don't fit together, print warning and jump to the next note
                if bar_fraction == 0:
                    print("The level {0} is not usable with the meter {1}/{2}. Please choose a different level.".format(self.levelInput.value.get(), current_time_signature[0], current_time_signature[1]))
                else:
                    # set the correct length for list-weights
                    list_weights = check_list_length(list_weights, current_time_signature, self.levelInput.value.get())
                    # apply quant and weight to the values
                    list_weights = apply_factors_to_list(self.quantValue.get(), self.weightInput.value.get(), list_weights)
          
                    # set the beat-place of the note
                    beat_place = ack_value % bar_fraction

                    # make the list of beat fractions
                    list_of_beat_fractions = make_list_of_beats(len(list_weights), self.levelInput.value.get(), current_time_signature)

                    # loop over the beat fractions and give the note the according weights
                    for i, beat in enumerate(list_of_beat_fractions):
                        if beat_place == beat:
                            add_attribute(noteRest, "metrical_value_amp", list_weights[i])

                    # increase ackumulation value by fraction of the note
                    ack_value = ack_value + get_note_value_fraction(noteRest)

    def apply_metrical_amp(self):
        for voice in scoreAndPerformance.getVoices():
            for note in scoreAndPerformance.getNotesOfVoice(voice):
                if get_attribute(note, "metrical_value_amp") != None:
                    # changed: not checking if it is rest
                    # changed: not adding to 'metrical-amp, this is just for the reset function (see DM)
                    add_attribute(note, "sound_level", get_attribute(note, "metrical_value_amp"))
