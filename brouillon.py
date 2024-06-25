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
    img_input_array = nib.load(path_img_input).get_fdata()
    img_input_array_rot = np.transpose(img_input_array, (0, 1, 2))[::-1, ::1, ::-1]
    img_input_rot_nifti = copy_info_geo(img_input_array_rot, path_img_input)
    nib.save(img_input_rot_nifti, path_img_rot_nifti)

def creation_PATH_pour_fichier_swaper(list_path_sujet):
    list_path_sujet_rot = []
    for path_in in list_path_sujet:
        repertoire = os.path.dirname(path_in)
        fichier = os.path.basename(path_in)
        nom_initial, fin = (fichier[:-7], ".nii.gz") if fichier.endswith(".nii.gz") else os.path.splitext(fichier)
        list_path_sujet_rot.append(os.path.join(repertoire, f"{nom_initial}_rot{fin}"))
    return list_path_sujet_rot

def swap_each_SUB(path_list_sujet, list_path_sujet_rot):
    for path_sujet, path_sujet_rot in zip(path_list_sujet, list_path_sujet_rot):
        SWAP_COPY_INFO_SAVE(path_sujet, path_sujet_rot)

def Parcours_dossier_only_data_match(Path, nom_caracteristic):
    pattern = re.compile(nom_caracteristic)
    return sorted(f for f in os.listdir(Path) if pattern.match(f))

def tabs_1D_to_tab2D(donnee_ligne, donnee_colonne):
    return pd.DataFrame(index=donnee_ligne, columns=donnee_colonne)

def calcul_similarity_ants(img1, img2, critere):
    return ants.image_similarity(img1, img2, metric_type=critere)

def Recalage_atlas(atlas_fix, img_mouv, type_transfo, masque):
    warp_sub = ants.registration(atlas_fix, img_mouv, type_transfo)
    return ants.apply_transforms(atlas_fix, img_mouv, transformlist=warp_sub['fwdtransforms'][0],interpolator = 'nearestNeighbor', mask = masque )
def Inv_Recalage_atlas(atlas, img_mouv,type_transfo) :
    warp_sub = ants.registration(img_mouv, atlas,   type_transfo)
    return ants.apply_transforms(img_mouv, atlas,   transformlist=warp_sub['fwdtransforms'], interpolator = 'nearestNeighbor')

def recup_atlas_sujet(path_repertoire, fichier):
    return ants.image_read(os.path.join(path_repertoire, fichier))

def path_abs_sujet_to_fichier_repertorie_sujet(tab_path):
    repertoire = [os.path.dirname(path) for path in tab_path]
    fichier = [os.path.basename(path) for path in tab_path]
    return repertoire, fichier

def Enregistrer_img_ants_en_nifit(img, path_repertoire, nom_img):
    ants.image_write(img, os.path.join(path_repertoire, nom_img))

def recupAtlas_to_tableau_simil(tab2D, ligne, colonne, path_atlas, sujet, sujet_repertoire, type_transfo):
    sujet_ants = recup_atlas_sujet(sujet_repertoire, sujet)
    for atlas in ligne:
        Atlas_recherche = recup_atlas_sujet(path_atlas, atlas)
        Sujet_Warped = Recalage_atlas(Atlas_recherche, sujet_ants, type_transfo)
        for critere in colonne:
            similarity = calcul_similarity_ants(Atlas_recherche, Sujet_Warped, critere)
            tab2D.loc[atlas, critere] = similarity
    return tab2D

def Atlas_du_bon_age(tab_similarity):
    abs_tab = tab_similarity.abs()
    return abs_tab['MattesMutualInformation'].idxmax(), abs_tab['Correlation'].idxmax()

def retourne_bon_atlas(liste_atlas_pretendant):
    atlas1, atlas2 = liste_atlas_pretendant
    if atlas1 == atlas2:
        return atlas1
    print("aucun atlas ne réunit 2 critères")
    return atlas1

def recal_sujet_avc_bon_atlas_save(path_des_atlas, bon_atlas, path_sujet, sujet, nom_general_sujet_rot):
    Atlas_pour_sujet_ants = ants.image_read(os.path.join(path_des_atlas, bon_atlas))
    img_sub = ants.image_read(os.path.join(path_sujet, sujet))
    img_sub_recale = Recalage_atlas(Atlas_pour_sujet_ants, img_sub, "Rigid")
    path_img_rot_rec = creation_chemin_nom_img_rot_rec(path_sujet, nom_general_sujet_rot)
    Enregistrer_img_ants_en_nifit(img_sub_recale, path_sujet, path_img_rot_rec)

def creation_chemin_nom_img_rot_rec(path_repertoire, img_rot_name, nom_atlas_segm : str):

    nom_initial, fin = (img_rot_name[:-7], ".nii.gz") if img_rot_name.endswith(".nii.gz") else os.path.splitext(img_rot_name)
    return os.path.join(path_repertoire, f"{nom_initial}_{nom_atlas_segm}")

def creation_chemin_nom_img_threshold(path_repertoire, img, nom_atlas_threshold : str):

    nom_initial, fin = (img[:-7], ".nii.gz") if img.endswith(".nii.gz") else os.path.splitext(img)
    return os.path.join(path_repertoire, f"{nom_initial}_{nom_atlas_threshold}{fin}")
if __name__ == "__main__":
    debut = time.time()

    nom_general_sujet = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz'
    nom_general_sujet_rot = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz'
    all_sujets_path = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/"
    Nom_caract = r'^STA\d+\.nii.gz'
    path_des_atlas = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2"

    files_atlas = Parcours_dossier_only_data_match(path_des_atlas, Nom_caract)
    tab_path_sujet = recup_sujet(all_sujets_path, nom_general_sujet)
    #list_path_sujet_rot = creation_PATH_pour_fichier_swaper(tab_path_sujet)
    #swap_each_SUB(tab_path_sujet, list_path_sujet_rot)

    tab_path_sujet_rot = recup_sujet(all_sujets_path, nom_general_sujet_rot)
    print(tab_path_sujet_rot)
    tab_repertoire, tab_img_sujet = path_abs_sujet_to_fichier_repertorie_sujet(tab_path_sujet_rot)
    # criteres = ['MattesMutualInformation','Correlation']
    # tableau_criteres_by_atlas = tabs_1D_to_tab2D(files_atlas, criteres)
    #
    # List_atlas_finaux = []
    # total_frame = []
    # for sujet, repertoire in zip(tab_img_sujet, tab_repertoire):
    #     tab2D_global = recupAtlas_to_tableau_simil(tableau_criteres_by_atlas, files_atlas, criteres, path_des_atlas, sujet, repertoire, "Rigid")
    #     print(tab2D_global)
    #
    #     tab2D_global_array = [tab2D_global.to_numpy()]
    #     total_frame.append(tab2D_global_array)
    #
    #     list_atlas_pretendant = Atlas_du_bon_age(tab2D_global)
    #     Atlas_final = retourne_bon_atlas(list_atlas_pretendant)
    #     List_atlas_finaux.append(Atlas_final)
    #     print(f"l'atlas qui maximise l'information mutuel est : {list_atlas_pretendant[0]} pour {sujet}\n",
    #           f"l'atlas qui maximise la correlation est : {list_atlas_pretendant[1]} pour {sujet}\n")
    #
    # tableau_bon_atlas_by_sujet = [(tab_img_sujet), (List_atlas_finaux)]
    # print(tableau_bon_atlas_by_sujet)

    tableau_bon_atlas_by_sujet= [['sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz', 'sub-0002_ses-0002_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz', 'sub-0009_ses-0012_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz', 'sub-0019_ses-0022_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz', 'sub-0081_ses-0093_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz'], ['STA25.nii.gz', 'STA23.nii.gz', 'STA30.nii.gz', 'STA28.nii.gz', 'STA24.nii.gz']]
    (tab_img_sujet), (List_atlas_finaux) = tableau_bon_atlas_by_sujet
    #On cherche à recaler l'atlas sur l'image (une inversion du recalage), nous utilisons cette fois l'atlas segmenté
    #NOM des ATLAS SEGMENTÉ
    nom_atlas_binary = 'r^STA\d+\_all_reg_LR_dilM.nii.gz'
    path_des_atlas_binary = r'/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas'
    les_atlas_binary = []
    SUB_rec_by_Atlas_PATH = []
    for atlas in List_atlas_finaux :
        nom, fin = (atlas[:-7], ".nii.gz") if atlas.endswith(".nii.gz") else os.path.splitext(atlas)
        numero_atlas = nom.split('STA')[1]
        print(numero_atlas)
        les_atlas_binary.append(f'STA{numero_atlas}_all_reg_LR_dilM.nii.gz')
    for sujet, repertoire, atlas in zip(tab_img_sujet, tab_repertoire, les_atlas_binary):
        Sujet_fixe = ants.image_read(os.path.join(repertoire, sujet))
        Atlas_binary = ants.image_read(os.path.join(path_des_atlas_binary, atlas))
        SUB_recal_atlas_segm = Inv_Recalage_atlas(Atlas_binary,Sujet_fixe,  "Rigid")
        path_sub_recale_by_atlas_binary = creation_chemin_nom_img_rot_rec(repertoire, sujet, atlas)
        SUB_rec_by_Atlas_PATH.append(path_sub_recale_by_atlas_binary)
        Enregistrer_img_ants_en_nifit(SUB_recal_atlas_segm, os.path.join(repertoire, sujet), path_sub_recale_by_atlas_binary)


        #Seuillage par hemisphère et importer image segmenter

    list_repertoire, list_image_sub_recal =path_abs_sujet_to_fichier_repertorie_sujet(SUB_rec_by_Atlas_PATH)

    list_path_threshold = []
    for image_sub_recal, repertoire in zip(list_image_sub_recal, list_repertoire):
        Image_recal_array = nib.load(os.path.join(repertoire, image_sub_recal)).get_fdata()
        Image_recal_array[Image_recal_array == 2] = 10
        Image_recal_array[Image_recal_array != 10] = 0
        path_image_threshold = creation_chemin_nom_img_threshold(repertoire, image_sub_recal, "seg_L_only_x10")
        list_path_threshold.append(path_image_threshold)
        Image_recal_threshold = nib.Nifti1Image(Image_recal_array, affine=np.eye(4))
        nib.save(Image_recal_threshold, path_image_threshold)


    #Recuperation des images segmentés :

    repertoire_sujet_seg = r'/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor'
    nom_mask_sujet = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-brainmask_T2w.nii.gz'
    pattern = re.compile(nom_general_sujet)
    path_sujet_segment= [os.path.join(root, s)
                  for root, _, files in os.walk(all_sujets_path)
                  for s in files if pattern.match(s) and root == all_sujets_path]
    pattern_mask = re.compile(nom_mask_sujet)
    list_path_sujet_mask= [os.path.join(root, s)
                  for root, _, files in os.walk(all_sujets_path)
                  for s in files if pattern_mask.match(s)]
    list_path_img_segmente_rot = creation_PATH_pour_fichier_swaper(path_sujet_segment)
    swap_each_SUB(path_sujet_segment, list_path_img_segmente_rot)
    list_repertoire_segm_bin, list_image_sub_segm_bin =path_abs_sujet_to_fichier_repertorie_sujet(list_path_img_segmente_rot )

    for path_sujet_segm_rot, path_image_sub_binaryse, sujet, repertoire, mask_path in zip(list_path_img_segmente_rot, list_path_threshold,list_image_sub_segm_bin, list_repertoire_segm_bin,list_path_sujet_mask):
        Masque_sujet = ants.image_read(mask_path)
        Img_sujet_segmente = ants.image_read(path_sujet_segm_rot)
        Img_sujet_binarise = ants.image_read(path_image_sub_binaryse)
        Img_sujet_binarise_recal = Recalage_atlas(Img_sujet_segmente, Img_sujet_binarise,"Rigid",Masque_sujet)
        Img_sujet_segmente_array = Img_sujet_segmente.numpy()
        Img_sujet_segm_binar_combined_array = Img_sujet_segmente_array.copy()
        Img_sujet_binarise_recal_array = Img_sujet_binarise_recal.numpy()
        Img_sujet_segm_binar_combined_array = Img_sujet_segmente_array + Img_sujet_binarise_recal_array
        Img_sujet_segm_binar_combined = ants.from_numpy(Img_sujet_segm_binar_combined_array, origin=Img_sujet_segmente.origin, spacing=Img_sujet_segmente.spacing, direction=Img_sujet_segmente.direction)
        path_img_final = creation_chemin_nom_img_threshold(repertoire, sujet, "segmentation_LR")
        ants.image_write(Img_sujet_segm_binar_combined, path_img_final)







    fin = time.time()
    tps_excecution = fin - debut
    print(f"le temps d'exécution du programme est : {tps_excecution} secondes")



    # #SUB001
    # sujet_path = '/home/achalhi.k/Bureau/Lien vers 2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/'
    # sujet = "sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz"
    # recal_sujet_avc_bon_atlas_save(path_des_atlas,"STA25.nii.gz", sujet_path, sujet, nom_general_sujet_rot)


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

    #ECRIRE SUR FICHIER TEXTE TOUT LES PRINTS :
        #print("avant l'ecriture dans le fichier")
    #path_fichier = '/envau/work/meca/users/2024_Kamal/2024_stage_Kamal/outputKamalRECALAGESymilarity.txt'
    #output_directory = '/envau/work/meca/users/2024_Kamal/2024_stage_Kamal/'

       # if os.access(output_directory, os.W_OK ):
    #     print(("le repertoire est accessible pour lecrire"))
    # else:
    #     print("pas permis")
    # try :
    #     with open(path_fichier, 'w') as f:
    #         sys.stdout = f
            #CE QU'ON CHERCHE A ÉCRIRE

        #         sys.stdout = sys.__stdout__
    #         f.flush()
    #         print("apres fichier ecrit")
    # except IOError as e:
    #     print(f"erreur d'entree/sortie lors de l'écritute dans le fichier {e}")
    # except Exception as e:
    #     print(f"erreur  lors de l'écritute dans le fichier {e}")


    #ENREGRISTREMENT DE CERTAINS SUJET SWAPER ET RECALER:
    # #on enregistre Sub0009_rot_rec
    # atlas_30 = "STA30.nii.gz"
    # path_img = "/home/achalhi.k/Bureau/Lien vers 2024_Kamal/real_data/lastest_nesvor/sub-0009/ses-0012/haste/default_reconst/sub-0009_ses-0012_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz"
    # Atlas_30_ants = ants.image_read(os.path.join(path_des_atlas,atlas_30))
    # img_sub_0009 = ants.image_read(path_img)
    # img_sub_0009_recale = Recalage_atlas(Atlas_30_ants,img_sub_0009, "Affine")
    # img_0009_rec_name = "sub-0009_ses-0012_acq-haste_rec-nesvor_desc-aligned_T2w_rot_recaffine.nii.gz"
    # path_repertoir_sujet_009 = "/home/achalhi.k/Bureau/Lien vers 2024_Kamal/real_data/lastest_nesvor/sub-0009/ses-0012/haste/default_reconst"
    # Enregistrer_img_ants_en_nifit(img_sub_0009_recale,path_repertoir_sujet_009 ,img_0009_rec_name )
    #
    #
    #
    # atlas_28 = "STA28.nii.gz"
    # path_img = "/home/achalhi.k/Bureau/Lien vers 2024_Kamal/real_data/lastest_nesvor/sub-0019/ses-0022/haste/default_reconst/sub-0019_ses-0022_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz"
    # Atlas_28_ants = ants.image_read(os.path.join(path_des_atlas,atlas_28))
    # img_sub_0019 = ants.image_read(path_img)
    # img_sub_0019_recale = Recalage_atlas(Atlas_28_ants,img_sub_0019, "Affine")
    # img_0019_rec_name = "sub-0019_ses-0022_acq-haste_rec-nesvor_desc-aligned_T2w_rot_recaffine.nii.gz"
    # path_repertoir_sujet_019 = "/home/achalhi.k/Bureau/Lien vers 2024_Kamal/real_data/lastest_nesvor/sub-0019/ses-0022/haste/default_reconst"
    # Enregistrer_img_ants_en_nifit(img_sub_0019_recale,path_repertoir_sujet_019 ,img_0019_rec_name )


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