from scoreAndPerformance import scoreAndPerformance, add_attribute, add_duration, get_attribute, get_next_object, get_nominal_duration_sum, is_last_note, set_attribute
import partitura as pt
from util_functions import checkConditions
from rules.curve_functions import curve_functions

def mark_leap(voice):

    notes = scoreAndPerformance.getNotesOfVoice(voice)
    for idx, note in enumerate(notes):
        # change: removed the condition if this is a rest, because the notes array only consists of notes and no rests
        if checkConditions(lambda : not is_last_note(idx, notes),
                           lambda : not isinstance(get_next_object(note, object), pt.score.Rest)):

            # change: not including the uncommented code
            set_attribute(note, 'leap', get_next_object(note, pt.score.Note).midi_pitch - note.midi_pitch)

def level_to_bar_fraction(level, meter):
    bar_fraction = 1
    number_of_beats = get_list_length_for_level_and_meter(level, meter)

    # if zero, level and meter don't fit, return 0 to signal abortion
    if number_of_beats == 0:
        bar_fraction = 0

    if level == "T4":
        bar_fraction = 16
    elif level == "T2":
        bar_fraction = 8
    elif level == "T1":
        bar_fraction = 4
    else:
        bar_fraction = (1 / int(level)) * number_of_beats

    return bar_fraction

def cycle_to_bar_fraction(cycle, meter):
    bar_fraction = 1

    if cycle == "T4":
        bar_fraction = 4 * meter_to_number(meter)
    elif cycle == "T2":
        bar_fraction = 2 * meter_to_number(meter)
    elif cycle == "T1":
        bar_fraction = meter_to_number(meter)
    else:
        bar_fraction = 1 / int(cycle)

    return bar_fraction

def get_list_length_for_level_and_meter(level, meter):
    # all combinations of levels and meters, that need length of 4, are not checked and get the default value of 4
    list_length = 4

    if len(level) == 1:
        levelAsInt = int(level)

        # 2/4
        if meter[0] == 2 and meter[1] == 4:
            if levelAsInt == 1 or levelAsInt == 2:
                list_length = 0
        # 3/2
        if meter[0] == 3 and meter[1] == 2:
            if levelAsInt == 1:
                list_length = 0
            elif levelAsInt == 2:
                list_length = 3
            elif levelAsInt == 4:
                list_length = 6
        # 3/4
        if meter[0] == 3 and meter[1] == 4:
            if levelAsInt == 1 or levelAsInt == 2:
                list_length = 0
            elif levelAsInt == 4:
                list_length = 3
            elif levelAsInt == 8:
                list_length = 6
        # 6/4
        if meter[0] == 6 and meter[1] == 4:
            if levelAsInt == 1 or levelAsInt == 2:
                list_length = 0
            elif levelAsInt == 4 or levelAsInt == 8:
                list_length = 6
        # 3/4
        if meter[0] == 3 and meter[1] == 8:
            if levelAsInt == 1 or levelAsInt == 2 or levelAsInt == 4:
                list_length = 0
            elif levelAsInt == 8:
                list_length = 3
            elif levelAsInt == 16:
                list_length = 6
        # 6/8
        if meter[0] == 6 and meter[1] == 8:
            if levelAsInt == 1 or levelAsInt == 2:
                list_length = 0
            elif levelAsInt == 4:
                list_length = 4
            elif levelAsInt == 8 or levelAsInt == 16:
                list_length = 6
        # 9/8
        if meter[0] == 9 and meter[1] == 8:
            if levelAsInt == 1 or levelAsInt == 2:
                list_length = 0
            elif levelAsInt == 4:
                list_length = 3
            elif levelAsInt == 8:
                list_length = 9
            elif levelAsInt == 16:
                list_length = 6
        # 12/8
        if meter[0] == 12 and meter[1] == 8:
            if levelAsInt == 1:
                list_length = 0
            elif levelAsInt == 2 or levelAsInt == 4:
                list_length = 4
            elif levelAsInt == 8:
                list_length = 12
            elif levelAsInt == 16:
                list_length = 6
        # 6/16
        if meter[0] == 6 and meter[1] == 16:
            if levelAsInt == 2 or levelAsInt == 8:
                list_length = 4
            elif levelAsInt == 1 or levelAsInt == 4:
                list_length = 0
            elif levelAsInt == 16 or levelAsInt == 32:
                list_length = 6
        # 9/16
        if meter[0] == 9 and meter[1] == 16:
            if levelAsInt == 1 or levelAsInt == 2 or levelAsInt == 4:
                list_length = 0
            elif levelAsInt == 8:
                list_length = 3
            elif levelAsInt == 16:
                list_length = 9
            elif levelAsInt == 32:
                list_length = 6
        # 12/16
        if meter[0] == 12 and meter[1] == 16:
            if levelAsInt == 2 or levelAsInt == 8:
                list_length = 4
            elif levelAsInt == 1 or levelAsInt == 4:
                list_length = 0
            elif levelAsInt == 16:
                list_length = 12
            elif levelAsInt == 32:
                list_length = 6

    return list_length

def meter_to_number(meter):
    return meter[0] / meter[1]

# Ritardando rule for the bars that fall out of norm
# it is called every time there is a new restart on a bar
def add_ritardando_in_front(notes, index_restart, list_idx, lengths_in_fraction: list, standard_length, intensities, powers, functions):

    # get item at list_idx, if index out of range, get else
    length_in_fraction = lengths_in_fraction[list_idx] if lengths_in_fraction[list_idx:] else standard_length
    intensity = intensities[list_idx] if intensities[list_idx:] else 40
    power = powers[list_idx] if powers[list_idx:] else 2
    accfn = curve_functions[(functions[list_idx] if functions[list_idx:] else "power-fn") + "-acc"]
    decfn = curve_functions[(functions[list_idx] if functions[list_idx:] else "power-fn") + "-dec"]

    last_note = index_restart - 1
    first_note = index_restart - 1
    ack_fraction = 0

    # while loop for setting the index of the first note
    while ack_fraction < length_in_fraction:
        ack_fraction = ack_fraction + get_note_value_fraction()
        first_note = first_note - 1

    iadd_ramp_x2_decimal_last(notes, first_note, last_note, 0.0, 0.0, 0, intensity, "duration", power, accfn, decfn)

def get_note_value_fraction(note):
    return scoreAndPerformance.part.quarter_map(note.duration) / 4

# this function should put the curve values in a list and return the list
def make_list_ramp_x2_decimal_last(num_notes, start_val, end_val, power, accfn, decfn, smallest_ndr):
    return_list = []
    num_notes_minus_one = num_notes - 1
    endtime = num_notes_minus_one * smallest_ndr

    if not endtime > 0.0:
        print("WARNING: The segment does not have a positive duration")
    else:
        if start_val <= end_val:
            time = 0.0
            for i in range(0, int(num_notes_minus_one)):
                return_list.insert(0, start_val + ((end_val - start_val) * decfn(time / endtime, power)))
                time = time + smallest_ndr
        elif start_val > end_val:
            time = 0.0
            for i in range(0, int(num_notes_minus_one)):
                return_list.insert(0, end_val + ((start_val - end_val) * accfn(time / endtime, power)))
                time = time + smallest_ndr

    return list(reversed(return_list))

# same as the original, but it adds to the prop instead of setting it
def iadd_ramp_x2_decimal_last(notes, i_from, i_to, sdisp, edisp, sval, eval, prop, power, accfn, decfn):
    initdur = 0.0

    if sdisp > 0:
        if get_attribute(notes[i_from], "nominal_duration") != None:
            initdur = get_attribute(notes[i_from], "nominal_duration") - sdisp
            i_from = i_from + 1

    etime = get_nominal_duration_sum(i_from, i_to, notes) + initdur + edisp

    if not etime > 0.0:
        print("WARNING: The segment does not have a positive duration")
    elif get_attribute(notes[i], "nominal_duration") != None:
        if sval <= eval:
            time = initdur
            for i in range(i_from, i_to):
                addValue = sval + ((eval - sval) * decfn(time / etime, power))
                if prop == "duration":
                    add_duration(notes[i], addValue, i, notes)
                else:
                    add_attribute(notes[i], prop, addValue)
                time = time + get_attribute(notes[i], "nominal_duration")
        elif sval > eval:
            time = initdur
            for i in range(i_from, i_to):
                addValue = eval + ((sval - eval) * accfn(time / etime, power))
                if prop == "duration":
                    add_duration(notes[i], addValue, i, notes)
                else:
                    add_attribute(notes[i], prop, addValue)
                time = time + get_attribute(notes[i], "nominal_duration")

def check_list_length(list, meter, level):
    proper_length = get_list_length_for_level_and_meter(level, meter)
    new_list = []
    
    if proper_length == 0:
        print("The level {0} is not usable with the meter {1}/{2}. Please choose a different level.".format(level, meter[0], meter[1]))
    else:
        if len(list) > proper_length:
            print("The hierarchy list is too long. Only the first {0} numbers are used.".format(proper_length))
            new_list = list[:proper_length]
        elif len(list) < proper_length:
            print("{0} numbers with the value 50 are added to the end of the list.".format(proper_length - len(list)))
            print("The hierarchy list is too small. It should be {0} numbers long.".format(proper_length))
            list.extend([50 for i in range(proper_length - len(list))])
            new_list = list
        elif len(list) == proper_length:
            new_list = list

    return new_list

def apply_factors_to_list(quant, weight, the_list):
    return list(map(lambda x : quant * weight * 4 * (x / 100), the_list))

def make_list_of_beats(length, level, meter):
    iterator = 0
    return_list = []
    step_size = 0

    # set step_size
    if level == "T4":
        step_size = 4 * meter_to_number(meter)
    elif level == "T2":
        step_size = 2 * meter_to_number(meter)
    elif level == "T1":
        step_size = meter_to_number(meter)
    else:
        step_size = 1 / int(level)

    for i in range(length):
        return_list.append(iterator)
        iterator = iterator + step_size

    return return_list

def get_lenth_per_cent(total_length, absolute_length, meter):
    result = 0

    absolute_length = absolute_length * meter_to_number(meter)

    if absolute_length > total_length:
        print("Length of curve is longer than the cycle. It is set to the full length of the cycle.")
        result = 1
    else:
        result = absolute_length / total_length
    
    return result
