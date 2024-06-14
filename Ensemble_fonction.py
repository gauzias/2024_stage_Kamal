import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import nibabel as nib
import nisnap
import ants
import os
import glob
import re

def SWAP_COPY_INFO_SAVE(img_input, path_img_rot_nifti):
    img_input_array = nib.load(os.path.abspath(img_input)).get_fdata()  #trouver path,charger image nifti,conversion en array numpy
    img_input_array_rot = np.transpose(img_input_array, (0, 1, 2))[::-1, ::1, ::-1] # x et z ont une transposé inverse et y une transposé
    img_input_rot_nifti = nib.Nifti1Image(img_input_array_rot, nib.load(os.path.abspath(img_input)).affine, nib.load(os.path.abspath(img_input)).header)

    nib.save(img_input_rot_nifti, path_img_rot_nifti)
def Parcours_dossier_only_data_match(Path, nom_caracteristic : str):
    files = os.listdir(Path)
    files_atlas = list()
    Pattern = re.compile(nom_caracteristic)
    for f in files:
        if Pattern.match(f):
            files_atlas.append(f)
    files_atlas.sort()
    return files_atlas

def calcul_similarity_ants(img1, img2, critere):
    similarite = ants.image_similarity(img1, img2, metric_type=critere)
    return similarite
def Recalage_atlas_rigid(img_fix, atlas_mouv):
    atlas_mouv_reshap = ants.resample_image_to_target(img_fix, atlas_mouv)
    Warp_atlas = ants.registration(img_fix, atlas_mouv_reshap, 'Rigid')
    Atlas_Warped = ants.apply_transforms(img_fix,atlas_mouv_reshap , transformlist=Warp_atlas['fwdtransforms'][0])
    return Atlas_Warped





if __name__ == "__main__":
    print("repertoire_courant: ",os.getcwd())
    #os.chdir('')
    img_in = "real_data/lastest_nesvor/sub-0009/ses-0012/haste/default_reconst/sub-0009_ses-0012_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz"
    nom_initial, ajout = os.path.splitext(os.path.basename(os.path.abspath(img_in))) #On ajoute au nom de l'image original un suffixe
    img_out = os.path.join(os.path.dirname(os.path.abspath(img_in)), f"{nom_initial}_rot.nii.gz")
    SWAP_COPY_INFO_SAVE(img_in, img_out)
