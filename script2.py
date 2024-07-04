import os
import re
import time
import numpy as np
import pandas as pd
import nibabel as nib
import ants
import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('Qt5Agg')
import tools as tls


def etape2(path_des_atlas_binary, list_atlas_finaux,tab_img_sujet_rot,list_tranf_inv,path_repertoire_sujet_rot,path_output_repertoire ):
    debut = time.time()
    #On cherche à recaler l'atlas sur l'image (une inversion du recalage), nous utilisons cette fois l'atlas binar
    #NOM des ATLAS Binairs

    les_atlas_binary = []
    for atlas in list_atlas_finaux:
        nom, fin = (atlas[:-7], ".nii.gz") if atlas.endswith(".nii.gz") else os.path.splitext(atlas)
        numero_atlas = nom.split('STA')[1]
        print(numero_atlas)
        les_atlas_binary.append(f'STA{numero_atlas}_all_reg_LR_dilM{fin}')

    # for sujet, atlas_binar in zip(tab_img_sujet_rot, les_atlas_binary):
    #     print(atlas_binar )
    #     atlas_binary_redim = tls.copy_info_geo(os.path.join(path_des_atlas_binary, atlas_binar), os.path.join(path_repertoire_sujet_rot, sujet))
    #     print(f"les dimension de Atlas_binary est : {np.shape(atlas_binary_redim )}")
    #     path_atlas_binary_redim = os.path.join(path_output_repertoire, atlas_binar)
    #     nib.save(atlas_binary_redim, path_atlas_binary_redim)

    SUB_rec_by_Atlas_PATH = []
    for sujet, atlas_binar, warp in zip(tab_img_sujet_rot, les_atlas_binary, list_tranf_inv):
        Sujet_fixe = ants.image_read(os.path.join(path_repertoire_sujet_rot, sujet))
        Atlas_binary = ants.image_read(os.path.join(path_des_atlas_binary, atlas_binar))
        print(f"les dimension de Sujet_fixe est : {np.shape(Sujet_fixe)}")
        print(f"les dimension de Atlas_binary est : {np.shape(Atlas_binary )}")
        transfo =warp + "_Inverse_0GenericAffine.mat"
        Atlas_binary_warped = ants.apply_transforms(Sujet_fixe, Atlas_binary, transformlist=transfo, interpolator="nearestNeighbor")
        print(f"les dimension de Atlas_binary_warped est : {np.shape(Atlas_binary_warped)}")
        path_atlas_binary_warped = tls.creation_chemin_nom_img(path_output_repertoire, sujet, atlas_binar)
        SUB_rec_by_Atlas_PATH.append(path_atlas_binary_warped)
        nib.save(Atlas_binary_warped, path_atlas_binary_warped)
    fin = time.time()
    tps_excecution = fin - debut
    print(f"le temps d'exécution du programme est : {tps_excecution} secondes")
    return SUB_rec_by_Atlas_PATH


if __name__ == "__main__":
    path_des_atlas_binary = r'/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas'
    path_variables = "/envau/work/meca/users/2024_Kamal/2024_stage_Kamal/variables"
    path_repertoire_sujet_rot = "/envau/work/meca/users/2024_Kamal/output/output_script1"
    path_output_repertoire = "/envau/work/meca/users/2024_Kamal/output/output_script2"
    list_atlas_finaux = np.load(os.path.join(path_variables, "list_atlas_finaux.npy"))
    tab_img_sujet_rot = np.load(os.path.join(path_variables, "tab_img_sujet_rot.npy"))
    list_tranf_direc =  np.load(os.path.join(path_variables, "list_tranf_direc.npy"))
    list_tranf_inv = np.load(os.path.join(path_variables, "list_tranf_inv.npy"))
    # transfo_test = ants.read_transform(list_tranf_direc[0]+"0GenericAffine.mat")
    # trasnfo_test_mat = np.reshape(transfo_test.parameters, (4,3))
    # transfo_test_inv = ants.read_transform(list_tranf_inv[0]+"0GenericAffine.mat")
    # trasnfo_test_inv_mat = np.reshape(transfo_test_inv.parameters, (4,3))
    # inv_trasnfo_test_mat = np.reshape(transfo_test.invert().parameters, (4,3))
    # print(trasnfo_test_inv_mat-trasnfo_test_mat)
    # print(trasnfo_test_inv_mat-inv_trasnfo_test_mat)
    #print(trasnfo_test_inv_mat-np.linalg.inv(trasnfo_test_mat))
    print(list_tranf_inv)

    SUB_rec_by_Atlas_PATH = etape2(path_des_atlas_binary, list_atlas_finaux, tab_img_sujet_rot, list_tranf_inv, path_repertoire_sujet_rot, path_output_repertoire)
    print(SUB_rec_by_Atlas_PATH)
    np.save(os.path.join(path_variables, "SUB_rec_by_Atlas_PATH.npy"), SUB_rec_by_Atlas_PATH, allow_pickle='False')