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
    path_ouput = ""
    Nom_caract = r'^STA\d+\.nii.gz'
    path_des_atlas = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2"

    tableau_bon_atlas_by_sujet= [['sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz', 'sub-0002_ses-0002_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz', 'sub-0009_ses-0012_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz', 'sub-0019_ses-0022_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz', 'sub-0081_ses-0093_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz'], ['STA25.nii.gz', 'STA23.nii.gz', 'STA30.nii.gz', 'STA28.nii.gz', 'STA24.nii.gz']]
    (tab_img_sujet), (List_atlas_finaux) = tableau_bon_atlas_by_sujet
    #On cherche à recaler l'atlas sur l'image (une inversion du recalage), nous utilisons cette fois l'atlas segmenté
    #NOM des ATLAS SEGMENTÉ
    nom_atlas_binary = 'r^STA\d+\_all_reg_LR_dilM.nii.gz'
    path_des_atlas_binary = r'/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas'
    les_atlas_binary = []
    SUB_rec_by_Atlas_PATH = []

    for atlas in List_atlas_finaux :
        nom, fin = (atlas[:-7], ".nii.gz") if atlas.endswith(".nii.gz") else os.path.splitext(atlas)
        numero_atlas = nom.split('STA')[1]
        print(numero_atlas)
        les_atlas_binary.append(f'STA{numero_atlas}_all_reg_LR_dilM.nii.gz')


    for sujet, repertoire, atlas in zip(tab_img_sujet, tab_repertoire, les_atlas_binary):
        Sujet_fixe = ants.image_read(os.path.join(repertoire, sujet))
        Atlas_binary = ants.image_read(os.path.join(path_des_atlas_binary, atlas))
        SUB_recal_atlas_segm = tls.Inv_Recalage_atlas(Atlas_binary,Sujet_fixe,  "SyN", None)
        path_sub_recale_by_atlas_binary = tls.creation_chemin_nom_img_rot_rec(repertoire, sujet, atlas)
        SUB_rec_by_Atlas_PATH.append(path_sub_recale_by_atlas_binary)
        tls.Enregistrer_img_ants_en_nifit(SUB_recal_atlas_segm, os.path.join(repertoire, sujet), path_sub_recale_by_atlas_binary)