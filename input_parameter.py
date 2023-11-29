import customtkinter

class StringInput:
    def __init__(self, masterFrame, columnNumber, defaultValue, displayName):
        self.value = customtkinter.StringVar(master=masterFrame, value=defaultValue)
        entry = customtkinter.CTkEntry(master=masterFrame, width=60, textvariable=self.value)
        label = customtkinter.CTkLabel(master=masterFrame, text=displayName + ":")
        label.grid(row=0, column=columnNumber, sticky="e", padx=2)
        entry.grid(row=0, column=columnNumber+1, sticky="w", padx=2)

class IntInput:
    def __init__(self, masterFrame, columnNumber, defaultValue, displayName):
        self.value = customtkinter.IntVar(master=masterFrame, value=defaultValue)
        entry = customtkinter.CTkEntry(master=masterFrame, width=60, textvariable=self.value)
        label = customtkinter.CTkLabel(master=masterFrame, text=displayName + ":")
        label.grid(row=0, column=columnNumber, sticky="e", padx=2)
        entry.grid(row=0, column=columnNumber+1, sticky="w", padx=2)

class DoubleInput:
    def __init__(self, masterFrame, columnNumber, defaultValue, displayName):
        self.value = customtkinter.DoubleVar(master=masterFrame, value=defaultValue)
        entry = customtkinter.CTkEntry(master=masterFrame, width=60, textvariable=self.value)
        label = customtkinter.CTkLabel(master=masterFrame, text=displayName + ":")
        label.grid(row=0, column=columnNumber, sticky="e", padx=2)
        entry.grid(row=0, column=columnNumber+1, sticky="w", padx=2)

class BooleanInput:
    def __init__(self, masterFrame, columnNumber, defaultValue, displayName):
        self.value = customtkinter.BooleanVar(master=masterFrame, value=defaultValue)
        entry = customtkinter.CTkEntry(master=masterFrame, width=60, textvariable=self.value)
        label = customtkinter.CTkLabel(master=masterFrame, text=displayName + ":")
        label.grid(row=0, column=columnNumber, sticky="e", padx=2)
        entry.grid(row=0, column=columnNumber+1, sticky="w", padx=2)
