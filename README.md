# Director Musices Novus
This tool is a new version of **Director Musices** created as part of my master thesis. 

For more information on the original **Director Musices** follow these links:
- add link to dm github
- add link to dm github site
- add referenze to papers

## Installation

To use the tool, first clone this repository or download the files. Optionally create a virtual environment for Python using this command:
```
python -m venv /path/to/new/virtual/environment
```

Active the environment:
```
source /yourenvironment/bin/activate
```

Install the required packages:
```
pip install -r requirements.txt
```

To start the tool, run the **main.py** file.

## Usage

![GUI](dmn-gui.png)

### The buttons and functions
- **Open a new score:** user can choose a new score (file formats: mei, musicxml, midi, humdrum **kern)
- **Set voices:** if selected, the voice estimation algorithm estimates the voices and assigns them to the notes (useful if score has no voice markings)
- **Open a midi performance:** user can choose a performance in midi format. The piece and the section/part should match the currently opened score!
- **Play:** playback of the rule generated performance
- **Apply:** applying all selected rules with the respective parameters to generate a performance
- **Show score as Graph:** if selected while pressing apply, a graph showing every voice as a line will be displayed (y-axis = midi-pitch, x-axis = time in quarternotes)
- **Export Performance:** exports the rule generated performance as midi file (named "rulegenerated_performance.mid")
- **Export Graphs:** exports all graphs and the piano roll as png files


## Adding new rules