#!/bin/bash
#SBATCH --nodes=1
#SBATCH -p gpu_veryshort
#SBATCH --gres=gpu:1
#SBATCH --time=06:00:00
#SBATCH --mem=50GB
#SBATCH --output=RFdiffusion_test
#SBATCH --account={HPC_code}

singularity run --bind /user/work/$(whoami):/user/work/$(whoami) --nv rf_se3_diffusion.sif run_inference.py inference.deterministic=True diffuser.T=100 inference.output_prefix=output/ligand_only/sample inference.input_pdb=input/7v11.pdb contigmap.contigs=[\'150-150\'] inference.ligand=OQO inference.num_designs=1 inference.design_startnum=0
