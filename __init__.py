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


def isBlenderExecutablePath(p: str):
	if not p:
		return False
	if p == "blender-app.exe" or p == "blender":
		return True
	if not os.path.exists(p):
		print("File doesn't exist: " + p)
		return False
	p = p.replace("\\", "/")
	if p.endswith("blender.exe"): # Blender 2.82
		return True
	lastSlashIndex = p.rfind("/")
	lastBlenderIndex = p.rfind("Blender/blender") + len("Blender/blender")
	return lastSlashIndex < lastBlenderIndex


#print("sys.argv[0]: " + sys.argv[0])
# print(isBlenderExecutablePath("C:/Program Files/Blender Foundation/Blender/blender-app.exe"))
# print(isBlenderExecutablePath("blender-app.exe")) #When double clicking a .blend, or when launching a .blend from commandline (without specifying executable)
# print(isBlenderExecutablePath("")) # empty on commandline
# print(isBlenderExecutablePath("C:\\Users\\Emile\\AppData\\Roaming\\Blender Foundation\\Blender\\2.73\\scripts\\addons\\TDS_RandomPluginNameHere\\headless_background_scripts\\undercut.py"))
# C:\Program Files\Blender Foundation\Blender 2.82\blender.exe

classes = []
all_registers = []
all_unregister = []

# Only automaticaly import everything when in Blender
if not isBlenderExecutablePath(sys.argv[0]):
	print("Package not running as Blender addon: " + currentFolderName)
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
