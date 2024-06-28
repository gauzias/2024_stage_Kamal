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
# from shared_module import list_path_threshold, tab_img_sujet


def etape4():
    debut = time.time()
    nom_general_sujet = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz'
    all_sujets_path = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/"
    path_output = "/envau/work/meca/users/2024_Kamal/output/output_script4"
    #Recuperation des images segmentés et on les swap :
    list_path_img_segmente = tls.recup_sujet(all_sujets_path, nom_general_sujet)
    list_path_img_segmente_rot = [tls.creation_PATH_pour_fichier_swaper(sujet_path, path_output) for sujet_path in list_path_img_segmente]
    for path_sujet_rot, path_sujet in zip(list_path_img_segmente_rot, list_path_img_segmente):
        tls.SWAP_COPY_INFO_SAVE(path_sujet, path_sujet_rot)

    # ON additionne apres passage en numpy array les tableau de l'image segmenté du sujet l'image de l'hemisphère droit*10
    for path_sujet_segm_rot, path_image_sub_binaryse, sujet in zip(list_path_img_segmente_rot, list_path_threshold, tab_img_sujet):
        Img_sujet_segmente = ants.image_read(path_sujet_segm_rot)
        Img_sujet_binarise = ants.image_read(path_image_sub_binaryse)
        Img_sujet_segmente_array = Img_sujet_segmente.numpy()
        Img_sujet_binarise_recal_array = Img_sujet_binarise.numpy()
        Img_sujet_segm_binar_combined_array = Img_sujet_segmente_array + Img_sujet_binarise_recal_array
        Image_segm_final = nib.Nifti1Image(Img_sujet_segm_binar_combined_array, affine=np.eye(4))
        path_img_final = tls.creation_chemin_nom_img(path_output, sujet, "segmentation_LR.nii.gz")
        nib.save(Image_segm_final,path_img_final)
    fin = time.time()
    tps_excecution = fin - debut
    print(f"le temps d'exécution du programme est : {tps_excecution} secondes")


if __name__ == "__main__":
    etape4()
