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



def etape4(nom_general_sujet, all_sujets_path,path_output, tab_img_sujet, list_path_threshold ):
    debut = time.time()
    #Recuperation des images segmentés et on les swap :
    list_path_img_segmente = tls.recup_les_sujets(nom_general_sujet, repertoire_sujet_segm = all_sujets_path)
    print(list_path_img_segmente)
    list_path_img_segmente_rot = [tls.creation_PATH_pour_fichier_swaper(sujet_path, path_output) for sujet_path in list_path_img_segmente]
    for path_sujet_rot, path_sujet in zip(list_path_img_segmente_rot, list_path_img_segmente):
        tls.SWAP_COPY_INFO_SAVE(path_sujet, path_sujet_rot)
    # ON additionne apres passage en numpy array les tableau de l'image segmenté du sujet l'image de l'hemisphère droit*10
    for path_sujet_segm_rot, path_image_sub_binaryse, sujet in zip(list_path_img_segmente_rot, list_path_threshold, tab_img_sujet):
        img_sujet_segmente = ants.image_read(path_sujet_segm_rot)
        img_sujet_binarise = ants.image_read(path_image_sub_binaryse)
        img_sujet_segmente_array = img_sujet_segmente.numpy()
        img_sujet_binarise_recal_array = img_sujet_binarise.numpy()
        img_sujet_segm_binar_combined_array = img_sujet_segmente_array + img_sujet_binarise_recal_array
        image_segm_final = nib.Nifti1Image(img_sujet_segm_binar_combined_array, affine=np.eye(4))
        path_img_final = tls.creation_chemin_nom_img(path_output, sujet, "segmentation_LR.nii.gz")
        nib.save(image_segm_final, path_img_final)
    fin = time.time()
    tps_excecution = fin - debut
    print(f"le temps d'exécution du programme est : {tps_excecution} secondes")


if __name__ == "__main__":
    path_variables = "/envau/work/meca/users/2024_Kamal/2024_stage_Kamal/variables"
    nom_general_sujet = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz'
    all_sujets_path = r"/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/"
    path_output = "/envau/work/meca/users/2024_Kamal/output/output_script4"
    tab_img_sujet = np.load(os.path.join(path_variables, "tab_img_sujet.npy"))
    list_path_threshold = np.load(os.path.join(path_variables, "list_path_threshold.npy"))
    etape4(nom_general_sujet, all_sujets_path, path_output, tab_img_sujet, list_path_threshold)
