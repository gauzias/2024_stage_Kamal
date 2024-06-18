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
from collections import Counter


def recup_sujet(all_sujets_path,nom_general_sujet):
    file_path = list()
    pattern = re.compile(nom_general_sujet)
    for root, dirs, files in os.walk(all_sujets_path):
        for s in files:
            if pattern.match(s) :
                file_path.append(os.path.join(root, s))
    file_path.sort()
    return file_path


def SWAP_COPY_INFO_SAVE(path_img_input, path_img_rot_nifti):
    img_input_array = recup_img_sujet_array (path_img_input)
    img_input_array_rot = np.transpose(img_input_array, (0, 1, 2))[::-1, ::1, ::-1] # x et z ont une transposé inverse et y une transposé
    img_input_rot_nifti = copy_info_geo(img_input_array_rot,path_img_input)
    nib.save(img_input_rot_nifti, path_img_rot_nifti)
def recup_img_sujet_array(path_img_input) :
    img_input_array = nib.load(path_img_input).get_fdata()  #trouver path,charger image nifti,conversion en array numpy
    return img_input_array
def copy_info_geo(img_recoit,img_give_copy):
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
        path =os.path.join(repertoire , f"{nom_initial}_rot{fin}")

        list_path_sujet_rot.append(path)
    return list_path_sujet_rot
def swap_each_SUB(path_list_sujet,list_path_sujet_rot):
    for path_sujet,path_sujet_rot in zip (path_list_sujet,list_path_sujet_rot) :
        SWAP_COPY_INFO_SAVE(path_sujet,path_sujet_rot)

def Parcours_dossier_only_data_match(Path, nom_caracteristic : str):
    files = os.listdir(Path)
    files_atlas = list()
    Pattern = re.compile(nom_caracteristic)
    for f in files:
        if Pattern.match(f):
            files_atlas.append(f)
    files_atlas.sort()
    return files_atlas

def tabs_1D_to_tab2D (donnee_ligne , donnee_colonne) :
    Tab_2D= pd.DataFrame(index=donnee_ligne, columns=donnee_colonne)
    return Tab_2D
def calcul_similarity_ants(img1, img2, critere):
    similarite = ants.image_similarity(img1, img2, metric_type=critere)
    return similarite
def Recalage_atlas_rigid(atlas_fix, img_mouv):
    Warp_Sub = ants.registration(atlas_fix, img_mouv,type_of_transform ='Rigid')
    Sub_Warped = ants.apply_transforms(atlas_fix, img_mouv, transformlist=Warp_Sub['fwdtransforms'])
    return Sub_Warped
def recup_atlas(fichier):
    fichier_recup = ants.image_read(os.path.join( fichier))
    return fichier_recup
def recupAtlas_to_tableau_simil (tab2D, ligne, colonne, path):
    for atlas in ligne:
        Atlas_recherche = recup_atlas(path,atlas)
        Sujet_Warped = Recalage_atlas_rigid(Atlas_recherche, sujet)
        for critere in colonne:
            similarity = calcul_similarity_ants(Atlas_recherche, Sujet_Warped, critere)
            tab2D.loc[atlas, critere] = similarity
    return tab2D # Atlas_du_bon_age(tab2D)
def Atlas_du_bon_age(tab_similarity):
    abs_tab = tab_similarity.abs()
    min_ecart = abs_tab['MeanSquares'].idxmin()
    max_MI =  abs_tab['MattesMutualInformation'].idxmax()
    max_Correlation =  abs_tab['Correlation'].idxmax()
    return (min_ecart,max_MI,max_Correlation)

def charger_le_meilleure(path_des_atlas, liste_atlas_pretendant):
    atlas1, atlas2, atlas3 = liste_atlas_pretendant
    if atlas1 == atlas2 or atlas1 == atlas3:
        Atlas_pour_sujet = recup_atlas(atlas1)
    else:
        if atlas2 == atlas3 or atlas2 == atlas1:
            Atlas_pour_sujet = recup_atlas(atlas2)
        else:
            print("aucun atlas ne réunis 2 critères")
    return Atlas_pour_sujet


if __name__ == "__main__":
    #Conversion d'image nifti en numpy array en 3d
    # input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w = nib.load('/home/achalhi.k/Bureau/Lien vers 2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz')
    # sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w = input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w.get_fdata()
    # #print(type(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w[1,1,1]))
    #
    # # On swap l'image
    # sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot = np.transpose(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w, (0,1,2))[::-1,::1,::-1]
    #
    #Copie des informaations géométrique / Fslcpgeom
    #Conversion de np array vers fichier nifti
    #Sub_0001_template_masked_rot_nifti = np.array(, dtype = np.float64)
    #Sub_0001_template_masked_rot_nifti
    # Enregistrer l'image NIfTI
    # path_pour_fichier_rot = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz"
    # nib.save(Sub_0001_template_masked_rot_nifti, path_pour_fichier_rot)
    #:sub_2_temp_ro_r = ants.registration(fixed=fi, moving=img_sub_aligned_rot_ants, type_of_transform = 'SyN' )
    #Parcours d'un dossier pour trouver le bon atlas du bon(du bon âge), il faut un critère qu'on cherche à minimiser
    # nii.gz image conversion pour ants :
    nom_general_sujet = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz'
    nom_general_sujet_rot = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz'
    all_sujets_path = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/"
    Nom_caract = r'^STA\d+\.nii.gz'
    path_des_atlas = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2"

    files_atlas = Parcours_dossier_only_data_match(path_des_atlas, Nom_caract)

    tab_path_sujet = recup_sujet(all_sujets_path,nom_general_sujet)
    print(tab_path_sujet )
    list_path_sujet_rot = creation_PATH_pour_fichier_swaper(tab_path_sujet)
    print(list_path_sujet_rot)
    swap_each_SUB(tab_path_sujet, list_path_sujet_rot)
    tab_path_sujet_rot = recup_sujet(all_sujets_path, nom_general_sujet_rot)
    print(tab_path_sujet_rot)
    criteres = ['MeanSquares', 'MattesMutualInformation', 'Correlation']
    tableau_criteres_by_atlas = tabs_1D_to_tab2D(files_atlas,criteres)
    print("avant l'ecriture dans le fichier")
    path_fichier = '/envau/work/meca/users/2024_Kamal/2024_stage_Kamal/outputKamal.txt'
    output_directory = '/envau/work/meca/users/2024_Kamal/2024_stage_Kamal/'
    if os.access(output_directory, os.W_OK ):
        print(("le repertoire est accessible pour lecrire"))
    else:
        print("pas permis")
    try :
        with open(path_fichier, 'w') as f:
            sys.stdout = f
            for sujet_path in tab_path_sujet_rot:
                tab2D_global = recupAtlas_to_tableau_simil(tableau_criteres_by_atlas, files_atlas, criteres, sujet_path)
                print(tab2D_global)
                min_ecart, max_MI, max_Correlation = Atlas_du_bon_age(tab2D_global)
                print(f"l'atlas qui minimise l'equart à la moyenne est : {min_ecart} pour {sujet_path}\n",
                      f"l'atlas qui maximise l'information mutuel est : {max_MI} pour {sujet_path}\n",
                      f"l'atlas qui maximise la correlation est : {max_Correlation} pour {sujet_path}\n")
            sys.stdout = sys.__stdout__
            f.flush()
            print("apres fichier ecrit")
    except IOError as e:
        print(f"erreur d'entree/sortie lors de l'écritute dans le fichier {e}")
    except Exception as e:
        print(f"erreur  lors de l'écritute dans le fichier {e}")




   # print(tab)

    # print(tab_sujet)
    # sujet001_path = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/"
    # sujet0001_rot = "sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz"
    # img_path =os.path.join(sujet001_path,sujet0001_rot)
    # img_sub_aligned_ants = ants.image_read(img_path)
    # print(files_atlas)
    # print(len(files_atlas))











    #tab =



    # for atlas in files_atlas:
    #    Atlas_rchrche = ants.image_read(os.path.join(path_des_atlas,atlas))
    #    Atlas_Warped = Recalage_atlas_rigid(img_sub_aligned_ants, Atlas_rchrche)
    #    for critere in criteres:
    #       similarity = calcul_similarity_ants(img_sub_aligned_ants, Atlas_Warped, critere)
    #       tableau_criteres_by_atlas.loc[atlas, critere] = similarity
    # print(tableau_criteres_by_atlas)

    #Fonction pour recaler sta34 à notre sujet 0001


    # Atlas_25 = ants.image_read(os.path.join(path_des_atlas,"STA25.nii.gz"))
    #
    # SWAP_COPY_INFO_SAVE(os.path.join(path_des_atlas,"STA25.nii.gz"), "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2/STA25_rot.nii.gz")
    # Atlas_25_ROT = ants.image_read(os.path.join(path_des_atlas,"STA25_rot.nii.gz"))
    # plt.imshow(Atlas_25[60,:,:])
    # plt.show()
    # plt.imshow(Atlas_25_ROT[60,:,:])
    # plt.show()
    # Warped_atlas = Recalage_atlas_rigid(img_sub_aligned_ants, Atlas_25_ROT)
    # plt.imshow(Warped_atlas[60,:,:])
    # plt.show()
    # plt.imshow(img_sub_aligned_ants[60,:,:])
    # plt.show()
    # path_fct_rigid_recalage = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2/STA34_ROT_RECpy.nii.gz"
    # nib.save(Warped_atlas,path_fct_rigid_recalage)
