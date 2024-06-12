import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt 
import nibabel as nib
import nisnap
#Conversion d'image nifti en numpy array en 3d
input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w = nib.load(r"/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w.nii.gz")
sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w = input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w.get_fdata()

# On swap l'image
sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot = np.transpose(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w, (0,1,2))[::-1, :, ::-1]

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
# plt.figure(1)
# plt.subplot(1,2,1)
# plt.imshow(tranche_z)
# plt.title("tranche z image origin")
# plt.subplot(1,2,2)
# plt.imshow(tranche_z_rot)
# plt.title("tranche z rot image origin")
# plt.show()
#
# plt.figure(2)
# plt.subplot(1,2,1)
# plt.imshow(tranche_y)
# plt.title("tranche y image origin")
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
Sub_0001_template_masked_rot_conv = np.array(sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot, dtype = np.float32)
affine = np.eye(4)
Sub_0001_template_masked_rot_nifti = nib.Nifti1Image(Sub_0001_template_masked_rot_conv, affine)


# Copier l'affine matrix et le header du fichier source vers le fichier cible
affine_source = input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w.affine
Sub_0001_template_masked_rot_nifti.set_sform(affine_source)
Sub_0001_template_masked_rot_nifti.set_qform(affine_source)
for key, value in input_sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w.header.items():
    Sub_0001_template_masked_rot_nifti.header[key] = value


# Enregistrer l'image NIfTI
path_pour_fichier_rot = "/envau/work/meca/users/2024_Kamal/real_data/lastest_nesvor/sub-0001/ses-0001/haste/default_reconst/sub_0001_ses_0001_acq_haste_rec_nesvor_desc_aligned_T2w_rot.nii.gz"
nib.save(Sub_0001_template_masked_rot_nifti, path_pour_fichier_rot)
