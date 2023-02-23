# GCI-Practice  

This program is intended to help new GCIs gain confidence processing information and making unprompted calls.  

## Installation instructions  

### Installing python 3.11  

This program was made in python 3.11. It may work with earlier or later versions, but is untested and may result in
unforseen consequences. To install python, go to [python.org](https://www.python.org/) and install version 3.11.x (or
later if you're feeling risky). Once the .exe is downloaded, follow the instructions in the installer, making sure to
enable adding pip to PATH.  

### Installing packages  

Once you've installed python, you'll have to use pip to install some packages. To do this, open up the terminal 
(cmd.exe on windows) and run the following commands:  
`pip install pyttsx3`  
`pip install SpeechRecognition`  
This will install all required packages for you to run the program.  

### Setting up your install  

Now that python is all set up, you'll need to customize your install. First, extract the .zip file into a separate 
directory For readability's sake, the program uses a .toml file for most of its configs. Using a text editor like 
notepad++ or similar, open the toml file and edit values in the "User setup variables" section of the document. Once 
that's done, just run main.py and you'll be good to go!

## A guide to the app

My UI design isn't exactly top-tier, but I tried to keep the interface as simple as possible and easy to navigate. 
Along the top is the infobar, which shouldn't be used unless there is an error or you are testing the interface. Below
it is the canvas, where your radar pictures will be displayed when a problem is started. Along the bottom is the answer
bar, it is where you will give your answers to a problem. Each problem has an intended page, and it will be opened for
you when the problem is chosen. Moving to the top right, we have our settings box. Along the top is a status indicator,
which should keep you up to date on what the program's doing. Below that are the problem type choices, followed by the
text to speech words per minute setting. Lastly is the problem management and BRAA page, placed just below the settings
box. It has the problem management buttons (submit your answers, redraw the page, and be given a new problem), and has
a table with BRAA and Bullseye measurements for each plane of interest.

## Features/roadmap

### Features

Problem types: 

- Check-in  
- Threat  
- Caution  

Radar screen  
BRAA and Bullseye table  
Answer checking  

### Roadmap

Given that I'm a single developer, the roadmap is subject to change depending on the weather, the phase of the moon, 
and whatever I feel like coding. It will give you a general idea of where the app will be heading and in what order though.  

- Internal rework
- Implement speech recognition
- Polish UI and stuff
