from time import sleep
from threading import Thread


def try_several_times(func, *args, **kwargs):
	err = None
	for i in range(0, 3):
		try:
			result = func(*args, **kwargs)
			return result
		except Exception as ex:
			err = ex
	Exception(err)
#end define

def print_table(arr):
	buff = dict()
	for i in range(len(arr[0])):
		buff[i] = list()
		for item in arr:
			buff[i].append(len(str(item[i])))
	for item in arr:
		for i in range(len(arr[0])):
			index = max(buff[i]) + 2
			text = str(item[i]).ljust(index)
			if item == arr[0]:
				text = bcolors.blue + bcolors.bold + text + bcolors.endc
			print(text, end='')
		print()
#end define

def try_function(func, *args, **kwargs):
	result = None
	try:
		result = func(*args, **kwargs)
	except Exception as err:
		print(f"{func.__name__} error: {err}")
	return result
#end define

def start_thread(func, *args, **kwargs):
	name = kwargs.pop("name", func.__name__)
	Thread(target=func, name=name, args=args, kwargs=kwargs, daemon=True).start()
	print(f"Thread {name} started")
#end define

def cycle(func, *args, **kwargs):
	sec = kwargs.pop("sec")
	while True:
		try_function(func, *args, **kwargs)
		sleep(sec)
#end define

def start_cycle(func, *args, **kwargs):
	name = kwargs.pop("name", func.__name__)
	start_thread(cycle, func, *args, **kwargs, name=name)
#end define

class bcolors:
	'''This class is designed to display text in color format'''
	red = "\033[31m"
	green = "\033[32m"
	yellow = "\033[33m"
	blue = "\033[34m"
	magenta = "\033[35m"
	cyan = "\033[36m"
	endc = "\033[0m"
	bold = "\033[1m"
	underline = "\033[4m"
	default = "\033[39m"
#end class

class Dict(dict):
	def __init__(self, *args, **kwargs):
		for item in args:
			self._parse_dict(item)
		self._parse_dict(kwargs)
	#end define

	def _parse_dict(self, d):
		for key, value in d.items():
			if type(value) in [dict, Dict]:
				value = Dict(value)
			if type(value) == list:
				value = self._parse_list(value)
			self[key] = value
	#end define

	def _parse_list(self, lst):
		result = list()
		for value in lst:
			if type(value) in [dict, Dict]:
				value = Dict(value)
			result.append(value)
		return result
	#end define

	def __setattr__(self, key, value):
		self[key] = value
	#end define

	def __getattr__(self, key):
		return self.get(key)
	#end define
#end class
