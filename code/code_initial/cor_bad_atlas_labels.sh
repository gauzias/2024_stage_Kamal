#!/bin/bash

path_in="/Users/letroter.a/Desktop/projects_teams/INT/MecA/MarsFet/Fetal_atlas_gholipour/T2"

name="38"

atlas_tissu_old="${path_in}//STA${name}_tissue_old.nii.gz"
atlas_tissu="${path_in}//STA${name}_tissue.nii.gz"

cp -rf $atlas_tissu $atlas_tissu_old 

#replace bad Left hemi WM labels (112) by Right hemi WM label (113)
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 48 149 88; 
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 44 147 91; 
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 45 147 91; 
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 45 147 92; 
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 48 147 92;  
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 49 147 93; 
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 43 146 92; 
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 46 146 92; 
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 47 145 92; 
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 48 146 92;  
ImageMath 3 $atlas_tissu SetOrGetPixel $atlas_tissu 113 48 148 92; 