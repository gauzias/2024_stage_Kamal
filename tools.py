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
                  for s in files if pattern.match(s) and root != all_sujets_path]
    return sorted(file_paths)


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


def Recalage_atlas(atlas_fix, img_mouv, type_transfo, interpolator, file_transfo_direct, file_transfo_inv):
    warp_sub = ants.registration(atlas_fix, img_mouv, type_of_transform=type_transfo, outprefix =file_transfo_direct )

    inv_warp = ants.registration(img_mouv, atlas_fix, type_of_transform=type_transfo,outprefix =file_transfo_inv )

    return ants.apply_transforms(atlas_fix, img_mouv, transformlist=warp_sub['fwdtransforms'], interpolator=interpolator), inv_warp


def path_abs_sujet_to_fichier_repertorie_sujet(tab_path):
    repertoire = [os.path.dirname(path) for path in tab_path]
    fichier = [os.path.basename(path) for path in tab_path]
    return repertoire, fichier

def Enregistrer_img_ants_en_nifit(img, path_repertoire, nom_img):
    ants.image_write(img, os.path.join(path_repertoire, nom_img))

def recupAtlas_to_tableau_simil(lignes_atlas,criteres, path_atlas, sujet, sujet_repertoire, type_transfo, interpolation, file_transfo_direct, file_transfo_inv):
    tab2D = pd.DataFrame(index=lignes_atlas, columns=criteres)
    print(sujet)
    sujet_ants = ants.image_read((os.path.join(sujet_repertoire, sujet)), reorient=True)
    list_warp = []
    for atlas in lignes_atlas:
        Atlas_recherche = ants.image_read((os.path.join(path_atlas, atlas)), reorient=True)
        Sujet_Warped, warp = Recalage_atlas(Atlas_recherche, sujet_ants, type_transfo, interpolation,file_transfo_direct, file_transfo_inv)
        list_warp.append(warp)
        for critere in criteres:
            similarity = calcul_similarity_ants(Atlas_recherche, Sujet_Warped, critere)
            tab2D.loc[atlas, critere] = similarity
    bon_atlas, indice_bon_atlas = Atlas_du_bon_age(tab2D)
    return tab2D, bon_atlas, list_warp[indice_bon_atlas]

def Atlas_du_bon_age(tab_similarity):
    abs_tab = tab_similarity.abs()
    max = abs_tab['MattesMutualInformation'].idxmax()
    indice = tab_similarity.index.get_loc(max)
    return max, indice

# def recal_sujet_avc_bon_atlas_save(path_des_atlas, bon_atlas, path_sujet, sujet, nom_general_sujet_rot):
#     Atlas_pour_sujet_ants = ants.image_read(os.path.join(path_des_atlas, bon_atlas))
#     img_sub = ants.image_read(os.path.join(path_sujet, sujet))
#     img_sub_recale = Recalage_atlas(Atlas_pour_sujet_ants, img_sub, "Rigid")
#     path_img_rot_rec = creation_chemin_nom_img(path_sujet, img_sub_recale, nom_general_sujet_rot)
#     Enregistrer_img_ants_en_nifit(img_sub_recale, path_sujet, path_img_rot_rec)

def creation_chemin_nom_img(path_repertoire_output, img_name, suffix_nom_image: str):
    nom_initial, fin = (img_name[:-7], ".nii.gz") if img_name.endswith(".nii.gz") else os.path.splitext(img_name)
    return os.path.join(path_repertoire_output, f"{nom_initial}_{suffix_nom_image}")

