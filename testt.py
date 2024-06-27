import os
import re
import time
import numpy as np
import pandas as pd
import nibabel as nib
import ants
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
import tools as tls
path_atlas = '/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2'
path = '/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/STA22_all_reg_LR_dilM.nii.gz'
sujet_repertoire = '/envau/work/meca/users/2024_Kamal/output/output_script1/'
sujet_segm = '/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz'
atlas_binaire = ants.image_read(path)
ligne_atlas = ['STA22.nii.gz']
atlas = ants.image_read('/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2/STA22.nii.gz')
criteres = ['MattesMutualInformation']
path_sujet = '/envau/work/meca/users/2024_Kamal/output/output_script1/sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz'
sujet = ants.image_read(path_sujet)
sujet_segm = ants.image_read(sujet_segm)
tab2D_global, Bon_atlas, warp = tls.recupAtlas_to_tableau_simil(ligne_atlas, criteres, path_atlas, 'sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz' , '/envau/work/meca/users/2024_Kamal/output/output_script1/', "Rigid", "linear")
#print(warp_inv,warp_inv['invtransforms'])
Atlas_binary_warped = ants.apply_transforms(sujet, atlas_binaire,  transformlist=warp['invtransforms'], interpolator= "nearestNeighbor")
path_atlas_binary_warped = tls.creation_chemin_nom_img( '/envau/work/meca/users/2024_Kamal/output/output_script2', 'sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot', 'STA22_all_reg_LR_dilM.nii.gz')
ants.image_write(Atlas_binary_warped, path_atlas_binary_warped)