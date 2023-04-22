# GCI-Practice  

This program is intended to help new GCIs gain confidence processing information and making unprompted calls.

## Installation instructions  

### Installing python 3.11  

This program was made in python 3.11. It may work with later versions, but is untested and may result in unforseen consequences. To install python, go to [python.org](https://www.python.org/) and install version 3.11.x (or later if you're feeling risky). Once the .exe is downloaded, follow the instructions in the installer, and make sure to enable adding python to PATH.

### Setting up your install  

To get started, extract the .zip file into its own folder. Then run the setup.py file, and you should be off. **THERE IS A POSIBILITY THAT IT WILL FAIL, SEE FIXING SETUP ERRORS**. To customize your install, go to `Resources/config.toml` and edit the section labeled `# User setup variables`. The only ones there for the time being should be `alias` (your name) and `sr_key` (your speech recognition key). Now just run main.py to get running!

### Fixing setup errors

If you're here, then setup.py has failed for some reason. There are a few points at which it can do this, so I'll try to cover the expected ones. 

- **Please ensure all files are installed correctly**
   - This error occurs when the program detects that some of its requried files are missing. Make sure that you've downloaded the correct zip file, unzipped it into its own folder, and haven't moved its files
- **setup.py does not work on macos\[...]**
   - This one is rather self-explanatory. You'll have to manually download the requirements listed in requirements.txt (equivalent to the following + dependencies: pocketsphinx, pyaudio, pyttsx3).
- **Something went wrong trying to get python\'s version. Please check your python install.**
   - I'm honestly not too sure what could cause this, but this means that setup.py can't access your python install. Try running setup.py as administrator and, if that fails, re-installing python.
-  **Python should be version 3.11.x**
   - This seems self-explanatory, but is a bit trickier. The most obvious problem is that you might have installed the incorrect version of python. To check this, look in your python installation directory (by default `C:/Users/<your name>/AppData/Local/Programs/Python/`). If there is only one folder, uninstall your current python instance and re-download the correct installer from [python.org](https://www.python.org/). If there are multiple, you need to either edit your path variable to reference your python 3.11 install or uninstall your older versions.
- **Something went wrong...\[...]**
   - If you see this, something's really run amok. Please send a bug report to Damsel's server with the included error info **MAKING SURE TO EDIT OUT ANY PERSONAL INFORMATION BEFOREHAND**..
- **You need to install a C/C++ compiler \[...]**
   - This error is rather self-explanatory. Install [Visual Studio](https://visualstudio.microsoft.com/vs/) (or if you're more tech-savvy, your C/C++ compiler of choice) and you should be on your way.
- **Something went wrong installing a module**
   - This error means that pip failed to install one of the required packages. Please submit a bug report to Damsel's server with the included error info **MAKING SURE TO EDIT OUT ANY PERSONAL INFORMATION BEFOREHAND**.
- **\[Any other error/program closing unexpectedly]**
  - If you're seeing an error that's not listed above, congratulations, you've hit an uncaught exception! Please use cmd.exe to run setup.py by navigating to its directory and running `python setup.py`. Then submit a bug report to Damsel's server with the included error info **MAKING SURE TO EDIT OUT ANY PERSONAL INFORMATION BEFOREHAND**.

## A guide to the app

My UI design isn't exactly top-tier, but I tried to keep the interface as simple as possible and easy to navigate. Along the top is the infobar, which shouldn't be used unless there is an error, or you are testing the interface. Below it is the canvas, where your radar pictures will be displayed when a problem is started. Clicking on the canvas will draw a braa line. Click once for the origin and once for the destination. Along the bottom is the answer bar, it is where you will give your answers to a problem. Moving to the top right, we have our settings box. It contains the problem types that you want to enable, followed by the text to speech words per minute setting. Lastly is the problem management page, placed just below the settings box. It has the problem management buttons (submit your answers, redraw the page, and be given a new problem) and will give you corrections on your answers. You can hover over each correction for more detail and an example.

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

Given that I'm a single developer, the roadmap is subject to change depending on the weather, the phase of the moon, and whatever I feel like coding. It will give you a general idea of where the app will be heading and in what order though.  

- Polish UI and stuff
- More calls
- Dynamic missions? Idk I guess
