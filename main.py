import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt 
import nibabel as nib
import nisnap
import ants
import os

import glob

if __name__ == "__main__":
    #Conversion d'image nifti en numpy array en 3d
    input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w = nib.load('/home/achalhi.k/Bureau/Lien vers 2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz')
    sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w = input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w.get_fdata()
    print(type(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w[1,1,1]))

    # On swap l'image
    sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot = np.transpose(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w, (0,1,2))[::-1,::1,::-1]

    #dimension de l'image
    dim_sub_0001 = np.shape(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot)
    print("lesexport dimensions de notre image :", dim_sub_0001)
    #On selectionne plusieurs tranche de cette objet 3d pour en affiche le swapping
    # tranche z = 74
    tranche_z = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w[:, :, 74]
    tranche_z_rot = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot[:, :, 74]
    #tranche y = 74
    tranche_y = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w[:, 74, :]
    tranche_y_rot = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot[:, 74, :]
    #tranche x = 74
    tranche_x = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w[74,:,:]
    tranche_x_rot = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot[74,:,:]

    #Affichage
    plt.figure(1)
    plt.subplot(1,2,1)
    plt.imshow(tranche_z, cmap='gray')
    plt.title("tranche z image origin")
    plt.subplot(1,2,2)
    plt.imshow(tranche_z_rot, cmap='bone')
    plt.title("tranche z rot image origin")
    #plt.show()
    #
    # plt.figure(2)
    # plt.subplot(1,2,1)
    # plt.imshow(tranche_y)
    # plt.subplot(1,2,2)
    # plt.imshow(tranche_y_rot)
    # plt.title("tranche y rot image origin")
    # plt.show()
    #
    # plt.figure(3)
    # plt.subplot(1,2,1)
    # plt.imshow(tranche_x)
    # plt.title("tranche x  image origin")
    # plt.subplot(1,2,2)
    # plt.imshow(tranche_x_rot)
    # plt.title("tranche x rot image origin")
    # plt.show()


    #Copie des informaations géométrique / Fslcpgeom
    #Conversion de np array vers fichier nifti
    #Sub_0001_template_masked_rot_nifti = np.array(, dtype = np.float64)
    #Sub_0001_template_masked_rot_nifti

    #Copier l'affine matrix et le header du fichier source vers le fichier cible
    # affine = np.eye(4)
    affine_source = input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w.affine
    header_source = input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w.header
    Sub_0001_template_masked_rot_nifti = nib.Nifti1Image(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot,affine=affine_source, header = header_source )
    print(input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w.header)
    print(Sub_0001_template_masked_rot_nifti.header)


    # Enregistrer l'image NIfTI
    path_pour_fichier_rot = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot.nii.gz"
    nib.save(Sub_0001_template_masked_rot_nifti, path_pour_fichier_rot)

    #ON cacule grace à ants registration le WARP SYN nécessaire pour recaler une image A à image B
    #nii.gz image conversion pour ants :
    img_path = os.path.join("/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/", "sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot.nii.gz")
    img_sub_aligned_rot_ants = ants.image_read(img_path)

    #sub_2_temp_ro_r = ants.registration(fixed=fi, moving=img_sub_aligned_rot_ants, type_of_transform = 'SyN' )


    #Parcours d'un dossier pour trouver le bon atlas du bon(du bon âge), il faut un critère qu'on cherche à minimiser

    path_des_atlas = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/"
    files = os.listdir(path_des_atlas)
    files_atlas = list()
    for f in files:
        if "_all_reg_LR_dilM.nii.gz" in f:
            files_atlas.append(f)
    files_atlas.sort()
    print(files_atlas)
    print(len(files_atlas))


    max_similarite = -float('inf')
    path_atlas_adapte = ""
    for atlas in files_atlas:
        Atlas_rchrche =ants.image_read(os.path.abspath(atlas))
        similarite = ants.image_similarity(img_sub_aligned_rot_ants, Atlas_rchrche)
        if similarite > max_similarite:
            max_similarite = similarite
            path_atlas_adapte = os.path.abspath(atlas)
    print(" similarité entre l'atlas adapté et l'image du sujet : ", max_similarite)
    print("chemin vers l'atlas adapté:", path_atlas_adapte)
