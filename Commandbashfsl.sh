#!/bin/bash

image_input = $'/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2/STA21.nii.gz'
image_output = $'/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2/STA21_ROT.nii.gz'
fslswapdim  $image_input  -x y -z $image_output 
