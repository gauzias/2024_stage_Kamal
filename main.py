import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt 
import nibabel as nib
import nisnap
import ants
import os
import re
import glob
import pandas as pd
import sys
import io
import time
def recup_sujet(all_sujets_path, nom_general_sujet):
    file_path = list()
    pattern = re.compile(nom_general_sujet)
    for root, dirs, files in os.walk(all_sujets_path):
        for s in files:
            if (pattern.match(s) and (root != all_sujets_path)): #ici je cherche à imposer un nom type à recup en évitant les fichiers placés à lastest_nesvor qui ont le même nom
                file_path.append(os.path.join(root, s))
    file_path.sort()
    return file_path

def SWAP_COPY_INFO_SAVE(path_img_input, path_img_rot_nifti):
    img_input_array = recup_img_sujet_array(path_img_input)
    img_input_array_rot = np.transpose(img_input_array, (0, 1, 2))[::-1, ::1, ::-1] # x et z ont une transposé inverse et y une transposé
    img_input_rot_nifti = copy_info_geo(img_input_array_rot, path_img_input)
    nib.save(img_input_rot_nifti, path_img_rot_nifti)
def recup_img_sujet_array(path_img_input):
    img_input_array = nib.load(path_img_input).get_fdata()  #trouver path,charger image nifti,conversion en array numpy
    return img_input_array
def copy_info_geo(img_recoit, img_give_copy):
    return nib.Nifti1Image(img_recoit, nib.load(os.path.abspath(img_give_copy)).affine, nib.load(os.path.abspath(img_give_copy)).header)
def creation_PATH_pour_fichier_swaper(list_path_sujet):
    list_path_sujet_rot = list()
    for path_in in list_path_sujet:
        repertoire = os.path.dirname(path_in)
        fichier = os.path.basename(path_in)
        if fichier.endswith(".nii.gz"):
            nom_initial = fichier[:-7]
            fin = ".nii.gz"
        else:
            nom_initial, fin = os.path.splitext(fichier)
        path =os.path.join(repertoire, f"{nom_initial}_rot{fin}")

        list_path_sujet_rot.append(path)
    return list_path_sujet_rot
def swap_each_SUB(path_list_sujet, list_path_sujet_rot):
    for path_sujet, path_sujet_rot in zip(path_list_sujet, list_path_sujet_rot):
        SWAP_COPY_INFO_SAVE(path_sujet, path_sujet_rot)

def Parcours_dossier_only_data_match(Path, nom_caracteristic : str):
    files = os.listdir(Path)
    files_atlas = list()
    Pattern = re.compile(nom_caracteristic)
    for f in files:
        if Pattern.match(f):
            files_atlas.append(f)
    files_atlas.sort()
    return files_atlas

def tabs_1D_to_tab2D (donnee_ligne, donnee_colonne):
    Tab_2D= pd.DataFrame(index=donnee_ligne, columns=donnee_colonne)
    return Tab_2D
def calcul_similarity_ants(img1, img2, critere):
    similarite = ants.image_similarity(img1, img2, metric_type=critere)
    return similarite
def Recalage_atlas(atlas_fix, img_mouv, type_transfo):
    type_of_transform = type_transfo
    Warp_Sub = ants.registration(atlas_fix, img_mouv, type_of_transform)
    Sub_Warped = ants.apply_transforms(atlas_fix, img_mouv, transformlist=Warp_Sub['fwdtransforms'][0])
    return Sub_Warped

def recup_atlas_sujet(path_repertoire, fichier):
    fichier_recup = ants.image_read(os.path.join(path_repertoire, fichier))
    return fichier_recup
def path_abs_sujet_to_fichier_repertorie_sujet(tab_path):
    repertoire = list()
    fichier = list()
    for path in tab_path:
        repertoire.append(os.path.dirname(path))
        fichier.append(os.path.basename(path))
    return repertoire, fichier
def Enregistrer_img_ants_en_nifit(img,path_repertoire, nom_img):
    path_abs = os.path.join(path_repertoire, nom_img)
    ants.image_write(img, path_abs)

def recupAtlas_to_tableau_simil (tab2D, ligne, colonne, path_atlas, sujet, sujet_repertoire, type_transfo):
    sujet_ants = recup_atlas_sujet(sujet_repertoire, sujet)

    for atlas in ligne:
        Atlas_recherche = recup_atlas_sujet(path_atlas, atlas)
        Sujet_Warped = Recalage_atlas(Atlas_recherche, sujet_ants, type_transfo)
        for critere in colonne:
            similarity = calcul_similarity_ants(Atlas_recherche, Sujet_Warped, critere)
            tab2D.loc[atlas, critere] = similarity
    return tab2D # Atlas_du_bon_age(tab2D)
def Atlas_du_bon_age(tab_similarity):
    abs_tab = tab_similarity.abs()
    max_MI = abs_tab['MattesMutualInformation'].idxmax()
    max_Correlation = abs_tab['Correlation'].idxmax()
    return (max_MI, max_Correlation)

def retourne_bon_atlas(liste_atlas_pretendant):
    atlas1, atlas2 = liste_atlas_pretendant
    if atlas1 == atlas2:
        Atlas_pour_sujet = atlas1
    else:
        Atlas_pour_sujet = atlas1
        print("aucun atlas ne réunis 2 critères")
    return Atlas_pour_sujet
def recal_sujet_avc_bon_atlas_save(path_des_atlas, liste_atlas_pretendant,path_sujet, sujet, nom_general_sujet_rot):
    bon_atlas = retourne_bon_atlas(path_des_atlas, liste_atlas_pretendant)
    Atlas_pour_sujet_ants = ants.image_read(os.path.join(path_des_atlas, bon_atlas))
    img_sub = ants.image_read(os.path.join(path_sujet, sujet))
    img_sub_0019_recale = Recalage_atlas(Atlas_pour_sujet_ants, img_sub)
    path_img_rot_rec =creation_chemin_nom_img_rot_rec(path_sujet, nom_general_sujet_rot)
    Enregistrer_img_ants_en_nifit(img_sub_0019_recale, path_sujet, path_img_rot_rec)

def creation_chemin_nom_img_rot_rec(path_repertoire, img_rot_name):
    if img_rot_name.endswith(".nii.gz"):
        nom_initial = img_rot_name[:-7]
        fin = ".nii.gz"
    else:
        nom_initial, fin = os.path.splitext(img_rot_name)
    path = os.path.join(path_repertoire, f"{nom_initial}_rec{fin}")
    return path

if __name__ == "__main__":
    debut = time.time()
    # Parcours d'un dossier pour trouver le bon atlas du bon(du bon âge), il faut un critère qu'on cherche à minimiser
    # nii.gz image conversion pour ants :
    nom_general_sujet = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz'
    nom_general_sujet_rot = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz'
    all_sujets_path = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/"
    Nom_caract = r'^STA\d+\.nii.gz'
    path_des_atlas = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2"

    files_atlas = Parcours_dossier_only_data_match(path_des_atlas, Nom_caract)

    tab_path_sujet = recup_sujet(all_sujets_path, nom_general_sujet)
    print(tab_path_sujet)
    list_path_sujet_rot = creation_PATH_pour_fichier_swaper(tab_path_sujet)
    print(list_path_sujet_rot)
    swap_each_SUB(tab_path_sujet, list_path_sujet_rot)
    tab_path_sujet_rot = recup_sujet(all_sujets_path, nom_general_sujet_rot)
    tab_repertoire, tab_img_sujet = path_abs_sujet_to_fichier_repertorie_sujet(tab_path_sujet_rot)
    criteres = ['MattesMutualInformation', 'Correlation'] # Je retire MeanSquares erreur car ils prends en compe les differences d'intensité ce qui est pas parlant ici car img pris avec appareil diff
    tableau_criteres_by_atlas = tabs_1D_to_tab2D(files_atlas, criteres)
    List_atlas_finaux = list()
    total_frame = []
    for sujet, repertoire in zip(tab_img_sujet, tab_repertoire):

        tab2D_global = recupAtlas_to_tableau_simil(tableau_criteres_by_atlas, files_atlas, criteres, path_des_atlas, sujet, repertoire, "Rigid")
        print(tab2D_global)

        tab2D_global_array = [tab2D_global.to_numpy()]
        total_frame.append(tab2D_global_array)

        list_atlas_pretendant = Atlas_du_bon_age(tab2D_global)
        Atlas_max_MI, Atlas_max_Correlation = list_atlas_pretendant
        Atlas_final = retourne_bon_atlas(list_atlas_pretendant)
        List_atlas_finaux.append(Atlas_final)

        print(f"l'atlas qui maximise l'information mutuel est : {Atlas_max_MI} pour {sujet}\n",
              f"l'atlas qui maximise la correlation est : {Atlas_max_Correlation} pour {sujet}\n")

    print(total_frame)
    tableau_bon_atlas_by_sujet = list(zip(tab_img_sujet, List_atlas_finaux))
    print(tableau_bon_atlas_by_sujet)

    fin = time.time()
    tps_excecution = fin - debut
    print(f"le temps d'éxecution du programme est : {tps_excecution} secondes")