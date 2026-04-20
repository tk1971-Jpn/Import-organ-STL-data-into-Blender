bl_info = {
    "name": "Medical STL Importer & Organizer",
    "author": "User & Gemini",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Slicer Tools",
    "description": "3D-Slicerで作成したSTLのインポート、自動分類、着色、Remeshを行います",
    "category": "Import-Export",
}

import bpy
import os

# --- データ定義 ---
COLLECTION_DICT = {
    "Bone": ["skull", "costal cartilage", "sternum", "left clavicle", "right clavicle", "left scapula", "right scapula",
             "left humerus", "right humerus", "C3 vertebra", "C4 vertebra", "C5 vertebra", "C6 vertebra", "C7 vertebra",
             "T1 vertebra", "T2 vertebra", "T3 vertebra", "T4 vertebra", "T5 vertebra", "T6 vertebra",
             "T7 vertebra", "T8 vertebra", "T9 vertebra", "T10 vertebra", "T11 vertebra", "T12 vertebra",
             "L1 vertebra", "L2 vertebra", "L3 vertebra", "L4 vertebra", "L5 vertebra", "S1 vertebra", "Sacrum",
             "left rib 1", "left rib 2", "left rib 3", "left rib 4", "left rib 5", "left rib 6",
             "left rib 7", "left rib 8", "left rib 9", "left rib 10", "left rib 11", "left rib 12",
             "right rib 1", "right rib 2", "right rib 3", "right rib 4", "right rib 5", "right rib 6",
             "right rib 7", "right rib 8", "right rib 9", "right rib 10", "right rib 11", "right rib 12",
             "left hip", "right hip", "left femur", "right femur", "spinal cord"],
    "Muscle": ["left iliopsoas muscle", "right iliopsoas muscle", "left deep back muscle", "right deep back muscle",
               "left gluteus maximus", "left gluteus medius", "left gluteus minimus",
               "right gluteus maximus", "right gluteus medius", "right gluteus minimus"],
    "Thoracic": ["trachea", "heart", "left atrial appendage", "pulmonary venous system", "thyroid",
                 "superior lobe of right lung", "inferior lobe of left lung", "inferior lobe of right lung", "middle lobe of right lung", "superior lobe of left lung"],
    "Abdominal": ["urinary bladder", "prostate", "colon", "duodenum", "esophagus", "gallbladder", "left adrenal gland", "left kidney", "liver",
                  "pancreas", "right adrenal gland", "right kidney", "small bowel", "spleen", "stomach"],
    "Vessel": ["aorta", "superior vena cava", "inferior vena cava",
               "left brachiocephalic vein", "right brachiocephalic vein", "left subclavian artery", "right subclavian artery", "brachiocephalic trunk",
               "left common iliac artery", "right common iliac artery",
               "left common carotid artery", "right common carotid artery",
               "left common iliac vein", "right common iliac vein", "portal vein and splenic vein"],
}

MATERIAL_COLORS = {
    "Bone": (0.509, 0.448, 0.391, 1.0),
    "Muscle": (0.458, 0.114, 0.100, 1.0),
    "Liver": (0.359, 0.052, 0.044, 1.0),
    "Stomach": (0.483, 0.277, 0.269, 1.0),
    "Artery": (0.675, 0.020, 0.042, 1.0),
    "Vein": (0.071, 0.014, 0.373, 1.0),
    "Kidney": (0.359, 0.084, 0.061, 1.0),
    "Adrenal": (0.800, 0.254, 0.030, 1.0),
    "Pancreas": (0.450, 0.260, 0.102, 1.0),
    "GB": (0.128, 0.163, 0.070, 1.0),
    "Heart": (0.675, 0.020, 0.042, 1.0),
    "Portal": (0.047, 0.046, 0.434, 1.0),
    "Lung": (0.475, 0.317, 0.299, 1.0),
    "Thyroid": (0.373, 0.246, 0.068, 1.0),
    "Bladder": (0.591, 0.383, 0.372, 1.0),
    "Spleen": (0.110, 0.022, 0.025, 1.0),
    "Prostate": (0.366, 0.160, 0.063, 1.0),
    "Colon": (0.403, 0.212, 0.104, 1.0),
}

# どのオブジェクトにどのマテリアルを塗るかの対応
OBJ_TO_MAT = {
    "heart": "Heart", "left atrial appendage": "Heart",
    "pulmonary venous system": "Vein", "superior vena cava": "Vein", "inferior vena cava": "Vein",
    "left brachiocephalic vein": "Vein", "right brachiocephalic vein": "Vein", "brachiocephalic trunk": "Vein",
    "left common iliac vein": "Vein", "right common iliac vein": "Vein", "portal vein and splenic vein": "Vein",
    "aorta": "Artery", "left subclavian artery": "Artery", "right subclavian artery": "Artery",
    "left common iliac artery": "Artery", "right common iliac artery": "Artery",
    "left common carotid artery": "Artery", "right common carotid artery": "Artery",
    "thyroid": "Thyroid", "urinary bladder": "Bladder", "prostate": "Prostate", "colon": "Colon",
    "duodenum": "Stomach", "esophagus": "Stomach", "small bowel": "Stomach", "stomach": "Stomach",
    "gallbladder": "GB", "left adrenal gland": "Adrenal", "right adrenal gland": "Adrenal",
    "left kidney": "Kidney", "right kidney": "Kidney", "liver": "Liver", "pancreas": "Pancreas",
    "spleen": "Spleen",
}

# --- ヘルパー関数 ---

def create_material(name, color):
    if name in bpy.data.materials:
        material = bpy.data.materials[name]
    else:
        material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs['Base Color'].default_value = color
    return material

# --- 実行オペレーター ---

class SLICER_OT_ImportOrganize(bpy.types.Operator):
    bl_idname = "slicer.import_organize"
    bl_label = "Import and Organize STL"
    
    def execute(self, context):
        props = context.scene.slicer_tool_props
        folder_path = bpy.path.abspath(props.stl_dir)
        
        if not os.path.isdir(folder_path):
            self.report({'ERROR'}, "フォルダが見つかりません")
            return {'CANCELLED'}

        # 1. コレクションの作成
        for col_name in COLLECTION_DICT.keys():
            if col_name not in bpy.data.collections:
                new_col = bpy.data.collections.new(col_name)
                context.scene.collection.children.link(new_col)

        # 2. ファイルのインポートと移動
        file_names = [f for f in os.listdir(folder_path) if f.endswith('.stl')]
        
        for filename in file_names:
            file_path = os.path.join(folder_path, filename)
            bpy.ops.wm.stl_import(filepath=file_path) # Blender 4.x以降の高速インポーター
            
            objs = context.selected_objects
            if not objs: continue
            obj = objs[0]

            # 名前変更
            full_name = os.path.splitext(filename)[0]
            new_name = full_name.split("segmentation_")[-1] if "segmentation_" in full_name else full_name
            obj.name = new_name
            
            # トランスフォーム
            obj.scale = (props.import_size, props.import_size, props.import_size)
            obj.rotation_euler[0] = -1.5708
            obj.location = (props.move_x, props.move_y, props.move_z)

            # 分類
            moved = False
            for col_name, obj_list in COLLECTION_DICT.items():
                if obj.name in obj_list:
                    dest_col = bpy.data.collections.get(col_name)
                    for col in obj.users_collection:
                        col.objects.unlink(obj)
                    dest_col.objects.link(obj)
                    moved = True
                    break
            
            if not moved:
                print(f"Object {obj.name} did not match any category.")

        return {'FINISHED'}

class SLICER_OT_ApplyMaterials(bpy.types.Operator):
    bl_idname = "slicer.apply_materials"
    bl_label = "Color Organs"

    def execute(self, context):
        # 全マテリアル作成
        for mat_name, color in MATERIAL_COLORS.items():
            create_material(mat_name, color)
        
        # 適用
        for obj in bpy.data.objects:
            # 1. 明示的なマッピングがある場合
            if obj.name in OBJ_TO_MAT:
                mat = bpy.data.materials.get(OBJ_TO_MAT[obj.name])
            # 2. 骨(Bone)や筋肉(Muscle)などリストに含まれる場合
            elif any(obj.name in v for k, v in COLLECTION_DICT.items() if k in ["Bone", "Muscle"]):
                col_name = "Bone" if any(obj.name in v for v in [COLLECTION_DICT["Bone"]]) else "Muscle"
                mat = bpy.data.materials.get(col_name)
            # 3. 肺(Lung)
            elif "lung" in obj.name:
                mat = bpy.data.materials.get("Lung")
            else:
                continue

            if mat:
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
        
        return {'FINISHED'}

class SLICER_OT_Remesh(bpy.types.Operator):
    bl_idname = "slicer.remesh"
    bl_label = "Remesh Selected"

    def execute(self, context):
        props = context.scene.slicer_tool_props
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        for obj in selected_objects:
            context.view_layer.objects.active = obj
            mod = obj.modifiers.new(name="Remesh", type='REMESH')
            mod.mode = 'VOXEL'
            mod.voxel_size = props.remesh_voxel_size
            
            bpy.ops.object.modifier_apply(modifier=mod.name)
            
        self.report({'INFO'}, f"{len(selected_objects)} 個のオブジェクトをRemeshしました")
        return {'FINISHED'}

# --- UI & プロパティ ---

class SlicerToolProperties(bpy.types.PropertyGroup):
    stl_dir: bpy.props.StringProperty(
        name="STL Directory",
        subtype='DIR_PATH',
        default="/Users/tkimura/Desktop/STL"
    )
    import_size: bpy.props.FloatProperty(name="Scale", default=0.02)
    move_x: bpy.props.FloatProperty(name="Move X", default=0.0)
    move_y: bpy.props.FloatProperty(name="Move Y", default=0.0)
    move_z: bpy.props.FloatProperty(name="Move Z", default=0.0)
    remesh_voxel_size: bpy.props.FloatProperty(name="Voxel Size", default=1.5, min=0.001)

class VIEW3D_PT_SlicerTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Slicer Tools'
    bl_label = "Medical Data Organizer"

    def draw(self, context):
        layout = self.layout
        props = context.scene.slicer_tool_props

        col = layout.column(align=True)
        col.label(text="1. Import & Setup")
        col.prop(props, "stl_dir", text="")
        col.prop(props, "import_size")
        col.operator("slicer.import_organize", icon='IMPORT')

        layout.separator()
        col = layout.column(align=True)
        col.label(text="2. Coloring")
        col.operator("slicer.apply_materials", icon='MATERIAL')

        layout.separator()
        col = layout.column(align=True)
        col.label(text="3. Remesh (Selected)")
        col.prop(props, "remesh_voxel_size")
        col.operator("slicer.remesh", icon='MOD_REMESH')

# --- 登録 ---

classes = (
    SlicerToolProperties,
    SLICER_OT_ImportOrganize,
    SLICER_OT_ApplyMaterials,
    SLICER_OT_Remesh,
    VIEW3D_PT_SlicerTools,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.slicer_tool_props = bpy.props.PointerProperty(type=SlicerToolProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.slicer_tool_props

if __name__ == "__main__":
    register()