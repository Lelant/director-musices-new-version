import customtkinter

class Rule:

    def __init__(self, frame, row, column, rulename):

        self.ruleFrame = customtkinter.CTkFrame(master=frame)
        self.ruleFrame.grid(row=row, column=column, sticky="w")

        self.ruleFrame.rowconfigure(0, weight=1)
        self.ruleFrame.columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)#, uniform='a')

        self.quantValue = customtkinter.DoubleVar(master=self.ruleFrame, value=1.0)

        self.checkbox = customtkinter.CTkCheckBox(master=self.ruleFrame, text=rulename)
        self.checkbox.grid(row=0, column=0, sticky="w", padx=10)

        self.sliderValueEntry = customtkinter.CTkEntry(master=self.ruleFrame, width=60, textvariable=self.quantValue)
        self.sliderValueEntry.grid(row=0, column=1, sticky="e", padx=10)

        self.slider = customtkinter.CTkSlider(master=self.ruleFrame, from_=-5.0, to=5.0, variable=self.quantValue)
        self.slider.grid(row=0, column=2, sticky="w", padx=10)
