import subprocess
from os.path import exists
from sys import executable, platform
from time import sleep


print('Verifying installation (checking if files exist)')
files = ('main.py', 'scripts/__init__.py', 'scripts/GCI_structures.py', 'scripts/tk_objects.py', 'scripts/tts_sr.py',
		 'resources/callsigns.txt', 'resources/config.toml', 'resources/lang_model/0889.dic', 'resources/lang_model/0889.lm',
		 'resources/lang_model/0889.log_pronounce', 'resources/lang_model/0889.sent', 'resources/lang_model/0889.vocab')
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
	if cout.returncode != 0:
		print('Something went wrong trying to get python\'s version. Please check your python install.')
		sleep(10)
		raise Exception()
	v_nums = str(cout.stdout).split('.')
	if v_nums[0][-1] != '3' or int(v_nums[1]) < 11:
		print('Python should be version 3.11.x or later')
		sleep(10)
		raise AssertionError()
except KeyError:
	print('Something went wrong... \nKeyerror version checker')
	sleep(10)
	raise KeyError('Error checking python verison')
print('Done!', end='\n\n')

print('Installing packages, please be patient')
i = 0
for library in ['pocketsphinx', 'pyaudio', 'pyttsx3']:
	print(f'{i}/3 -> {library}')
	if (out := subprocess.run([executable, '-m', 'pip', 'install', library], capture_output=True)).returncode != 0:
		if 'Building windows wheels for Python 3.11 requires Microsoft Visual Studio' in str(out.stderr):
			print(f'You need to install a C/C++ compiler, one is available with Visual Studio at https://visualstudio.microsoft.com/vs/')
			print(f'args: {out.args} \nout: {out.stdout} \nerror: {out.stderr}')
			sleep(10)
			raise ModuleNotFoundError(out)
		else:
			print(f'Something went wrong installing a module')
			print(f'args: {out.args} \nout: {out.stdout} \nerror: {out.stderr}')
			sleep(10)
		raise ModuleNotFoundError(out)
	i += 1
print('3/3 -> Done', end='\n\n')

print('All done! Closing in 3')
sleep(1)
print('2')
sleep(1)
print('1')
sleep(1)
