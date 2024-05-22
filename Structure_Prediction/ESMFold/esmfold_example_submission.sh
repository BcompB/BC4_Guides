#!/bin/bash
#SBATCH --nodes=1
#SBATCH -p gpu_veryshort
#SBATCH --gres=gpu:1
#SBATCH --time=0-06:00:00
#SBATCH --mem=50GB
#SBATCH --output={name}
#SBATCH --account={code}
module purge
module load libs/fair-esm/2.0.0-python3.9.5

date
python esmfold_batch_scores_plots_ext.py big_fasta_clean.fa
date
