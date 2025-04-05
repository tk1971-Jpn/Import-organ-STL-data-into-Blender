### This script is designed to batch import STL files of organs created using the Auto Segmentator in 3D Slicer into Blender. 

(You need to enable the `Import-Export STL files` add-on in Blender. Open Blender Preferences, go to Get-Extensions, install it, and enable the add-on. After installation, it will appear as **STL format (legacy)** in the Add-ons section.)

<img width="612" alt="import STL" src="https://github.com/user-attachments/assets/dddbcbf0-cb61-4f53-ad69-a31862f54a1f" />

**Note:** Since the object sizes are too large and exceed Blender's workspace limits, they are scaled down to 1/50th upon import.

In the script, specify the directory where the STL data is stored in the `folder_path` variable. Adjust the values of `x_move`, `y_move`, and `z_move` in the script to modify the import position.

**Note:**  When using a Windows PC, a SyntaxError (unicode error) related to the path can be resolved by adding `r` at the beginning of the path.  
`NG` path = "C:\Users\myname\Documents\file.txt"  
`OK` path = r"C:\Users\myname\Documents\file.txt" 

**Note:** In 3D Slicer, surface data may sometimes be extracted as a mirrored object. In such cases, please use the script for mirrored objects.

**option:** To reduce the file size, copy and paste `Remesh` file into Blender's script mode and remesh all objects at once. (The default voxel size is 3.)

**option:** You can automatically sort objects (organs) into collections by executing 'Collection sort'."
