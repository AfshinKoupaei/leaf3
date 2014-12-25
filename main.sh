#!/bin/bash


blender="/usr/share/blender/blender"
base_mesh_name="grid.blend"

here=$(pwd)
base="$here/base_mesh/$base_mesh_name"
export_base="$here/export_base.py"
build_mesh="$here/leaf.py"
leaf="$here/leaf.py"
leaf_skin="$here/leaf_skin.py"



res_folder="$here/res/"

if [ ! -d "$res_folder" ]; then
  mkdir $res_folder
fi

"$blender" "$base" -b -P "$export_base"

"$leaf"

"$blender" -b -P "$leaf_skin"






#export BLENDER_USER_SCRIPTS="$here/modules/"
