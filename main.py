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
if __name__ == "__main__":
    #Conversion d'image nifti en numpy array en 3d
    input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w = nib.load('/home/achalhi.k/Bureau/Lien vers 2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz')
    sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w = input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w.get_fdata()
    #print(type(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w[1,1,1]))

    # On swap l'image
    sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot = np.transpose(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w, (0,1,2))[::-1,::1,::-1]

    #dimension de l'image
    #dim_sub_0001 = np.shape(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot)
    #print("lesexport dimensions de notre image :", dim_sub_0001)
    #On selectionne plusieurs tranche de cette objet 3d pour en affiche le swapping
    # tranche z = 74
    # tranche_z = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w[:, :, 74]
    # tranche_z_rot = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot[:, :, 74]
    # #tranche y = 74
    # tranche_y = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w[:, 74, :]
    # tranche_y_rot = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot[:, 74, :]
    # #tranche x = 74
    # tranche_x = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w[74,:,:]
    # tranche_x_rot = sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot[74,:,:]

    #Affichage
    # plt.figure(1)
    # plt.subplot(1,2,1)
    # plt.imshow(tranche_z, cmap='gray')
    # plt.title("tranche z image origin")
    # plt.subplot(1,2,2)
    # plt.imshow(tranche_z_rot, cmap='bone')
    # plt.title("tranche z rot image origin")
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
    #print(input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w.header)
    #print(Sub_0001_template_masked_rot_nifti.header)


    # Enregistrer l'image NIfTI
    path_pour_fichier_rot = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz"
    nib.save(Sub_0001_template_masked_rot_nifti, path_pour_fichier_rot)




    #sub_2_temp_ro_r = ants.registration(fixed=fi, moving=img_sub_aligned_rot_ants, type_of_transform = 'SyN' )


    #Parcours d'un dossier pour trouver le bon atlas du bon(du bon âge), il faut un critère qu'on cherche à minimiser

    # nii.gz image conversion pour ants :
    img_path = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot.nii.gz"
    img_sub_aligned_ants = ants.image_read(img_path)
    def Parcours_dossier_only_data_match(Path, nom_caracteristic : str):
        files = os.listdir(Path)
        files_atlas = list()
        Pattern = re.compile(nom_caracteristic)
        for f in files:
            if Pattern.match(f):
                files_atlas.append(f)
        files_atlas.sort()
        return files_atlas

    Nom_caract = r'^STA\d+\.nii.gz'
    path_des_atlas = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2"
    files_atlas = Parcours_dossier_only_data_match(path_des_atlas, Nom_caract)
    def SWAP_COPY_INFO_SAVE(img_input, path_img_rot_nifti):
        img_input_array = nib.load(os.path.abspath(img_input)).get_fdata()  #trouver path,charger image nifti,conversion en array numpy
        img_input_array_rot = np.transpose(img_input_array, (0, 1, 2))[::-1, ::1, ::-1] # x et z ont une transposé inverse et y une transposé
        img_input_rot_nifti = nib.Nifti1Image(img_input_array_rot, nib.load(os.path.abspath(img_input)).affine, nib.load(os.path.abspath(img_input)).header)
        nib.save(img_input_rot_nifti, path_img_rot_nifti)
    print(files_atlas)
    print(len(files_atlas))

    def calcul_similarity_ants(img1, img2, critere):
        similarite = ants.image_similarity(img1, img2, metric_type=critere)
        return similarite
    def Recalage_atlas_rigid(img_fix, atlas_mouv):

        Warp_atlas = ants.registration(img_fix, atlas_mouv, type_of_transform ='Rigid')
        Atlas_Warped = ants.apply_transforms(img_fix,atlas_mouv, transformlist=Warp_atlas['fwdtransforms'],whichtoinvert=None)
        return Atlas_Warped
    # img_sub_aligned_ants2 = img_sub_aligned_ants.copy()
    # sim_lui_meme = ants.image_similarity(img_sub_aligned_ants, img_sub_aligned_ants2 ,sampling_strategy='regular',  metric_type='MattesMutualInformation', sampling_percentage=1.)
    # print(sim_lui_meme)
    criteres = ['MeanSquares', 'MattesMutualInformation', 'Correlation']
    simlarity= 0

    tableau_criteres_by_atlas = pd.DataFrame(index=files_atlas, columns=criteres)
    # for atlas in files_atlas:
    #    Atlas_rchrche = ants.image_read(os.path.join(path_des_atlas,atlas))
    #    Atlas_Warped = Recalage_atlas_rigid(img_sub_aligned_ants, Atlas_rchrche)
    #    for critere in criteres:
    #       similarity = calcul_similarity_ants(img_sub_aligned_ants, Atlas_Warped, critere)
    #       tableau_criteres_by_atlas.loc[atlas, critere] = similarity
    # print(tableau_criteres_by_atlas)

    #Fonction pour recaler sta34 à notre sujet 0001


    Atlas_35 = ants.image_read(os.path.join(path_des_atlas,"STA34.nii.gz"))

    SWAP_COPY_INFO_SAVE(os.path.join(path_des_atlas,"STA35.nii.gz"), "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2/STA34_rot.nii.gz")
    Atlas_35_ROT = ants.image_read(os.path.join(path_des_atlas,"STA34_rot.nii.gz"))
    plt.imshow(Atlas_35[60,:,:])
    plt.show()
    plt.imshow(Atlas_35_ROT[60,:,:])
    plt.show()
    Warped_atlas = Recalage_atlas_rigid(img_sub_aligned_ants, Atlas_35_ROT)
    plt.imshow(Warped_atlas[60,:,:])
    plt.show()
    path_fct_rigid_recalage = "/envau/work/meca/users/2024_Kamal/Sym_Hemi_atlas/Fetal_atlas_gholipour/T2/STA34_ROT_RECpy.nii.gz"
    nib.save(Warped_atlas,path_fct_rigid_recalage)
