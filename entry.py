if __name__ == '__main__':
	from multiprocessing import freeze_support
	freeze_support()
	from main import main_loop
	from time import sleep
	try:
		main_loop()
	except Exception as error:
		print(error)
		sleep(10)
