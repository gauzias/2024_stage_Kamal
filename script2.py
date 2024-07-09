"""
Application de la transformations de recalage inverse sur un atlas de segmentation d'hemisphère LR vers le sujet associès (dont il est le plus similaire)
"""
import os
import time
import numpy as np
import nibabel as nib
import ants
import tools as tls


def etape2(path_des_atlas_hemi_seg, list_atlas_meilleur,tab_path_sujet,list_tranf_inv,path_output_repertoire):
    """

    :param path_des_atlas_hemi_seg: Chemins des atlas segmenté par hemisphères RL
    :param list_atlas_meilleur: Listes des chemins pour chaque atlas mieux adaptés à un sujet données
    :param tab_img_sujet_rot: Listes des noms de chaques images de sujets anatomiques
    :param list_tranf_inv: Listes des chemins vers les transformations de recalage inverse obtenue entre chaque sujet et son meilleur atlas
    :param path_repertoire_sujet_rot: Listes chemin vers repertoire où on était sauvé les iamges de sujet anatomiques après "swaping" du script1
    :param path_output_repertoire: Chemin de sauvegarde des images après traitement réalisé par script2
    :return: AtlasLR_rec_dans_sub_space : Atlas segmenté LR recalé dans l'espace sujet associès
    """
    debut = time.time()
    #On cherche à recaler l'atlas sur l'image (une inversion du recalage), nous utilisons cette fois l'atlas binar
    #NOM des ATLAS Binairs
    tab_repertoire, tab_img_sujet = tls.path_abs_sujet_to_fichier_repertorie_sujet(tab_path_sujet)
    tls.creation_data_frame_sujet_by_best_atlas(tab_img_sujet, list_atlas_meilleur)
    les_atlas_binary = []
    list_num = tls.extraction_numero_atlas(list_atlas_meilleur)
    for num in list_num:
        les_atlas_binary.append(f'STA{num}_all_reg_LR_dilM.nii.gz')
    AtlasRL_rec_dans_sub_space= []  # liste des...
    for sujet, repertoire,  atlas_binar, warp in zip(tab_img_sujet,tab_repertoire, les_atlas_binary, list_tranf_inv):
        Sujet_fixe =ants.image_read(os.path.join(repertoire, sujet))
        Atlas_binary = ants.image_read(os.path.join(path_des_atlas_hemi_seg, atlas_binar))
        transfo =warp + '_Inverse_0GenericAffine.mat'
        print(transfo)
        Atlas_binary_warped = ants.apply_transforms(Sujet_fixe, Atlas_binary,  transformlist=transfo, interpolator="nearestNeighbor")
        print(type(Atlas_binary_warped))
        path_atlas_binary_warped = tls.creation_chemin_nom_img(path_output_repertoire, sujet, atlas_binar)
        AtlasRL_rec_dans_sub_space.append(path_atlas_binary_warped)
        ants.image_write(Atlas_binary_warped , path_atlas_binary_warped)
    fin = time.time()
    tps_excecution = fin - debut
    print(f"le temps d'exécution du programme est : {tps_excecution} secondes")
    return AtlasRL_rec_dans_sub_space


if __name__ == "__main__":
    nom_general_sujet = r'^sub-00\d+\_ses-00\d+\_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz'
    path_pattern = r'/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/sub-00\d+\/ses-00\d+\/haste/default_reconst'
    path_des_atlas_hemi_seg = r'/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas'
    path_variables = "/envau/work/meca/users/2024_Kamal/2024_stage_Kamal/variables"
    path_repertoire_sujet_rot = "/envau/work/meca/users/2024_Kamal/output/output_script1"
    path_output_repertoire = "/envau/work/meca/users/2024_Kamal/output/output_script2"
    list_atlas_meilleur = np.load(os.path.join(path_variables, "list_atlas_meilleur.npy"))
    tab_path_sujet = np.load(os.path.join(path_variables, "tab_path_sujet.npy"))
    list_tranf_direc =  np.load(os.path.join(path_variables, "list_tranf_direc.npy"))
    list_tranf_inv = np.load(os.path.join(path_variables, "list_tranf_inv.npy"))

    AtlasRL_rec_dans_sub_space = etape2(path_des_atlas_hemi_seg, list_atlas_meilleur, tab_path_sujet, list_tranf_inv, path_output_repertoire)
    np.save(os.path.join(path_variables, "AtlasRL_rec_dans_sub_space.npy"), AtlasRL_rec_dans_sub_space, allow_pickle='False')