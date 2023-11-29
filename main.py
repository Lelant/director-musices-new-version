import os
import customtkinter
from tkinter import filedialog
from scoreAndPerformance import scoreAndPerformance
from graph import PianoRoll
from rule_dictionary import allRules
from voices_window import ShowVoicesWindow

class ctkApp:

    num_open_rules = 0
    all_open_rules = []

    def __init__(self):
        customtkinter.set_appearance_mode("system")
        customtkinter.set_default_color_theme("blue")
        self.ctkRoot = customtkinter.CTk()
        self.ctkRoot.geometry("1200x600")
        self.ctkRoot.minsize(800, 600)
        self.ctkRoot.title("NEW DM")
        self.ctkRoot.update()

        self.show_voices_window = None

        self.frameControlls = customtkinter.CTkScrollableFrame(master=self.ctkRoot, width=200, orientation='vertical')
        self.frameControlls.place(x=0, y=0, relheight=1)

        self.frameGraphs = customtkinter.CTkScrollableFrame(master=self.ctkRoot, fg_color='#3c3c3c', orientation='vertical')
        self.frameGraphs.place(x=200, y=0, relheight=0.7, relwidth=0.8)

        self.frameRules = customtkinter.CTkScrollableFrame(master=self.ctkRoot, orientation='horizontal')
        self.frameRules.place(x=200, rely=0.7, relheight=0.3, relwidth=0.8)

        self.currentScoreLabel = customtkinter.CTkLabel(master=self.frameControlls, text="No score loaded")
        self.currentScoreLabel.pack(pady=12, padx=10)
        self.openScoreButton = customtkinter.CTkButton(master=self.frameControlls, text="Open a new score", command=self.openScore)
        self.openScoreButton.pack(pady=12, padx=10)
        self.setVoicesVar = customtkinter.BooleanVar(master=self.frameControlls, value=False)
        self.setVoicesCheckbox = customtkinter.CTkCheckBox(master=self.frameControlls, text="Set voices", variable=self.setVoicesVar)
        self.setVoicesCheckbox.pack(pady=12, padx=10)

        self.currentPerformanceLabel = customtkinter.CTkLabel(master=self.frameControlls, text="No performance loaded")
        self.currentPerformanceLabel.pack(pady=12, padx=10)
        self.openPerformanceButton = customtkinter.CTkButton(master=self.frameControlls, text="Open a midi performance", command=self.openPerformance)
        self.openPerformanceButton.pack(pady=12, padx=10)
        self.playButton = customtkinter.CTkButton(master=self.frameControlls, text="Play", command=self.playScore)
        self.playButton.pack(pady=12, padx=10)
        self.applyRulesButton = customtkinter.CTkButton(master=self.frameControlls, text="Apply", command=self.applyRules)
        self.applyRulesButton.pack(pady=12, padx=10)
        self.showScoreGraphVar = customtkinter.BooleanVar(master=self.frameControlls, value=False)
        self.showScoreGraphCheckbox = customtkinter.CTkCheckBox(master=self.frameControlls, text="Show Score as Graph", variable=self.showScoreGraphVar)
        self.showScoreGraphCheckbox.pack(pady=12, padx=10)
        self.exportFileButton = customtkinter.CTkButton(master=self.frameControlls, text="Export generated Performance as Midi", command=self.exportFile)
        self.exportFileButton.pack(pady=12, padx=10)
        self.exportGraphsButton = customtkinter.CTkButton(master=self.frameControlls, text="Export Graphs", command=self.exportGraphs)
        self.exportGraphsButton.pack(pady=12, padx=10)
        self.addRuleButton = customtkinter.CTkButton(master=self.frameControlls, text="Add Rule", command=self.add_rule_dialog)
        self.addRuleButton.pack(pady=12, padx=10)

        self.showVoicesButton = customtkinter.CTkButton(master=self.frameControlls, text="Show Voices", command=self.show_voices)
        self.showVoicesButton.pack(pady=12, padx=10)

        self.inputFiletypes = (('score files', '*.mid *.musicxml *.krn *mei'), ('midi files', '*.mid'), ('all files', '*.*'))

        self.testScorePath = "test_files/Mozart_copy.musicxml"
        self.currentScoreLabel.configure(text=os.path.basename(self.testScorePath))

        scoreAndPerformance.loadScore(self.testScorePath, self.frameGraphs)

        self.pianoRoll = PianoRoll(scoreAndPerformance.getPianoRoll(), self.frameGraphs)

        rowIndexList = [*range(len(scoreAndPerformance.getVoices()) * 3)]
        self.frameGraphs.columnconfigure(0, weight=1)
        self.frameGraphs.rowconfigure(rowIndexList, weight=1)

        self.voicesCheckboxes = dict()

        self.add_rule('high loud')
        self.add_rule('metrical amp')
        self.add_rule('metrical dur')
        self.add_rule('decrease amp')
        self.add_rule('decrease dur')

        self.ctkRoot.mainloop()

    def exportFile(self):
        scoreAndPerformance.export_performedPart_as_midi()

    def exportGraphs(self):
        for key in scoreAndPerformance.graphs:
            scoreAndPerformance.graphs[key].exportPng(key[0] + "-" + key[1])
        self.pianoRoll.exportPng('pianoRoll.png')

    def openScore(self):
        filepath = filedialog.askopenfilename(title="Choose a score", filetypes=self.inputFiletypes)
        print(filepath)
        if filepath == "":
            return
        scoreAndPerformance.loadScore(filepath, self.frameGraphs, self.setVoicesVar.get())
        self.currentScoreLabel.configure(text=os.path.basename(filepath))

        self.update_graphs()

        for rule in self.all_open_rules:
            rule.checkbox.deselect()

    def openPerformance(self):
        filepath = filedialog.askopenfilename(title="Choose a midi performance", filetypes=self.inputFiletypes)
        print(filepath)
        if filepath == "":
            return
        
        scoreAndPerformance.loadPerformance(filepath)
        self.currentPerformanceLabel.configure(text=os.path.basename(filepath))

        self.update_graphs()

        for rule in self.all_open_rules:
            rule.checkbox.deselect()

    def playScore(self):
        self.setPlayButtonToPlaying()
        print("playing...")
        scoreAndPerformance.playScore()
        self.checkPlayingLoop()

    def stopScore(self):
        print("Playback stopped")
        scoreAndPerformance.stopPlayback()
        self.setPlayButtonToIdle()

    def checkPlayingLoop(self):
        if scoreAndPerformance.scoreIsPlaying():
            self.ctkRoot.after(100, self.checkPlayingLoop)
        else:
            print("Playback finished")
            self.setPlayButtonToIdle()

    def setPlayButtonToIdle(self):
        self.playButton.configure(text="Play")
        self.playButton.configure(command=self.playScore)

    def setPlayButtonToPlaying(self):
        self.playButton.configure(text="Stop")
        self.playButton.configure(command=self.stopScore)

    def applyRules(self):
        scoreAndPerformance.resetToDefault()

        for rule in self.all_open_rules:
            if rule.checkbox.get():
                print("Applying rule: {0}".format(rule))
                rule.apply()

        self.update_graphs()

    def update_graphs(self):
        scoreAndPerformance.forget_all_graphs()
        
        positionIndex = 0

        if self.showScoreGraphCheckbox.get():
            for voice in scoreAndPerformance.getVoices():
                notePositions = scoreAndPerformance.getNotePositions(voice)
                pitches = scoreAndPerformance.getPitches(voice)
                scoreAndPerformance.scoreGraph.setLine(notePositions, pitches, voice)

            scoreAndPerformance.scoreGraph.setGridTrue()
            scoreAndPerformance.scoreGraph.position(positionIndex)
            positionIndex += 1

        for key in scoreAndPerformance.graphs:
            # the keys of scoreAndPerformance.graphs and self.voicesCheckboxes should be the same
            if key in self.voicesCheckboxes:
                if self.voicesCheckboxes[key].get():

                    # getData takes the two tuple values of the dictionary key (voice and graph title)
                    scoreData = scoreAndPerformance.getScoreData(key[0], key[1])
                    performedData = scoreAndPerformance.getPerformedData(key[0], key[1])
                    loadedPerformedData = scoreAndPerformance.getLoadedPerformedData(key[0], key[1])
                    notePositions = scoreAndPerformance.getNotePositions(key[0])

                    scoreAndPerformance.graphs[key].setValues(scoreData, performedData, loadedPerformedData, notePositions)
                    scoreAndPerformance.graphs[key].position(positionIndex)
                    positionIndex += 1

    def add_rule_dialog(self):
        dialog = customtkinter.CTkInputDialog(text="Type in the rule name:", title="Add Rule")
        userinput = dialog.get_input()
        print(allRules)
        for key in allRules:
            if userinput == key:
                self.add_rule(key)

    def add_rule(self, rulename):
        self.frameRules.rowconfigure(self.num_open_rules, weight=1)
        newrule = allRules[rulename](frame=self.frameRules, row=self.num_open_rules, column=0)
        self.num_open_rules = self.num_open_rules + 1
        self.all_open_rules.append(newrule)

    def show_voices(self):
        if self.show_voices_window is None or not self.show_voices_window.winfo_exists():
            self.show_voices_window = ShowVoicesWindow(self.voicesCheckboxes, scoreAndPerformance.getVoices())
            resultDictionary = self.show_voices_window.wait_for_values()

            if resultDictionary != None:
                self.voicesCheckboxes = resultDictionary
                self.update_graphs()
        else:
            self.show_voices_window.focus()

if __name__ == "__main__":
    CTK_Window = ctkApp()