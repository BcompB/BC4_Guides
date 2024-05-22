#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --job-name=LigMPNN
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=06:00:00
#SBATCH --mem=50GB
#SBATCH --account={account}

python run.py \
	--model_type "ligand_mpnn" \
	--pdb_path "./inputs/{input}.pdb" \
	--out_folder "./outputs/" \
	--redesigned_residues "A60 A62 A63 A66 A70 A100 A101 A104 A108 A126 A128 A129 A132 A136N A167" \
	--omit_AA "HC" \
