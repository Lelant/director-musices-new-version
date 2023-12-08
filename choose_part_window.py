import customtkinter
from util_functions import graphTitles

class ChoosePartWindow(customtkinter.CTkToplevel):

    def __init__(self, possibleParts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x400")
        self.title("Choose a part")

        # self.frameOptions = customtkinter.CTkFrame(master=self)
        # self.frameOptions.place(x=0, y=0, relheight=0.8, relwidth=1)

        # self.frameOptions.columnconfigure(len(voices), weight=1, uniform='v')
        # self.frameOptions.rowconfigure(4, weight=1, uniform='v')

        # self.frameButtons = customtkinter.CTkFrame(master=self)
        # self.frameButtons.place(x=0, rely=0.8, relheight=0.2, relwidth=1)

        # # keys: tuple of voice and graph title
        # self.checkboxes = dict()

        # for idx, voice in enumerate(voices):
        #     label = customtkinter.CTkLabel(master=self.frameOptions, text="Voice " + str(voice))
        #     label.grid(column=idx, row=0, padx=10, pady=10)

        #     var1 = customtkinter.BooleanVar(value=False)
        #     var2 = customtkinter.BooleanVar(value=False)
        #     var3 = customtkinter.BooleanVar(value=False)

        #     if (voice, graphTitles[0]) in lastCheckboxes:
        #         var1.set(lastCheckboxes[(voice, graphTitles[0])].get())
        #     if (voice, graphTitles[1]) in lastCheckboxes:
        #         var2.set(lastCheckboxes[(voice, graphTitles[1])].get())
        #     if (voice, graphTitles[2]) in lastCheckboxes:
        #         var3.set(lastCheckboxes[(voice, graphTitles[2])].get())

        #     checkbox1 = customtkinter.CTkCheckBox(master=self.frameOptions, text="Volume", variable=var1)
        #     checkbox2 = customtkinter.CTkCheckBox(master=self.frameOptions, text="Duration", variable=var2)
        #     checkbox3 = customtkinter.CTkCheckBox(master=self.frameOptions, text="Duration Difference", variable=var3)
            
        #     checkbox1.grid(column=idx, row=1, padx=10, pady=10, sticky='w')
        #     checkbox2.grid(column=idx, row=2, padx=10, pady=10, sticky='w')
        #     checkbox3.grid(column=idx, row=3, padx=10, pady=10, sticky='w')

        #     self.checkboxes[(voice, graphTitles[0])] = checkbox1
        #     self.checkboxes[(voice, graphTitles[1])] = checkbox2
        #     self.checkboxes[(voice, graphTitles[2])] = checkbox3

        # self.submitButton = customtkinter.CTkButton(master=self.frameButtons, text="Apply", command=self.applyPressed)
        # self.closeButton = customtkinter.CTkButton(master=self.frameButtons, text="Cancel", command=self.cancelPressed)

        # self.submitButton.place(relx=0.7, y=0)
        # self.closeButton.place(relx=0.3, y=0)

        # self.returnValue = None

    def applyPressed(self):
        self.returnValue = self.checkboxes
        self.destroy()

    def cancelPressed(self):
        self.destroy()

    def wait_for_values(self):
        self.wait_window()
        return self.returnValue