# LigandMPNN
Updated version of ProteinMPNN, now with new model types that permit ligand awareness in the structure diversitifcation, as well as specifiying soluble or membranous designs. The code and instructions can be found at the following page: https://github.com/dauparas/LigandMPNN. There are no specific modules installed on BC4 required for this to run, its a simple github clone and depencies download, so it can be installed on any local machine or cluster. 

# How to install LigandMPNN
1. Clone the LigandMPNN github to your desired location
```
git clone https://github.com/dauparas/LigandMPNN.git
```
2. This creates a LigandMPNN directory, so you'll need to head into there to download the model weights:
```
cd LigandMPNN
bash get_model_params.sh "./model_params" 
```
# Running LigandMPNN
3. Load the required depencies. The environment is already availble to access on BC4
```
module add languages/miniconda/3.9.7
source activate ligandmpnn_env
```
If you're installing this elsewhere, create a conda/other environment and install the requirements:
```
#conda create -n ligandmpnn_env python=3.11
#pip3 install -r requirements.txt
```
4. Create a slurm submission script according to the examples available on the LigandMPNN github or above here. Ensure you have the correct PDB input path, and that the PDB has chain information. 

# Key information on the submission scripts
*model_type*
This updated version can run original ProteinMPNN, LigandMPNN, SolubleMPNN, ProteinMPNN with global membrane label, proteinMPNN with per residue membrane label, and a sidechain packing model. This last is the most exciting, allowing an all-atom structure prediction of the outputs, powered by OpenFold. If you'd want a folded output, ensure you have the checkpoint in your submission script:
```
--checkpoint_path_sc "./model_params/ligandmpnn_sc_v_32_002_16.pt"
```
Each model has a parameter checkpoint you can add with the submission script, each differing with a different level of Gaussian noise. As seen in ProteinMPNN, sequence recovery is inversely proportional to the amount of Gaussain noise added to the input coordinates.

# Expected Outcomes 
Inside your output directory, there will be a 'seqs' and 'backbone' folder. Inside 'seqs' will be a fasta file with the sequences, seed, and scores. The scores differ from original ProteinMPNN, as the higher the score, the higher the confidence. The entire .fa file can be fed into folding architecture (i.e. ESMFold) if scrubbed using the command:
```
sed -e 's/\//:/g' -e 's/[^A-Za-z0-9._>:-]/_/g' -e 's/\./-/g'
```
Quick note: if you're running a PDB input that has covalent ligands or non-natural amino acids, these will be omitted from the output fasta file. To add a residue back into place, use the sed command:
```
sed -i '0~2s/.\{8\}/&C/' #adds a 'C' residue in the **9th** position (Position in command = n-1) on every other line
```
The backbone folder simply has a stripped backbone for each output. There is little information to be obtained from these. 

If you ran a sidechain packing command, there will also be a 'packed' directory, with your all-atom PDB output file. As seen in the original github, there a few parameters on the number of packings, and repack everything option. This code is relatively new so I'll need to update this readme when I have a better understanding of these parameters. 
