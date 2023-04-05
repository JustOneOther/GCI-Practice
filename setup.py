import subprocess
from os.path import exists
from sys import executable, platform
from time import sleep


print('Verifying installation (checking if files exist)')
files = ('main.py', 'Scripts/__init__.py', 'Scripts/GCI_structures.py', 'Scripts/tk_objects.py', 'Scripts/tts_sr.py',
		 'Resources/callsigns.txt', 'Resources/config.toml', 'Resources/lang_model/0889.dic', 'Resources/lang_model/0889.lm',
		 'Resources/lang_model/0889.log_pronounce', 'Resources/lang_model/0889.sent', 'Resources/lang_model/0889.vocab')
for file in files:
	sleep(0.2)		# Slow down for user and make it feel like the computer's acutally doing something
	is_there = exists(file)
	if is_there:
		print(f'{file} : True')
	else:
		print(f'{file}: False')
		print('Please ensure all files are installed correctly')
		sleep(10)
		raise FileNotFoundError(f'{file} does not exist')
print('Done!', end='\n\n')

print('Checking platform and python version')
sleep(0.5)
if platform == 'darwin':
	print('setup.py does not work on macos, please install the requirements in requirements.txt manually.')
	sleep(10)
	raise OSError('Bad OS type')
try:
	cout = subprocess.run([executable, '-V'], capture_output=True)
	assert cout.returncode == 0, "Something went wrong trying to get python's version. Please check your python install."
	v_nums = str(cout.stdout).split('.')
	assert v_nums[0][-1] == '3' and int(v_nums[1]) >= 11, "Python should be version 3.11.x"
except KeyError:
	print('problem')
print('Done!', end='\n\n')

print('Installing packages, please be patient')
print('0/3 -> pocketsphinx')
if (out := subprocess.run([executable, '-m', 'pip', 'install', 'pocketsphinx'], capture_output=True)).returncode != 0:
	print(f'Something went wrong installing a module \nargs: {out.args}')
	sleep(10)
	raise ModuleNotFoundError(out)
print('1/3 -> pyaudio')
if (out := subprocess.run([executable, '-m', 'pip', 'install', 'pyaudio'], capture_output=True)).returncode != 0:
	print(f'Something went wrong installing a module \nargs: {out.args}')
	sleep(10)
	raise ModuleNotFoundError(out)
print('2/3 -> pyttsx3')
if (out := subprocess.run([executable, '-m', 'pip', 'install', 'pyttsx3'], capture_output=True)).returncode != 0:
	print(f'Something went wrong installing a module \nargs: {out.args}')
	sleep(10)
	raise ModuleNotFoundError(out)
print('3/3 -> Done', end='\n\n')

print('All done! Closing in 3')
sleep(1)
print('2')
sleep(1)
print('1')
sleep(1)
