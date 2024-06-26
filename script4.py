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

    #Recuperation des images segmentés :

    repertoire_sujet_seg = r'/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor'
    nom_mask_sujet = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-brainmask_T2w.nii.gz'
    pattern = re.compile(nom_general_sujet)
    path_sujet_segment= [os.path.join(root, s)
                  for root, _, files in os.walk(all_sujets_path)
                  for s in files if pattern.match(s) and root == all_sujets_path]
    pattern_mask = re.compile(nom_mask_sujet)
    list_path_sujet_mask= [os.path.join(root, s)
                  for root, _, files in os.walk(all_sujets_path)
                  for s in files if pattern_mask.match(s)]
    list_path_img_segmente_rot = creation_PATH_pour_fichier_swaper(path_sujet_segment)
    swap_each_SUB(path_sujet_segment, list_path_img_segmente_rot)
    list_repertoire_segm_bin, list_image_sub_segm_bin =path_abs_sujet_to_fichier_repertorie_sujet(list_path_img_segmente_rot )

    for path_sujet_segm_rot, path_image_sub_binaryse, sujet, repertoire, mask_path in zip(list_path_img_segmente_rot, list_path_threshold,list_image_sub_segm_bin, list_repertoire_segm_bin,list_path_sujet_mask):
        Masque_sujet = ants.image_read(mask_path)
        Img_sujet_segmente = ants.image_read(path_sujet_segm_rot)
        Img_sujet_binarise = ants.image_read(path_image_sub_binaryse)
        Img_sujet_binarise_recal = Recalage_atlas(Img_sujet_segmente, Img_sujet_binarise,"Rigid", Masque_sujet)
        Img_sujet_segmente_array = Img_sujet_segmente.numpy()
        Img_sujet_segm_binar_combined_array = Img_sujet_segmente_array.copy()
        Img_sujet_binarise_recal_array = Img_sujet_binarise_recal.numpy()
        Img_sujet_segm_binar_combined_array = Img_sujet_segmente_array*Img_sujet_binarise_recal_array
        Img_sujet_segm_binar_combined = ants.from_numpy(Img_sujet_segm_binar_combined_array, origin=Img_sujet_segmente.origin, spacing=Img_sujet_segmente.spacing, direction=Img_sujet_segmente.direction)
        path_img_final = creation_chemin_nom_img_threshold(repertoire, sujet, "segmentation_LR")
        ants.image_write(Img_sujet_segm_binar_combined, path_img_final)