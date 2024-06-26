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

if __name__ == "__main__":
    debut = time.time()

    nom_general_sujet = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz'
    nom_general_sujet_rot = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz'
    all_sujets_path = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/"
    Nom_caract = r'^STA\d+\.nii.gz'
    path_des_atlas = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2"

    list_repertoire, list_image_sub_recal =tls.path_abs_sujet_to_fichier_repertorie_sujet(SUB_rec_by_Atlas_PATH)

    list_path_threshold = []
    for image_sub_recal, repertoire in zip(list_image_sub_recal, list_repertoire):
        Image_recal_array = nib.load(os.path.join(repertoire, image_sub_recal)).get_fdata()
        Image_recal_array[Image_recal_array == 2] = 10
        Image_recal_array[Image_recal_array != 10] = 0
        path_image_threshold = tls.creation_chemin_nom_img_threshold(repertoire, image_sub_recal, "seg_L_only_x10")
        list_path_threshold.append(path_image_threshold)
        Image_recal_threshold = nib.Nifti1Image(Image_recal_array, affine=np.eye(4))
        nib.save(Image_recal_threshold, path_image_threshold)
