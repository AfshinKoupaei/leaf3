#!/bin/bash

set -e

blender="/usr/share/blender/blender"

base_mesh_name="$1"
base="$here/$base_mesh_name"

here=$(pwd)
export_base="$here/export.py"
generate="$here/generate.py"
generate="$here/generate.py"
mesh="$here/mesh.py"

res_folder="$here/res/"


if [ ! -d "$res_folder" ]; then
  mkdir $res_folder
fi

case "$base_mesh_name" in
  
  "") 

    "$blender" -b -P "$export_base"
  ;;

  *)

    if [ ! -f "$base" ]; then
      echo "no such file: $base";
      exit 1;
    fi

    "$blender" "$base" -b -P "$export_base"
  ;;

esac


"$generate"

"$blender" -b -P "$mesh"

