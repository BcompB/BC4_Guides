# ESMFold 
How to perform ESMFold on a fasta input file on BC4

# What is ESMFold?
Architecture consists of ESM-2 language model trained using a masking pipeline, learning amino acid dependcies and evolutioanry patterns by hiding residues and using the remaining sequence to guess what goes where. This is fed into a folding head, using sequence and pairwise representations in structure preduction. High confidence outputs have low RMSD compared to experimentally determined structures, but in general is less successful than MSA-based methods like AlphaFold or RoseTTAFold. Benefits arise from success in predicting structure of *de novo* proteins (where MSAs are often redundant), low computational requirements, and extreme speed of predictions. 

# How to run ESMFold 
ESMFold is ran very eaily, just requiring a python script and the right module loaded, hence can all be performed in a single script:
```
#!/bin/bash 
#SBATCH --nodes=1 
#SBATCH -p gpu 
#SBATCH --gres=gpu:1 
#SBATCH --time=3-00:00:00 
#SBATCH --mem=50GB 
#SBATCH --output=esmfold.out 
#SBATCH --account={account}
 
module purge 
module load libs/fair-esm/2.0.0-python3.9.5 
date 
python /path/to/esmfold.py /path/to/formatted_fasta_file.fa 
date
```
The two python scripts above differ slightly, with the esmfold_batch_scores_plots.py script having the additional .json output for each structure prediction (more below). In our lab, where Protein/LigandMPNN use is rampant, we often feed the outputted fasta file into ESMFold. These files need slight formatting before being able to be read by ESMFold (removing spaces and unrecognised characters). This can be run using the sed command:
```
sed -e 's/[^A-Za-z0-9._>-]/_/g' -e 's/\./-/g' name_of_pdb_file_sorted.fa > name_of_pdb_file_final.fa
```

# Expected Outcomes
If you have used the esmfold_batch_scores_plots.py script as an input, we can extrude the PAE, pLDDT and pTM for each output. Briefly, the Predicted Aligned Error (PAE) is a pairwise assessment of confidence, expecially useful when predicting dimers or multidomain structures. The predicted local distance difference test (pLDDT) is a per-residue assessment of structure confidence, and the predicted TM (pTM) is a global metric on confidence. These scores are collated into the pTM_pLDDT_report.dat file, whereby the pLDDT is an average across each residue. The .json file has the per-residue pLDDT and PAE scores which can be plotted. To plot the data for each of the output .json, copy the contents of PAE_pLDDT_plotting.py into a Jupyter Notebook and follow the instructions. 
