import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Graph:

    def __init__(self, title, voice, frameGraph, ylabelDescription):
        # print(plt.style.available) # print available styles
        # plt.style.use('seaborn-v0_8-deep')

        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(5, 2)
        # self.fig.set_figwidth(300)
        # self.fig.set_figheight(30)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frameGraph)
        self.title = title
        self.ax.set_xlabel('Notes')
        self.ax.set_ylabel(ylabelDescription)
        self.ax.set_title(title + str(voice))

    def setValues(self, valueListNotated, valueListPerformed, valueListLoadedPerformed, notePositions):
        self.ax.clear()
        # score is red
        self.ax.plot(notePositions, valueListNotated, color='r', linestyle='-', marker='.', label='Score Notes')
        # generated performance is green
        self.ax.plot(notePositions, valueListPerformed, color='g', linestyle='-', marker='.', label='Performance Notes')
        # loaded performance is blue
        self.ax.plot(notePositions, valueListLoadedPerformed, color='b', linestyle='-', marker='.', label='Loaded Notes')
        self.ax.grid(True)

    def setValuesSingle(self, valueListPerformed, notePositions):
        self.ax.clear()
        self.ax.plot(notePositions, valueListPerformed, color='g', linestyle='-', marker='.', label='Performance Notes')
        self.ax.grid(True)

    def clear(self):
        self.ax.clear()

    def setLine(self, yList, xList, label):
        self.ax.plot(yList, xList, linestyle='-', marker='.', label=label)

    def setGridTrue(self):
        self.ax.grid(True)

    def position(self, row):
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=0, row=row)

    def forgetGraph(self):
        self.canvas.get_tk_widget().grid_forget()

    def exportPng(self, filename):
        self.fig.savefig("exported_graphs/" + filename)

class PianoRoll:

    def __init__(self, pianoroll, frameGraph):
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=frameGraph)
        self.ax.imshow(pianoroll.toarray(), origin="lower", cmap='gray', interpolation='nearest', aspect='auto')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Piano key')

    def position(self, row):
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=0, row=row)

    def exportPng(self, filename):
        self.fig.savefig("exported_graphs/" + filename)
