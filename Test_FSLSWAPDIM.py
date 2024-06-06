import subprocess
import fsl
import fsl.data.image as fslimage
import os

path_image = r'C:\Users\achalhi.k\2024_stage_Kamal\ds005072\sub-01\anat\sub-01_run-2_T1w.nii.gz'

if not os.path.exists(path_image):
    print(f"The file {path_image} does not exist.")
else:
    try:
        # Try to load the image
        input_image = fslimage.Image(path_image)
        print("dimension de l'image : ", input_image.shape)

        # Change the dimension of the image
        input_image = input_image.swapdims('y', 'x' , 'z')
        print("dimension de l'image après redimensionnement : ", input_image.shape)

        # Save the modified image
        input_image.save(r'\Users\achalhi.k\2024_stage_Kamal\ds005072\sub-01\func\image_redimensionne1.nii.gz')

        print("dimension de l'image après redimensionnement enregistré : ", input_image.shape)
    except Exception as e:
        print(f"An error occurred: {e}")
