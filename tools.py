import os
import re
import time
import numpy as np
import pandas as pd
import nibabel as nib
import ants


def recup_sujet(all_sujets_path, nom_general_sujet):
    pattern = re.compile(nom_general_sujet)
    file_paths = [os.path.join(root, s)
                  for root, _, files in os.walk(all_sujets_path)
                  for s in files if pattern.match(s)]
    return sorted(file_paths)


def separe_fichier_img_reel_img_segm(all_sujets_path, nom_general_sujet):
    file_paths = recup_sujet(all_sujets_path, nom_general_sujet)
    path_img_reel = []
    path_img_segm = []
    base_dir = os.path.normpath(all_sujets_path) #ces noermalisation servent à faire attention au slash pour être sur de se trouver à la bonne prfondeur (bon sous repertorie)
    for path in file_paths:
        chemin_normalized = os.path.normpath(path)
        repertoire = os.path.dirname(chemin_normalized)
        if os.path.commonpath([all_sujets_path, repertoire]) == base_dir and repertoire == base_dir:
            path_img_segm.append(path)
        else:
            path_img_reel.append(path)
    print(path_img_reel, path_img_segm)
    return path_img_reel, path_img_segm


# def chang_recup_nom_img_segm (old_name, all_sujets_path):
#     path_img_reel, path_img_segm = separe_fichier_img_reel_img_segm(all_sujets_path, old_name)
#     new_paths = [creation_chemin_nom_img(path_img, old_name, "Segmented") for path_img in path_img_segm]
#     for new_path, old_path in zip(new_paths, path_img_segm):
#          os.rename(old_path, new_path)
#     return new_paths


def copy_info_geo(img_recoit, img_give_copy):
    img_copy = nib.load(os.path.abspath(img_give_copy))
    return nib.Nifti1Image(img_recoit, img_copy.affine, img_copy.header)


def SWAP_COPY_INFO_SAVE(path_img_input, path_img_rot_nifti):
    if os.path.exists(path_img_rot_nifti):
        print("ça existe déja")
    else :
        img_input_array = nib.load(path_img_input).get_fdata()
        img_input_array_rot = np.transpose(img_input_array, (0, 1, 2))[::-1, ::1, ::-1]
        img_input_rot_nifti = copy_info_geo(img_input_array_rot, path_img_input)
        nib.save(img_input_rot_nifti, path_img_rot_nifti)


def creation_PATH_pour_fichier_swaper(path_sujet, repertoire_output):
    fichier = os.path.basename(path_sujet)
    nom_initial, fin = (fichier[:-7], ".nii.gz") if fichier.endswith(".nii.gz") else os.path.splitext(fichier)
    return os.path.join(repertoire_output, f"{nom_initial}_rot{fin}")


def Parcours_dossier_only_data_match(Path, nom_caracteristic):
    pattern = re.compile(nom_caracteristic)
    return sorted(f for f in os.listdir(Path) if pattern.match(f))


def calcul_similarity_ants(img1, img2, critere):
    return ants.image_similarity(img1, img2, metric_type=critere)


def Recalage_atlas(atlas_fix, img_mouv, type_transfo, interpolator):
    warp_sub = ants.registration(atlas_fix, img_mouv, type_of_transform=type_transfo)
    return ants.apply_transforms(atlas_fix, img_mouv, transformlist=warp_sub['fwdtransforms'], interpolator=interpolator)


def SAVE_Transfo_rec_mat(atlas_fix, img_mouv, type_transfo, file_transfo_direct, file_transfo_inv, name_sujet, name_atlas):
    path_file_transfo_direct = creation_chemin_fichier_mat(file_transfo_direct, name_sujet, name_atlas)
    path_file_transfo_inv = creation_chemin_fichier_mat(file_transfo_inv, name_sujet, name_atlas)
    if os.path.exists(path_file_transfo_direct):
        print("ça existe déja")
    ants.registration(atlas_fix, img_mouv, type_of_transform=type_transfo, outprefix=path_file_transfo_direct + '_direct_')
    if os.path.exists(path_file_transfo_inv):
        print("ça existe déja")
    ants.registration(img_mouv, atlas_fix, type_of_transform=type_transfo, outprefix=path_file_transfo_inv + '_Inverse_')
    return path_file_transfo_direct, path_file_transfo_inv


def path_abs_sujet_to_fichier_repertorie_sujet(tab_path):
    repertoire = [os.path.dirname(path) for path in tab_path]
    fichier = [os.path.basename(path) for path in tab_path]
    return repertoire, fichier


def Enregistrer_img_ants_en_nifit(img, path_repertoire, nom_img):
    ants.image_write(img, os.path.join(path_repertoire, nom_img))


def tab2d_atlas_sim_critere(lignes_atlas,criteres):
    tab2D = np.zeros((len(lignes_atlas), 3), dtype=object)
    tab2D[:, 0] = lignes_atlas
    tab2D[:, 2] = np.array(criteres[0])
    return tab2D


def recupAtlas_to_tableau_simil(lignes_atlas, criteres, path_atlas, sujet, sujet_repertoire, type_transfo, interpolation):
    tab2D = tab2d_atlas_sim_critere(lignes_atlas,criteres)
    sujet_ants = ants.image_read((os.path.join(sujet_repertoire, sujet)))
    for i in range(len(tab2D[:, 0])):
        Atlas_recherche = ants.image_read((os.path.join(path_atlas, tab2D[i, 0])))
        Sujet_Warped = Recalage_atlas(Atlas_recherche, sujet_ants, type_transfo, interpolation)
        for critere in criteres:
            similarity = calcul_similarity_ants(Atlas_recherche, Sujet_Warped, critere)
            tab2D[i, 1] = similarity
    print(tab2D)
    return tab2D

def atlas_du_bon_age(lignes_atlas, criteres, path_atlas, sujet, sujet_repertoire, type_transfo, interpolation):
    tab_similarity = recupAtlas_to_tableau_simil(lignes_atlas, criteres, path_atlas, sujet, sujet_repertoire, type_transfo, interpolation)
    indice_val_max = np.argmax(np.abs(tab_similarity[:, 1].astype(float)))
    nom_max = tab_similarity[indice_val_max, 0]
    return nom_max

def recup_bon_atlas_avc_transfos(lignes_atlas, criteres, path_atlas, sujet, sujet_repertoire, type_transfo, interpolation, file_transfo_direct, file_transfo_inv):
    bon_atlas = atlas_du_bon_age(lignes_atlas, criteres, path_atlas, sujet, sujet_repertoire, type_transfo, interpolation)
    sujet_ants = ants.image_read((os.path.join(sujet_repertoire,sujet)))
    atlas_ants = ants.image_read((os.path.join(path_atlas, bon_atlas)), reorient=True)
    path_trf_direct, path_trf_inv = SAVE_Transfo_rec_mat(atlas_ants, sujet_ants, type_transfo, file_transfo_direct, file_transfo_inv, sujet, bon_atlas)
    return bon_atlas, path_trf_direct, path_trf_inv
# def Atlas_du_bon_age(tab_similarity):
#     abs_tab = tab_similarity.abs()
#     max = abs_tab['MattesMutualInformation'].idxmax()
#     return max


def creation_chemin_nom_img(path_repertoire_output, img_name, suffix_nom_image: str):
    nom_initial, fin = (img_name[:-7], ".nii.gz") if img_name.endswith(".nii.gz") else os.path.splitext(img_name)
    return os.path.join(path_repertoire_output, f"{nom_initial}_{suffix_nom_image}")


def creation_chemin_fichier_mat(path_repertoire_output,img_name, atlas_name):
    nom_initial, fin = (img_name[:-7], ".gz") if img_name.endswith(".nii.gz") else os.path.splitext(img_name)
    nom_2, fin2 = (atlas_name[:-7], ".gz") if atlas_name.endswith(".nii.gz") else os.path.splitext(atlas_name)
    return os.path.join(path_repertoire_output, f"{nom_initial}_{nom_2}")
