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
from script1 import List_atlas_finaux, tab_img_sujet, list_warp_inv

print(List_atlas_finaux)
def etape2():
    debut = time.time()

    nom_general_sujet = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz'
    nom_general_sujet_rot = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz'
    all_sujets_path = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/"
    path_repertoire_sujet_rot = "/envau/work/meca/users/2024_Kamal/output/output_script1"
    path_output_repertoire = "/envau/work/meca/users/2024_Kamal/output/output_script2"
    Nom_caract = r'^STA\d+\.nii.gz'
    path_des_atlas = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2"


    #On cherche à recaler l'atlas sur l'image (une inversion du recalage), nous utilisons cette fois l'atlas binar
    #NOM des ATLAS Binairs
    nom_atlas_binary = 'r^STA\d+\_all_reg_LR_dilM.nii.gz'
    path_des_atlas_binary = r'/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas'
    les_atlas_binary = []
    SUB_rec_by_Atlas_PATH = []

    for atlas in List_atlas_finaux:
        nom, fin = (atlas[:-7], ".nii.gz") if atlas.endswith(".nii.gz") else os.path.splitext(atlas)
        numero_atlas = nom.split('STA')[1]
        print(numero_atlas)
        les_atlas_binary.append(f'STA{numero_atlas}_all_reg_LR_dilM')


    for sujet, atlas_binar, inv_warp in zip(tab_img_sujet, les_atlas_binary, list_warp_inv):
        Sujet_fixe = ants.image_read(os.path.join(path_output_repertoire, sujet))
        Atlas_binary = ants.image_read(os.path.join(path_des_atlas_binary, atlas))
        Atlas_binary_warped = ants.apply_transforms(Sujet_fixe, Atlas_binary, transformlist=inv_warp, interpolator= "nearestNeighbor")
        path_atlas_binary_warped = tls.creation_chemin_nom_img(path_output_repertoire, sujet, atlas_binar)
        SUB_rec_by_Atlas_PATH.append(path_atlas_binary_warped)
        ants.image_write(Atlas_binary_warped, path_atlas_binary_warped)
    fin = time.time()
    tps_excecution = fin - debut
    print(f"le temps d'exécution du programme est : {tps_excecution} secondes")

if __name__ == "__main__":
    etape2()