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
# from shared_module import List_atlas_finaux, tab_img_sujet, list_warp_inv
# Je déclare des variables globales pour pouvoir les récuperer dans le script 2 et poursuivre sans tout recalculer

def etape1(nom_general_sujet_in_template, nom_general_sujet_in_self_space, all_sujets_path, path_ouput, Nom_caract, path_des_atlas, file_transfo_direc, file_transfo_inv):
    debut = time.time()
    files_atlas = tls.Parcours_dossier_only_data_match(path_des_atlas, Nom_caract)
    # cas =  tls.determine_cas_template_or_self(nom_general_sujet_in_template, all_sujets_path)
     # cas,tab_path_sujet tls.determine_cas_template_or_self(nom_general_sujet_in_template, nom_general_sujet_in_self_space, all_sujets_path)
    tab_path_sujet_self, tab_path_sujet_segm = tls.separe_fichier_img_reel_img_segm(all_sujets_path, nom_general_sujet_in_self_space)
    list_path_sujet_rot = [tls.creation_PATH_pour_fichier_swaper(sujet_path, path_ouput) for sujet_path in tab_path_sujet_self]
    for path_sujet_rot, path_sujet in zip(list_path_sujet_rot, tab_path_sujet_self):
        tls.SWAP_COPY_INFO_SAVE(path_sujet, path_sujet_rot)
    tab_repertoire_self_rot, tab_img_sujet_self_rot = tls.path_abs_sujet_to_fichier_repertorie_sujet(list_path_sujet_rot)
    criteres = ['MattesMutualInformation']
    list_atlas_finaux = list()
    list_tranf_direc = []
    list_tranf_inv = []
    for sujet, repertoire in zip(tab_img_sujet_self_rot, tab_repertoire_self_rot):
        bon_atlas, path_trf_direct, path_trf_inv = tls.recup_bon_atlas_avc_transfos(files_atlas, criteres, path_des_atlas, sujet, repertoire, "Rigid", "linear", file_transfo_direc, file_transfo_inv)
        list_atlas_finaux.append(bon_atlas)
        list_tranf_direc.append(path_trf_direct)
        list_tranf_inv.append(path_trf_inv)
        print(f"l'atlas qui maximise l'information mutuel est : {bon_atlas} pour {sujet}\n")
    fin = time.time()
    tps_excecution = fin - debut
    print(f"le temps d'exécution du programme est : {tps_excecution} secondes")
    return list_atlas_finaux, tab_img_sujet, list_tranf_direc, list_tranf_inv
# def process_cas1_template_and_self():
#     if cas == 1 :
#         list_path_transfo_template_to_sujet = []
#         tab_repertoire_sujet_self_space, tab_fichier_sujet_self_space = tls.path_abs_sujet_to_fichier_repertorie_sujet(tab_path_sujet_self)
#         for sujet_template, repertoire_template, sujet_in_self, repertoire_self in zip(tab_img_sujet, tab_repertoire, tab_fichier_sujet_self_space, tab_repertoire_sujet_self_space):
#             sujet_template = ants.image_read((os.path.join(repertoire_template, sujet_template)))
#             sujet_self_space = ants.image_read((os.path.join(repertoire_self, sujet_in_self)))
#             path_transfo_template_to_space = tls.creation_chemin_fichier_mat(file_transfo_direc,sujet_template, sujet_in_self)
#             ants.registration(sujet_self_space,sujet_template,type_of_transform = "Rigid", outprefix = path_transfo_template_to_space)
#             list_path_transfo_template_to_sujet.append(path_transfo_template_to_space)
#         return list_path_transfo_template_to_sujet, tab_path_sujet_self



if __name__ == "__main__":
    file_transfo_direc = r'/envau/work/meca/users/2024_Kamal/output/output_script1'
    file_transfo_inv = r'/envau/work/meca/users/2024_Kamal/output/output_script2'
    path_variables = "/home/achalhi.k/2024_stage_Kamal/variables"
    nom_general_sujet_in_template = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_T2w.nii.gz'
    nom_general_sujet_in_self_space = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz'
    all_sujets_path = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor"
    path_ouput = "/envau/work/meca/users/2024_Kamal/output/output_script1"
    Nom_caract = r'^STA\d+\.nii.gz'
    path_des_atlas = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2"
    list_atlas_finaux, tab_img_sujet_self_rot, list_tranf_direc, list_tranf_inv = etape1(nom_general_sujet_in_template, nom_general_sujet_in_self_space, all_sujets_path, path_ouput, Nom_caract,path_des_atlas, file_transfo_direc, file_transfo_inv)

    print(list_atlas_finaux, tab_img_sujet_self_rot, list_tranf_inv)
    np.save(os.path.join(path_variables, "list_atlas_finaux.npy"), list_atlas_finaux, allow_pickle='False')
    np.save(os.path.join(path_variables, "tab_img_sujet_self_rot.npy"), tab_img_sujet_self_rot, allow_pickle='False')
    np.save(os.path.join(path_variables, "list_tranf_direc.npy"), list_tranf_direc, allow_pickle='False')
    np.save(os.path.join(path_variables, "list_tranf_inv.npy"), list_tranf_inv, allow_pickle='False')
    # np.save(os.path.join(path_variables, "list_path_transfo_template_to_sujet.npy"), list_path_transfo_template_to_sujet, allow_pickle='False')
    # np.save(os.path.join(path_variables, "tab_path_sujet_self.npy"), tab_path_sujet_self, allow_pickle='False')
    # np.save(os.path.join(path_variables, "cas.npy"), cas, allow_pickle='False')