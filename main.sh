#!/bin/bash

blender="/usr/share/blender/blender"
base_mesh_name="grid.blend"

here=$(pwd)
base="$here/base_mesh/$base_mesh_name"
export_base="$here/export_base.py"

leaf="$here/leaf.py"

res_folder="$here/res/"

if [ ! -d "$res_folder" ]; then
  mkdir $res_folder
fi

"$blender" "$base" -b -P "$export_base"

"$leaf"

