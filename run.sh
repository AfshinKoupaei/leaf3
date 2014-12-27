#!/bin/bash


blender="/usr/share/blender/blender"
base_mesh_name="$1.blend"

here=$(pwd)
base="$here/base_mesh/$base_mesh_name"
export_base="$here/export_base.py"
leaf_generate="$here/leaf_generate.py"
leaf="$here/leaf.py"
leaf_mesh="$here/leaf_mesh.py"



res_folder="$here/res/"

if [ ! -d "$res_folder" ]; then
  mkdir $res_folder
fi

"$blender" "$base" -b -P "$export_base"

"$leaf_generate"

"$blender" -b -P "$leaf_mesh"


#export BLENDER_USER_SCRIPTS="$here/modules/"

