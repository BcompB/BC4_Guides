#!/bin/bash
#SBATCH --nodes=1
#SBATCH -p gpu_veryshort
#SBATCH --gres=gpu:1
#SBATCH --time=06:00:00
#SBATCH --mem=50GB
#SBATCH --output=RFdiffusion_test
#SBATCH --account={HPC_code}

singularity run --bind /user/work/$(whoami):/user/work/$(whoami) --nv rf_se3_diffusion.sif run_inference.py inference.deterministic=True diffuser.T=100 inference.output_prefix=output/heme/sample inference.input_pdb=input/7ah0_clean.pdb contigmap.contigs=[\'200-200\'] inference.ligand=HEM inference.num_designs=4 inference.design_startnum=0
