# GCI-Practice  

This program is intended to help new GCIs gain confidence processing information and making unprompted calls.  

## Installation instructions  

### Installing python 3.11  

This program was made in python 3.11. It may work with later versions, but is untested and may result in
unforseen consequences. To install python, go to [python.org](https://www.python.org/) and install version 3.11.x (or
later if you're feeling risky). Once the .exe is downloaded, follow the instructions in the installer, and make sure to
enable adding python to PATH.

### Setting up your install  

To get started, extract the .zip file into its own folder. In my attempts to make this app easier to develop, I've 
forgone Marlan's suggestion to use pyinstaller for the moment (mostly because I don't want to troubleshoot 
it/restructure the project). In its place we have the wonderful setup.py file. Just open it and all the system stuff
will be handled for you. To customize your install, go to `Resources/config.toml` and edit the section labeled `# User
setup variables`. The only ones there for the time being should be `alias` (your name) and `sr_key` (your speech 
recognition key). Now just run main.py to get running!

## A guide to the app

My UI design isn't exactly top-tier, but I tried to keep the interface as simple as possible and easy to navigate. 
Along the top is the infobar, which shouldn't be used unless there is an error, or you are testing the interface. Below
it is the canvas, where your radar pictures will be displayed when a problem is started. Clicking on the canvas will 
draw a braa line. Click once for the origin and once for the destination. Along the bottom is the answer bar, it is 
where you will give your answers to a problem. Moving to the top right, we have our settings box. It contains the problem
types that you want to enable, followed by the text to speech words per minute setting. Lastly is the problem management 
page, placed just below the settings box. It has the problem management buttons (submit your answers, redraw the page, and 
be given a new problem) and will give you corrections on your answers. You can hover over each correction for more detail
and an example.  

## Features/roadmap

### Features

Problem types: 

- Check-in  
- Threat  
- Caution  

Speech recognition
Text to speech  
Clickable radar screen  
BRAA and Bullseye table  
Answer checking  

### Roadmap

Given that I'm a single developer, the roadmap is subject to change depending on the weather, the phase of the moon, 
and whatever I feel like coding. It will give you a general idea of where the app will be heading and in what order though.  

- Polish UI and stuff
- More calls
- Dynamic missions? Idk I guess
