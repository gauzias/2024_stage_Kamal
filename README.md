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
fusionnée des noms apres recalage et indiquer direction de recalage ex:  "Sub---------_to_STA--.nii.gz) )
        -fonction qui recale image sujet à une liste donnée d'atlas et qui estime la similarité
        -fonction qui cherche et retourne l'atlas qui maximise la similarité
        -fonction qui enregistre la transformé inverse de recalage dans un output choisis, retourne le path
        -fonction qui 'swap' et copie et enregistre les informations géometriques
        
script1 : -ce script permet de recuperer les images de nos sujets à partir d'un nom pattern (dont les numeros varient) qu'on lui donne en entrée,
d'un chemin pattern (dont le numéro varie selon le sujet). 
          - Je crée des chemins pour les images des sujets après transposition/basculement ("swap") 
          - Je "swap" et copies les informations géométriques de chacune de mes images sujets recupérés
            - Pour chacun de mes sujets, j'utilise la "fonction recalage par les atlas" de mon tools, 
            et je recupère en sortir dans des listes, l'atlas du bon âge, le path de chaque transformation inverse de recalage 

script2 :
script3 :
script4 :

#### dans le dossier variables il y a ..

## tutoriel
Pour appliquer le pieline à une image, suivre la procédure suivante:
- script1.py prend en entrée l'image anatomique d'un sujet dans l'espace du sujet et fait...