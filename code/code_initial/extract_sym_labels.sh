#!/bin/bash

path_in="/Users/letroter.a/Desktop/projects_teams/INT/MecA/MarsFet/Fetal_atlas_gholipour/T2"

path_out="./"


mkdir tmp_L
mkdir tmp_R

all_reg_L=""
all_reg_R=""

labels_R=(0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 36 38 40 42 44 46 48 50 52 54 56 58 60 62 64 66 68 70 72 74 76 78 80 82 84 86 88 90 93 97 99 101 103 105 107 109 113 115 117 119 121 123)

labels_L=(0 1 3 5 7 9 11 13 15 17 19 21 23 25 27 29 31 33 35 37 39 41 43 45 47 49 51 53 55 57 59 61 63 65 67 69 71 73 75 77 79 81 83 85 87 89 92 96 98 100 102 104 106 108 112 114 116 118 120 122) 

labels_LR=(91 110 111 124 125 199)

# bug fix for MIDBRAIN L (94) and R (95) not separated -> LR (removed from list 94 & 95)

for x in {21..38}
	do
	echo $x
	
	printf -v name "%02g" $x ;

	#atlas_regional="${path_in}/STA${name}_regional.nii.gz"
	atlas_tissu="${path_in}//STA${name}_tissue.nii.gz"

	for i in {0..59}
		do
		echo ${labels_R[i]} ${labels_L[i]}
		
		fslmaths $atlas_tissu -thr ${labels_R[i]} -uthr ${labels_R[i]} -bin tmp_R/label_R_${labels_R[i]}.nii.gz ;
		#fslmaths $atlas_regional -thr ${labels_R[i]} -uthr ${labels_R[i]} -bin tmp_R/label_R_${labels_R[i]}.nii.gz ;

		fslmaths $atlas_tissu -thr ${labels_L[i]} -uthr ${labels_L[i]} -bin tmp_L/label_L_${labels_L[i]}.nii.gz ;
		#fslmaths $atlas_regional -thr ${labels_L[i]} -uthr ${labels_L[i]} -bin tmp_L/label_L_${labels_L[i]}.nii.gz ;

		all_reg_R=${all_reg_R}"tmp_R/label_R_${labels_R[i]}.nii.gz -add "
		all_reg_L=${all_reg_L}"tmp_L/label_L_${labels_L[i]}.nii.gz -add "

		done

	echo ./STA${name}_all_reg_R.nii.gz  ./STA${name}_all_reg_L.nii.gz 
	fslmaths $all_reg_R tmp_R/label_R_0.nii.gz -thr 1 -bin ./STA${name}_all_reg_R.nii.gz 
	fslmaths $all_reg_L tmp_L/label_L_0.nii.gz -thr 1 -bin ./STA${name}_all_reg_L.nii.gz 

	fslmaths ./STA${name}_all_reg_R.nii.gz  -dilM -dilM -dilM -ero -ero -ero ./STA${name}_brainmask_R.nii.gz 
	fslmaths ./STA${name}_all_reg_L.nii.gz  -dilM -dilM -dilM -ero -ero -ero ./STA${name}_brainmask_L.nii.gz 

	fslmaths ./STA${name}_all_reg_L.nii.gz  -ero -ero -dilM -dilM -dilM -dilM -dilM -ero -ero -ero ./STA${name}_all_reg_L.nii.gz 
	fslmaths ./STA${name}_all_reg_R.nii.gz  -ero -ero -dilM -dilM -dilM -dilM -dilM -ero -ero -ero ./STA${name}_all_reg_R.nii.gz 

	fslmaths ./STA${name}_all_reg_L.nii.gz -mul 2 -add ./STA${name}_all_reg_R.nii.gz ./STA${name}_all_reg_LR.nii.gz -odt short
	fslmaths ./STA${name}_all_reg_LR.nii.gz -dilM -dilM -dilM -dilM ./STA${name}_all_reg_LR_dilM.nii.gz -odt short

	fslmaths ./STA${name}_all_reg_LR.nii.gz -dilM -dilM -dilM -dilM ./STA${name}_all_reg_LR_dilM.nii.gz -odt short

	done



	

#if [ $(( $i  % 2)) -eq 0 ]; then 
#echo "even" ; 
#else
#	for k in {0..6}
#		do
#		echo $k ${labels_LR[k]}
#		if [ $i != 91 ] & [ $i != 111 ]; then
#		echo "odd" ;
#		all_reg_R=${all_reg_R}"tmp_R/label_reg_${i}.nii.gz -add "
#		#fslmaths $atlas_tissu -thr ${i} -uthr ${i} -bin tmp_R/label_reg_${i}.nii.gz ;
#		fi
#		done
#fi



