import os
import partitura as pt
from partitura import utils as ptutils
from partitura import musicanalysis
from partitura.utils import music as ptmusic
import parangonar as pa
from graph import Graph
from util_functions import graphTitles, graphYlabels, sound_level_to_velocity, velocity_to_sound_level
import pygame

class ScoreAndPerformance:

    def __init__(self):
        self.performedPart = None
        self.loadedPerformedPart = None
        self.graphs = None
        self.scoreGraph = None

    def loadScore(self, path: str, frameGraphs, setVoices=False):
        self.frameGraphs = frameGraphs
        path_no_extension, file_extension = os.path.splitext(path)
        if file_extension == ".musicxml" or file_extension == ".mei" or file_extension == ".mid" or file_extension == ".krn":

            self.forget_all_graphs()

            try:
                self.part = pt.load_score_as_part(path)

                # create list of all notes and rests
                self.notesAndRests = self.makeListOfAllNotesAndRests()

                if not self.allNotesMarkedWithVoice():
                    self.estimate_and_set_voices()
                elif setVoices:
                    self.estimate_and_set_voices()

                self.performedPart = ptmusic.performance_from_part(self.part)

                self.removeAllTickInfoFromPerformance()

                self.setNominalDurations()
                self.setNominalSoundLevels()

                if self.loadedPerformedPart != None:
                    self.alignPerformanceToScore(self.loadedPerformedPart)

                # setup graphs
                self.setupScoreGraph()
                self.setupGraphs()

                # self.setChordInfos()

                print("Finished loading the score.")

            except Exception as error:
                print("ERROR while loading score file:", type(error).__name__, "-", error)
                
                try:
                    self.part = pt.load_score(path)
                    print("num of parts is: {0}".format(len(self.part.parts)))
                except Exception as error:
                    print("ERROR while loading score file with different approach:", type(error).__name__, "-", error)                

        else:
            print("The file extension {0} is note supported! No score loaded.".format(file_extension))

    # this can only be called if loadScore has run once
    def loadPerformance(self, path: str):
        path_no_extension, file_extension = os.path.splitext(path)
        if file_extension == ".mid":

            self.forget_all_graphs()

            loadedPerformance = pt.load_performance_midi(path)
            print("The loaded performance has {0} parts.".format(len(loadedPerformance.performedparts)))
            self.loadedPerformedPart = loadedPerformance.performedparts[0]

            # set the same ids
            self.alignPerformanceToScore(self.loadedPerformedPart)

            print("Finished loading the performance.")
        else:
            print("The file extension {0} is note supported! No performance loaded.".format(file_extension))

    def makeListOfAllNotesAndRests(self):
        print("Creating list of all notes and rests...")
        l = []
        for obj in scoreAndPerformance.part.iter_all():
            if isinstance(obj, pt.score.Note) or isinstance(obj, pt.score.Rest):
                l.append(obj)
        print("Done")
        return l
    
    def removeAllTickInfoFromPerformance(self):
        for n in scoreAndPerformance.performedPart.notes:
            n.pop('note_on_tick', None)
            n.pop('note_off_tick', None)

    def setNominalDurations(self):
        print("Setting the nominal durations...")

        # calculating with "rule of three", because performed note_array has no rests
        idReference = self.part.notes[0].id
        durationReference = self.part.notes[0].duration

        if durationReference <= 0.0:
            # find the first duration that is not negative or zero
            for note in self.part.notes:
                durationReference = note.duration
                idReference = note.id
                if durationReference > 0.0:
                    break

        for performedNote in ptmusic.performance_from_part(self.part).note_array():
            if performedNote['id'] == idReference:
                nominalDurationReference = performedNote['duration_sec']
                break

        for noteRest in self.notesAndRests:
            set_attribute(noteRest, 'nominal_duration', (noteRest.duration * nominalDurationReference) / durationReference)

        print("Done")

    def setNominalSoundLevels(self):
        print("Setting the nominal sound levels...")
        for note in self.part.notes:
            set_attribute(note, 'sound_level', 0.0)
        print("Done")

    # this adds the q attribute to the notes
    def setChordInfos(self):
        print("Setting the chord pitches variables...")
        for note in self.part.notes:
            set_attribute(note, 'q', get_chord_pitches(note, same_duration=True, same_voice=False))
        print("Done")
    # INFO:
    # in DM q is "Cmaj" or ("C", "E", "G")
    # in DM, the root is always the first in the list
    # here it is a list of midi_pitches [40, 42, 44]
    # here the list is not sorted, the root can be anywhere

    def setupScoreGraph(self):
        self.scoreGraph = Graph("Partitur", "all voices", self.frameGraphs, "Midi Pitch")

    def setupGraphs(self):
        print("Setting up the graphs...")
        # graphs is a dictionary
        # keys: tuple of voice and graph title
        # values: the graph object
        self.graphs = dict()
        for voice in self.getVoices():
            for i in range(3): # 3 graphs for each voice
                self.graphs[(voice, graphTitles[i])] = Graph(graphTitles[i], voice, self.frameGraphs, graphYlabels[i])
        print("Done")

    def forget_all_graphs(self):
        if self.scoreGraph != None:
            self.scoreGraph.forgetGraph()

        if self.graphs != None:
            for key in self.graphs:
                self.graphs[key].forgetGraph()

    # this is only necessary if a performance is loaded, but not if it is generated from the score
    def alignPerformanceToScore(self, performanceToAlign):
        print("Aligning Performance to Score...")
        sdm = pa.AutomaticNoteMatcher()
        self.scorePerformanceAlignment = sdm(self.part.note_array(), performanceToAlign.note_array())

        # change the ids of the performance notes to match the score notes ids
        for performedNote in performanceToAlign.notes:
            correspondingScoreID = None

            for dictionary in self.scorePerformanceAlignment:
                if dictionary['label'] == 'match':
                    if dictionary['performance_id'] == performedNote['id']:
                        correspondingScoreID = dictionary['score_id']
                        break

            if correspondingScoreID == None:
                print("FATAL ERROR: Could not find the corresponding score ID for the performed note with id {0}".format(performedNote['id']))
            else:
                performedNote['id'] = correspondingScoreID
        print("Done")

    def getNotesOfVoice(self, voice):
        array = []
        for note in self.part.notes:
            if note.voice == voice:
                array.append(note)
        return array
    
    def getNotesAndRestsOfVoice(self, voice):
        array = []
        for nr in self.notesAndRests:
            if nr.voice == voice:
                array.append(nr)
        return array

    def getNextNotesOfVoice(self, voice, startNote):
        array = []
        for nextNote in startNote.start.iter_next(pt.score.Note):
            if nextNote.voice == voice:
                array.append(nextNote)
        return array

    def playScore(self):
        self.export_performedPart_as_midi("temp_files/tempPerformanceForPlayback")

        pygame.init()
        pygame.mixer.music.load("temp_files/tempPerformanceForPlayback.mid")
        pygame.mixer.music.play()
    
    def stopPlayback(self):
        pygame.mixer.music.stop()

    def scoreIsPlaying(self):
        return pygame.mixer.music.get_busy()

    def resetToDefault(self):
        # reset all values to default, no rule applied
        self.performedPart = ptmusic.performance_from_part(self.part)
        self.removeAllTickInfoFromPerformance()
        self.setNominalDurations()
        self.setNominalSoundLevels()

    def getPianoRoll(self):
        return ptutils.compute_pianoroll(self.performedPart, pitch_margin=2, onset_only=False)

    def export_performedPart_as_midi(self, filename):
        # change velocity according to sound_level
        for note in self.part.notes:
            if get_attribute(note, "sound_level") != None:
                get_performed_note(note)['velocity'] = sound_level_to_velocity(get_attribute(note, "sound_level"))
        
        pt.save_performance_midi(self.performedPart, filename+".mid")

    def getVoices(self):
        voices = []
        for note in self.part.notes:
            if not note.voice in voices:
                voices.append(note.voice)
        return voices

    # check if all notes have a voice assigned to them, return true or false
    def allNotesMarkedWithVoice(self):
        for note in self.notesAndRests:
            if not note.voice:
                print("There is at least one note without a voice marking!")
                return False
        return True

    def estimate_and_set_voices(self, monophonic_voices=True):
        print("Estimating and setting the voices...")
        # only estimating voices for notes but not for rests! See issue https://github.com/CPJKU/partitura/issues/330
        newVoices = musicanalysis.estimate_voices(self.part, monophonic_voices)
        for i in range(len(newVoices)):
            self.part.notes[i].voice = newVoices[i]
        print("Done")

    # --------------------------------------------
    # Getting Methods for note data to display in graphs
    # --------------------------------------------

    def getScoreData(self, voice, graphTitle):
        datalist = []

        for note in self.getNotesOfVoice(voice):
            # if graphTitle is Volume
            if graphTitle == graphTitles[0]:
                datalist.append(0.0)
            # if graphTitle is Duration
            elif graphTitle == graphTitles[1]:
                datalist.append(get_attribute(note, 'nominal_duration'))
            # if graphTitle is Duration difference
            elif graphTitle == graphTitles[2]:
                datalist.append(0.0)

        return datalist

    def getPerformedData(self, voice, graphTitle):
        datalist = []

        for note in self.getNotesOfVoice(voice):
            # if graphTitle is Volume
            if graphTitle == graphTitles[0]:
                datalist.append(get_attribute(note, 'sound_level'))
            # if graphTitle is Duration
            elif graphTitle == graphTitles[1]:
                datalist.append(get_attribute(note, 'duration_sec'))
            # if graphTitle is Duration difference
            elif graphTitle == graphTitles[2]:
                nominal_duration = get_attribute(note, 'nominal_duration')
                if nominal_duration == None:
                    difference = 0.0
                else:
                    difference = round(get_attribute(note, 'duration_sec') - nominal_duration, 5)
                datalist.append(difference)

        return datalist

    def getLoadedPerformedData(self, voice, graphTitle):
        datalist = []

        for note in self.getNotesOfVoice(voice):

            if self.loadedPerformedPart == None:
                datalist.append(None)
            elif get_loaded_performed_note(note) == None:
                datalist.append(None)
            else:
                # if graphTitle is Volume
                if graphTitle == graphTitles[0]:
                    datalist.append(velocity_to_sound_level(get_loaded_performed_note(note)['velocity']))
                # if graphTitle is Duration
                elif graphTitle == graphTitles[1]:
                    datalist.append(get_property_from_loaded_performed_note_array(note, 'duration_sec'))
                # if graphTitle is Duration difference
                elif graphTitle == graphTitles[2]:
                    nominal_duration = get_attribute(note, 'nominal_duration')
                    if nominal_duration == None:
                        difference = 0.0
                    else:
                        difference = round(get_property_from_loaded_performed_note_array(note, 'duration_sec') - nominal_duration, 5)
                    datalist.append(difference)

        return datalist
    
    def getPitches(self, voice):
        datalist = []

        for note in self.getNotesOfVoice(voice):
            datalist.append(note.midi_pitch)

        return datalist

    def getNotePositions(self, voice):
        datalist = []

        for note in self.getNotesOfVoice(voice):
            datalist.append(get_property_from_part_note_array(note, 'onset_quarter'))

        return datalist

scoreAndPerformance = ScoreAndPerformance()


def is_last_timepoint(timepoint):
    if timepoint.t == scoreAndPerformance.part.last_point.t:
        return True
    else:
        return False

def is_last_note(current_idx, current_list):
    if current_idx == len(current_list) - 1:
    # if note.end.t == scoreAndPerformance.part.last_point.t:
        return True
    else:
        return False

def is_second_last_note(current_idx, current_list):
    if current_idx == len(current_list) - 2:
    # if note.end.t == scoreAndPerformance.part._points[-2].t:
        return True
    else:
        return False

def is_first_note(current_idx):
    if current_idx == 0:
    # if note.start.t == scoreAndPerformance.part.first_point.t:
        return True
    else:
        return False

def is_second_note(current_idx):
    if current_idx == 1:
    # if note.start.t == scoreAndPerformance.part._points[1].t:
        return True
    else:
        return False

def is_sharp(note):
    if note.alter == 1:
        return True
    else:
        return False

def is_flat(note):
    if note.alter == -1:
        return True
    else:
        return False

def get_next_object(start_obj, type):
    for obj in start_obj.start.iter_next(type):
        return obj

def get_prev_object(start_obj, type):
    for obj in start_obj.start.iter_prev(type):
        return obj

def get_idx_of_next_object_with_property(start_obj, current_idx, type, property):
    for obj in start_obj.start.iter_next(type):
        current_idx += 1
        if get_attribute(obj, property) != None:
            return current_idx

def get_idx_of_prev_object_with_property(start_obj, current_idx, type, property):
    for obj in start_obj.start.iter_prev(type):
        current_idx -= 1
        if get_attribute(obj, property) != None:
            return current_idx

def get_idx_of_last_obj(current_list):
    return len(current_list) - 1

def get_idx_of_performed_note(note):
    i = 0
    for current_note in scoreAndPerformance.performedPart.notes:
        if note.id == current_note['id']:
            return i
        i += 1

# returns the measure number at the note position, or none
def get_measure_number(note):
    measure_number = None
    if pt.score.Measure in note.start.starting_objects: # this is a dictionary
        for measure_object in note.start.starting_objects[pt.score.Measure]:
            # taking the first measure object
            measure_number = measure_object.number
            break
    return measure_number

# def get_time_signature(note):
#     time_signature = None
#     if pt.score.TimeSignature in note.start.starting_objects:
#         for time_signature_object in note.start.starting_objects[pt.score.TimeSignature]:
#             # taking the first
#             time_signature = time_signature_object
#             break
#     return time_signature

# --------------------------------------------
# Methods for getting performance note values
# --------------------------------------------

def get_nominal_duration_sum(idx_from, idx_to, current_note_list):
    sumValue = 0.0
    for idx in range(idx_from, idx_to):
        sumValue += get_attribute(current_note_list[idx], 'nominal_duration')
    return sumValue

def get_duration_sum(idx_from, idx_to, current_note_list):
    sumValue = 0.0
    for idx in range(idx_from, idx_to):
        sumValue += get_attribute(current_note_list[idx], 'duration_sec')
    return sumValue

def get_idx_of_note_at_duration_sum(start_idx, current_note_list, duration_sum):
    sumValue = 0.0
    for idx in range(start_idx, len(current_note_list)):
        if sumValue >= duration_sum:
            return idx
        sumValue += get_attribute(current_note_list[idx], 'duration_sec')

# --------------------------------------------
# Methods for adding and setting performance note values
# --------------------------------------------

def set_duration(_note, value, noteIdx, currentNotesAndRestsOfSameVoice):
    difference = value - get_property_from_performed_note_array(get_performed_note(_note), 'duration_sec')

    set_attribute_using_performed_note_array(get_performed_note(_note), 'duration_sec', value)

    for i in range(noteIdx+1, len(currentNotesAndRestsOfSameVoice)):
        add_attribute_using_performed_note_array(get_performed_note(currentNotesAndRestsOfSameVoice[i]), 'onset_sec', difference)

def add_duration(_note, value, noteIdx, currentNotesAndRestsOfSameVoice):
    add_attribute_using_performed_note_array(get_performed_note(_note), 'duration_sec', value)

    for i in range(noteIdx+1, len(currentNotesAndRestsOfSameVoice)):
        add_attribute_using_performed_note_array(get_performed_note(currentNotesAndRestsOfSameVoice[i]), 'onset_sec', value)

def get_chord_pitches(note, same_duration=True, same_voice=True):
    chord_pitches = []
    for chord_note in note.iter_chord(same_duration, same_voice):
        if isinstance(chord_note, pt.score.Note):
            chord_pitches.append(chord_note.midi_pitch)
    return chord_pitches

def get_first_note():
    return scoreAndPerformance.part.notes[0]

# get the corresponding performed note of a score note from the notes list
# returns None if no note is found with a matching id
def get_performed_note(_note):
    for note in scoreAndPerformance.performedPart.notes:
        if note['id'] == _note.id:
            return note

def get_loaded_performed_note(_note):
    for note in scoreAndPerformance.loadedPerformedPart.notes:
        if note['id'] == _note.id:
            return note

# --------------------------------------------
# New methods for getting, setting and adding note attributes of score notes
# --------------------------------------------

# all these functions take a score note.

# return None if attribute doesn't exist
def get_attribute(_note, attribute):
    try:
        # if attribute is in the normal note object
        if attribute in dir(_note):
            return getattr(_note, attribute)

        # if attribute only exists in the note_array
        if attribute in scoreAndPerformance.part.note_array().dtype.names:
            return get_property_from_part_note_array(_note, attribute)

        # if the note is a performed note and the attribute is only in the note_array
        if attribute in scoreAndPerformance.performedPart.note_array().dtype.names:
            return get_property_from_performed_note_array(get_performed_note(_note), attribute)

        # else try to get the attribute from the performed note
        else:
            return get_performed_note(_note)[attribute]
    except:
        return None

def set_attribute(_note, attribute, newValue):
    # check if there is a corresponding performed note
    # if attribute in performed note
    if get_performed_note(_note) and attribute in get_performed_note(_note):
        get_performed_note(_note)[attribute] = newValue
    # if attribute in performed note array
    elif get_performed_note(_note) and attribute in scoreAndPerformance.performedPart.note_array().dtype.names:
        set_attribute_using_performed_note_array(get_performed_note(_note), attribute, newValue)
    else:
        setattr(_note, attribute, newValue)

def add_attribute(_note, attribute, addValue):
    # if attribute in normal score note
    if attribute in dir(_note):
        try:
            setattr(_note, attribute, getattr(_note, attribute) + addValue)
        except:
            print("Error on adding to attribute {0}".format(attribute))
    # check if there is a corresponding performed note
    elif get_performed_note(_note):
        # if attribute in performed note
        if attribute in get_performed_note(_note):
            get_performed_note(_note)[attribute] += addValue
        # if attribute in performed note array
        elif attribute in scoreAndPerformance.performedPart.note_array().dtype.names:
            add_attribute_using_performed_note_array(get_performed_note(_note), attribute, addValue)
    else:
        print("Could not add to attribute {0}".format(attribute))

def multiply_attribute(_note, attribute, multiplyValue):
    # if attribute in normal score note
    if attribute in dir(_note):
        try:
            setattr(_note, attribute, getattr(_note, attribute) * multiplyValue)
        except:
            print("Error on multiplying to attribute {0}".format(attribute))
    # check if there is a corresponding performed note
    elif get_performed_note(_note):
        # if attribute in performed note
        if attribute in get_performed_note(_note):
            get_performed_note(_note)[attribute] *= multiplyValue
        # if attribute in performed note array
        elif attribute in scoreAndPerformance.performedPart.note_array().dtype.names:
            multiply_attribute_using_performed_note_array(get_performed_note(_note), attribute, multiplyValue)
    else:
        print("Could not add to attribute {0}".format(attribute))

def remove_attribute(_note, attribute):
    # only possible for score notes (and not for note_arrays or performed notes)
    try:
        delattr(_note, attribute)
    except:
        print("Could not remove attribute {0} from note {1}".format(attribute, _note))

def set_all(attribute, value):
    # only possible for score notes (and not for note_arrays or performed notes)
    for note in scoreAndPerformance.part.notes:
        setattr(note, attribute, value)

def remove_all(attribute):
    # only possible for score notes (and not for note_arrays or performed notes)
    for note in scoreAndPerformance.part.notes:
        try:
            delattr(note, attribute)
        except:
            print("Could not remove attribute {0} from note {1}".format(attribute, note))

# --------------- Help functions for getter, setter, adder, remover ------------------------

# # input needs a score note!
# def get_note_from_part_note_array(_note):
#     for note in scoreAndPerformance.part.note_array():
#         if note['id'] == _note.id:
#             return note

# # input needs a performed note!
# def get_note_from_performed_note_array(_note):
#     for note in scoreAndPerformance.performedPart.note_array():
#         if note['id'] == _note['id']:
#             return note

def get_property_from_part_note_array(_scoreNote, property):
    for note in scoreAndPerformance.part.note_array():
        if note['id'] == _scoreNote.id:
            return note[property]

def get_property_from_performed_note_array(_performedNote, property):
    for note in scoreAndPerformance.performedPart.note_array():
        if note['id'] == _performedNote['id']:
            return note[property]

def get_property_from_loaded_performed_note_array(_scoreNote, property):
    for note in scoreAndPerformance.loadedPerformedPart.note_array():
        if note['id'] == _scoreNote.id:
            return note[property]

# input needs a performed note!
def set_attribute_using_performed_note_array(_performedNote, attribute, newValue):
    performanceNoteArray = scoreAndPerformance.performedPart.note_array()
    for note in performanceNoteArray:
        if _performedNote['id'] == note['id']:
            note[attribute] = newValue
    scoreAndPerformance.performedPart = pt.performance.PerformedPart.from_note_array(performanceNoteArray)
    scoreAndPerformance.removeAllTickInfoFromPerformance()

# input needs a performed note!
def add_attribute_using_performed_note_array(_performedNote, attribute, addValue):
    performanceNoteArray = scoreAndPerformance.performedPart.note_array()
    for note in performanceNoteArray:
        if _performedNote['id'] == note['id']:
            note[attribute] += addValue
    scoreAndPerformance.performedPart = pt.performance.PerformedPart.from_note_array(performanceNoteArray)
    scoreAndPerformance.removeAllTickInfoFromPerformance()

# input needs a performed note!
def multiply_attribute_using_performed_note_array(_performedNote, attribute, mulValue):
    performanceNoteArray = scoreAndPerformance.performedPart.note_array()
    for note in performanceNoteArray:
        if _performedNote['id'] == note['id']:
            note[attribute] *= mulValue
    scoreAndPerformance.performedPart = pt.performance.PerformedPart.from_note_array(performanceNoteArray)
    scoreAndPerformance.removeAllTickInfoFromPerformance()
