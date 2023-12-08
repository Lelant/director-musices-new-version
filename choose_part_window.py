import customtkinter
from functools import partial

class ChoosePartWindow(customtkinter.CTkToplevel):

    def __init__(self, possibleParts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x400")
        self.title("Choose a part")

        self.frameOptions = customtkinter.CTkFrame(master=self)
        self.frameOptions.place(x=0, y=0, relheight=0.8, relwidth=1)

        self.frameOptions.columnconfigure(1, weight=1, uniform='v')
        self.frameOptions.rowconfigure(len(possibleParts), weight=1, uniform='v')

        self.frameButtons = customtkinter.CTkFrame(master=self)
        self.frameButtons.place(x=0, rely=0.8, relheight=0.2, relwidth=1)

        self.checkboxesAndVars = dict()

        for idx, part in enumerate(possibleParts):
            if part.part_name != None and part.part_name != "":
                partname = ": "+part.part_name
            else:
                partname = ""

            partVar = customtkinter.BooleanVar(value=False)

            checkBox = customtkinter.CTkCheckBox(master=self.frameOptions, text="Part "+str(idx+1)+partname, variable=partVar)
            action_with_arg = partial(self.checkbox_ticked, idx)
            checkBox.configure(command= action_with_arg)
            checkBox.grid(column=0, row=idx, padx=10, pady=10, sticky='w')

            self.checkboxesAndVars[str(idx)] = [checkBox, partVar, part]

        self.submitButton = customtkinter.CTkButton(master=self.frameButtons, text="Apply", command=self.applyPressed)
        self.closeButton = customtkinter.CTkButton(master=self.frameButtons, text="Cancel", command=self.cancelPressed)

        self.submitButton.place(relx=0.7, y=0)
        self.closeButton.place(relx=0.3, y=0)

        self.returnValue = None

    def checkbox_ticked(self, index):
        for key in self.checkboxesAndVars:
            if key != str(index):
                self.checkboxesAndVars[key][1].set(0)

    def applyPressed(self):
        for key in self.checkboxesAndVars:
            if self.checkboxesAndVars[key][1].get():
                self.returnValue = self.checkboxesAndVars[key][2]
                break
        self.destroy()

    def cancelPressed(self):
        self.destroy()

    def wait_for_values(self):
        self.wait_window()
        return self.returnValue