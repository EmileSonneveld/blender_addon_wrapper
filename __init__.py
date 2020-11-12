bl_info = {
	"name": "wrapper",
	"description": "wrapper",
	"author": "Emile Sonneveld",
	"version": (1, 0),
	"blender": (2, 82, 0),
	"location": "View3D > Add > Mesh",
	"warning": "development",
	"wiki_url": "",
	"tracker_url": "",
	"category": "wrapper"}

import os
import sys
import importlib

currentFolderName = __file__.replace("\\", "/").split("/")[-2]


def runningInBlender():
	# print("sys.executable", sys.executable)
	# print("sys.argv", sys.argv)

	# Ways this script can be running:

	# - Paste "C:/Program Files/Blender Foundation/Blender/blender-app.exe" in windows cmd
	# sys.executable C:\Program Files\Blender Foundation\Blender\blender-app.exe
	# sys.argv ['C:/Program Files/Blender Foundation/Blender/blender-app.exe']

	# - launch from windows taskbar:
	# sys.executable C:\Program Files\Blender Foundation\Blender\blender-app.exe
	# sys.argv ['C:\\Program Files\\Blender Foundation\\Blender\\blender-app.exe']

	# - When loaded from Blender commandline with --python
	# sys.executable C:\Program Files\Blender Foundation\Blender\blender-app.exe
	# sys.argv ['C:/Program Files/Blender Foundation/Blender/blender-app.exe', '--background', '--python', 'C:\\Users\\EmileSonneveld\\AppData\\Roaming\\Blender Foundation\\Blender\\2.73\\scripts\\addons\\TDS_Blender_general\\utils\\headless_boolean.py', '--', 'some-arguments-here']

	# - When .blend file is directly opened from commandline
	# sys.executable C:\Program Files\Blender Foundation\Blender\blender-app.exe
	# sys.argv ['blender-app.exe', 'C:\\cranioauto\\CranioAuto_Python\\configured_empty_scene.blend']

	# - When loaded as package. python -m CranioAuto_Blender_addon #cranio_tests
	# sys.executable C:\Users\EmileSonneveld\AppData\Local\Programs\Python\Python36\python.exe
	# sys.argv ['-m', '#cranio_tests']

	# - When a sub file is imported by a wild python script. from CranioAuto_Python.CranioAuto_Blender_addon.utils.python_utils import *
	# sys.executable  C:\Users\EmileSonneveld\AppData\Local\Programs\Python\Python36\python.exe
	# sys.argv  ['Copy_dlls.py']

	# Linux: type "blender" in the terminal:
	# sys.executable /usr/local/lib/blender2.73/blender
	# sys.argv ['blender']

	# Linux: Pasting "/usr/bin/blender" in the terminal:
	# sys.executable /usr/local/lib/blender2.73/blender
	# sys.argv ['/usr/bin/blender']

	ex = sys.executable.lower().replace("\\", "/")
	if ex.endswith("/blender.exe") or ex.endswith("/blender-app.exe"):
		return True
	if ex.endswith("/python.exe"):
		return False

	if ex.endswith("/blender") or ex.endswith("/blender-app"): # Linux
		return True
	if ex.endswith("/python"): # Linux
		return False

	if not os.path.exists(sys.executable):
		print("sys.executable does not exist: " + sys.executable)
		return False

	return False


classes = []
all_registers = []
all_unregister = []

# Only automaticaly import everything when in Blender
if not runningInBlender():
	print("Package not running as Blender addon: " + currentFolderName)
	if(sys.argv[0] == "-m"):
		# running as module. Allow to run file in this module
		if len(sys.argv) > 1:
			module_name = currentFolderName + '.' + sys.argv[1]
			sys.argv = sys.argv[1:]
			print("New args: ", sys.argv)
			importlib.import_module(module_name)
else:
	if 'bpy' in locals():
		print('Reloading addon: ' + currentFolderName)
	else:
		print('Importing addon: ' + currentFolderName)


	def getClassesInModule(mod):
		import inspect
		lst = []
		clsmembers = inspect.getmembers(mod, inspect.isclass)
		for name, obj in clsmembers:
			if obj.__module__ == mod.__name__:
				# print("mod.__name__: " + mod.__name__ + "  __module__: " + obj.__module__)
				lst.append(obj)
		return lst


	for file_name in os.listdir(os.path.dirname(__file__)):
		if file_name == '__init__.py' or \
				file_name[-3:] != '.py' or \
				file_name[0] == '.' or \
				file_name[0] == '#':
			continue
		# import/reload all .py files dynamically
		module_name = currentFolderName + '.' + file_name[:-3]
		# print("module_name: " + module_name)
		imported = importlib.import_module(module_name)
		if 'bpy' in locals():
			# note that old modules don't get unloaded!
			imported = importlib.reload(imported)

		classes += getClassesInModule(imported)

		if callable(getattr(imported, "register", None)):
			all_registers.append(imported.register)
		if callable(getattr(imported, "unregister", None)):
			all_unregister.append(imported.unregister)

	import bpy  # will change the return value of 'bpy' in locals()


def register():
	# bpy.utils.register_module(currentFolderName, verbose=True) # removed in Blender 2.80
	for cls in classes:
		try:
			bpy.utils.register_class(cls)
		except Exception as e:
			# example: RuntimeError: Error: Registering operator class: 'OBJECT_OT_my_cool_operator', invalid bl_idname 'my_cool_operator', must contain 1 '.' character
			import traceback
			# this allows half of the plugin to keep on working
			print("Dirty exception when calling the register function!")
			traceback.print_tb(e.__traceback__)
	for func in all_registers:
		try:
			func()
		except Exception as e:
			import traceback
			# this allows half of the plugin to keep on working
			print("Dirty exception when calling the register function!")
			traceback.print_tb(e.__traceback__)


def unregister():
	for func in reversed(all_unregister):
		try:
			func()
		except Exception as e:
			import traceback
			print("Dirty exception when calling the unregister function!")
			traceback.print_tb(e.__traceback__)
	# bpy.utils.unregister_module(__name__) # removed in Blender 2.80
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == '__main__':
	register()
