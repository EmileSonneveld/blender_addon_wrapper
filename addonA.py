bl_info = {
	"name": "addonA",
	"author": "Emile Sonneveld",
	"version": (1, 0),
	"blender": (2, 82, 0),
	"location": "View3D > Add > Mesh",
	"description": "addonA can also be imported as a separated addon",
	"warning": "development",
	"wiki_url": "",
	"category": "Add Mesh"}

import bpy

class OBJECT_PT_AddonA(bpy.types.Panel):
	bl_label = "__ addonA __"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'DEFAULT_CLOSED'}
	bl_category = "wrapper"

	def draw(self, context):
		scn = context.scene
		layout = self.layout
		
		box=layout.box()
		box.label(text="this is addonA")

def register():
	if "." not in __name__:  # only needed when used as standalone file
		# bpy.utils.register_module(__name__)
		bpy.utils.register_class(OBJECT_PT_AddonA)
def unregister():
	if "." not in __name__:  # only needed when used as standalone file
		# bpy.utils.unregister_module(__name__)
		bpy.utils.unregister_class(OBJECT_PT_AddonA)
