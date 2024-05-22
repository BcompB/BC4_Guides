#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=cpu
#SBATCH --time=1:00:00
#SBATCH --mem=10000M
#SBATCH --output={job_name}
#SBATCH --account={HPC_account}
#################
source activate mlfold
#################
folder_with_pdbs="inputs/"
#################
output_dir="outputs/"
if [ ! -d $output_dir ]
then
    mkdir -p $output_dir
fi
#################
path_for_parsed_chains=$output_dir"/parsed_pdbs.jsonl"
path_for_assigned_chains=$output_dir"/assigned_pdbs.jsonl"
path_for_fixed_positions=$output_dir"/fixed_pdbs.jsonl"
#################
#Adding global polar amino acid bias or removing amino acids (Doug Tische­r) Edit appropriatetely, 0 will remove an amino acid. 
AA_list="HC"
#################
chains_to_design="A"
#The first amino acid in the chain corresponds to 1 and not PDB residues index for now.
fixed_positions="15 19 36 40 77 94 95" #fixing/not designing residues 1 2 3...25 in chain A
#################
python /mnt/storage/software/apps/ProteinMPNN/helper_scripts/parse_multiple_chains.py --input_path=$folder_with_pdbs --output_path=$path_for_parsed_chains
python /mnt/storage/software/apps/ProteinMPNN/helper_scripts/assign_fixed_chains.py --input_path=$path_for_parsed_chains --output_path=$path_for_assigned_chains --chain_list "$chains_to_design"
python /mnt/storage/software/apps/ProteinMPNN//helper_scripts/make_fixed_positions_dict.py --input_path=$path_for_parsed_chains --output_path=$path_for_fixed_positions --chain_list "$chains_to_design" --position_list "$fixed_positions"
#################
python /mnt/storage/software/apps/ProteinMPNN/protein_mpnn_run.py \
        --jsonl_path $path_for_parsed_chains \
        --chain_id_jsonl $path_for_assigned_chains \
        --fixed_positions_jsonl $path_for_fixed_positions \
        --bias_by_res_jsonl {pdb_name}_bias.json \
        --out_folder $output_dir \
        --omit_AAs $AA_list \
        --num_seq_per_target 25 \
        --sampling_temp "0.1" \
        --seed 37 \
        --batch_size 1

