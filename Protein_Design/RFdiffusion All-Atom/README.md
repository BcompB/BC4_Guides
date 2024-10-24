# RFdiffusion All-Atom (AA) Guide 
Guide originally compiled by Ben Hardy (ben.hardy@bristol.ac.uk)

# 1. Install RFdiffusion all-atom in your work/scratch directory 
For this, you just need to follow steps 1-4 on the GitHub https://github.com/baker-laboratory/rf_diffusion_all_atom. Note: this will take a long time! The largest file (rf_se3_diffusion.sif) is about 13 GB and will take many hours to download. Just set this running and come back in a while...

# 2. Load "Singularity"
```
module load apps/singularity
```
You could also put this line in your submission script (see below) 

# 3. Create a submission script and run the test command from the GitHub 
An example submission script is in this folder. You’ll see that the command in the example submission script is slightly different than the one in the GitHub instructions. This is just because we are using Singularity instead of Apptainer to load all of the dependencies. 
```
--bind /user/work/$(whoami):/user/work/$(whoami) #- this allows Singularity to see the files in your current directory.
```
Sometimes Singularity still cannot find the “run_inference.py” script, so you will need to add the full directory to the path, e.g.: 
 ```
/user/work/{whoami)/RFdiffusion_aa/rf_diffusion_all_atom/run_inference.py 
```
# 4. Submit submission script to a GPU queue 
RFdiffusion-aa should generate backbones on the order of minutes. you need to make sure that you sbatch the scipt from the same exact directory that you have specified for your run_inference.py script. For all the options to change how RFdiffusion runs, see the instructions on both the RFdiffusion and RFdiffusion-aa githubs:
- https://github.com/baker-laboratory/rf_diffusion_all_atom  
- https://github.com/RosettaCommons/RFdiffusion

# Bonus Test Case: Diffusion proteins around the two hemes of 4D2 (PDB: 7AH0) 
1. Copy the 4D2 crystal structure into the inputs folder
2. Clean up the PDB by deleting all unneccessary lines (anything that's not protein e.g. CONNECT information)
3. Run the "submission_heme.sh" script

*Expected Outcomes*
Within your specified output folder, you should see your diffused PDBs (e.g. sample_0.pdb). These will contain the diffused backbone and your provided ligands, but will have no sequence information. This is the PDB you will then want to give to ProteinMPNN or LigandMPNN. You should also have two folders called “traj” and “unidealized”. 

If you would like to visualise the diffusion trajectory, then open either “sample_0_pX0_traj.pdb” or “sample_0_Xt-1_traj.pdb” in PyMol. 

By default, the states will contain the diffusion trajectory in reverse, so to re-order these in the correct order, run this command, replacing “object_name” with the name of your PDB: 
```
cmd.set_state_order('object_name', range(20, 0, -1))
```
