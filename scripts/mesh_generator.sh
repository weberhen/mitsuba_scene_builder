#!/bin/bash

if [ "$1" == "" ]; then
	echo "$1"
    echo "Usage: sh mesh_generator.sh <input PLY file name> <output PLY file name>"
else
  	meshlabserver -i $1 -o $2 -s scripts/mesher_script.mlx -om vc vn fc fn
fi