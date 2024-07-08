# code développé par Kamal durant son stage en 2024

## installation
### cloner le repos

### installer un environnement virtuel
module load all anaconda
conda create --name stage_Kamal python=3.8
conda activate stage_Kamal
pip install antspyx

## organisation du repos
### dans le dossier code il y a ...
tools : Ce fichier python contient toutes les fonctions que j'utilise lors des diffèrentes étapes de la pipeline:
        -Fonction de récuperéation de fichier selon pattern
        -fonction de création de chemin(récupère le path d'entrée et  modifie le nom du fichier 
pour qu'il puisse être adapté au processus qui a été utilisé (ajout de ROT pour fichier après 'swap', 
fusionnée des noms apres recalage et indiquer direction de recalage ex:  "sub-0002_ses-0002_acq-haste_rec-nesvor_desc-aligned_T2w_rot_STA21_all_reg_LR_dilM.nii.gz") )
        -fonction qui recale image sujet à une liste donnée d'atlas et qui estime la similarité
        -fonction qui cherche et retourne l'atlas qui maximise la similarité
        -fonction qui enregistre la transformé inverse de recalage dans un output choisis, retourne le path
        -fonction qui 'swap' et copie et enregistre les informations géometriques
        
script1 : 
-ce script permet de recuperer les images de nos sujets à partir d'un nom pattern (dont les numeros varient) qu'on lui donne en entrée,
d'un chemin pattern (dont le numéro varie selon le sujet). 
          - Je crée des chemins pour les images des sujets après transposition/basculement ("swap") 
          - Je "swap" et copies les informations géométriques de chacune de mes images sujets recupérés
          - Pour chacun de mes sujets, j'utilise la "fonction recalage par les atlas" de mon tools, 
            et je recupère en sortir dans des listes, l'atlas du bon âge, le path de chaque transformation inverse de recalage 

script2 :
Ce script charge les sorties du 1er script, il récupère les atlas binarisés correspondant aux atlas déterminés prcédemment. 
Sur une boucle, il applique les transformations inverses obtenues dans le script1 du sujet vers l'atlas, obtenant donc le sens inverse, 
et l'applique sur les atlas binaires vers le sujet correspondant. Il crée ensuite un chemin adaptés vers une sortie et un nom d'image adaptés

script3 : 
Ce script récupère les chemins vers les atlas binaire recalés dans l'espace sujet et réalise un seuillage de manière à amplifiés (x5) l'hemisphère gauche et annulés les pixels de l'hemisphères droit.
Et sauve ensuite les chemins des images d'hemisphère gauche avec un nom adaptés (ex : "sub-0001_ses-0001_acq-haste_rec-nesvor_desc-aligned_T2w_rot_STA25_all_reg_LR_dilM_seg_L_only_x10.nii.gz")

script4 : 
Ce script récupère les chemins des images des hemisphères gauches, et récupère également images de sujet segmentés (dans ce cas-ci, les sujets segmentés et anatomiques ont les mêmes noms mais des chemins diffèrents),
un swaping est réalisés sur les sujets segmentés avant d'aditionner chaques images aux masques d'hémisphères gauches récupérés


#### Le dossier variables contient des listes de chemins de fichiers sauvés, notamment : 
-Ceux des sujets anatomiques que l'on a transposés et inversés selon certains axes (swaping).
-Ceux des atlas d'âge adaptés pour chaque sujets mis en entrée dans le script1.
-Ceux des transformations direct et inverse obtenue dans le scripts1 entre chaque sujet vers son atlas d'âge adaptés.
-Ceux des atlas binarisés projetés vers l'espace sujet par le script2 en utilisant les transformations inverse récupérées.
-Ceux des hemisphères gauches obtenues dans l'espace sujet.(Script3)


## tutoriel
Pour appliquer le pipeline à une image, suivre la procédure suivante:
- script1.py prend en entrée l'image anatomique d'un sujet dans l'espace du sujet et fait...