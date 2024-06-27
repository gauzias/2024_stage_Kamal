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

SUB_rec_by_Atlas_PATH = []



def etape2():
    global SUB_rec_by_Atlas_PATH
    debut = time.time()
    print(List_atlas_finaux)
    path_repertoire_sujet_rot = "/envau/work/meca/users/2024_Kamal/output/output_script1"
    path_output_repertoire = "/envau/work/meca/users/2024_Kamal/output/output_script2"
    #On cherche à recaler l'atlas sur l'image (une inversion du recalage), nous utilisons cette fois l'atlas binar
    #NOM des ATLAS Binairs
    path_des_atlas_binary = r'/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas'
    les_atlas_binary = []
    for atlas in List_atlas_finaux:
        nom, fin = (atlas[:-7], ".nii.gz") if atlas.endswith(".nii.gz") else os.path.splitext(atlas)
        numero_atlas = nom.split('STA')[1]
        print(numero_atlas)
        les_atlas_binary.append(f'STA{numero_atlas}_all_reg_LR_dilM{fin}')


    for sujet, atlas_binar, warp in zip(tab_img_sujet, les_atlas_binary, list_warp_inv):
        Sujet_fixe = ants.image_read(os.path.join(path_repertoire_sujet_rot, sujet))
        Atlas_binary = ants.image_read(os.path.join(path_des_atlas_binary, atlas_binar))
        Atlas_binary_warped = ants.apply_transforms(Sujet_fixe, Atlas_binary,  transformlist=warp['invtransforms'], interpolator= "nearestNeighbor")
        path_atlas_binary_warped = tls.creation_chemin_nom_img(path_output_repertoire, sujet, atlas_binar)
        SUB_rec_by_Atlas_PATH.append(path_atlas_binary_warped)
        ants.image_write(Atlas_binary_warped, path_atlas_binary_warped)
    fin = time.time()
    tps_excecution = fin - debut
    print(f"le temps d'exécution du programme est : {tps_excecution} secondes")
    return SUB_rec_by_Atlas_PATH
# if __name__ == "__main__":
etape2()