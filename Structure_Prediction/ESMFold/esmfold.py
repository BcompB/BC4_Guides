# Script to run ESMFold on the cluster.
# author Holly Ford, h.ford@bristol.ac.uk

import sys
import torch
import esm

# You need to make a directory in your scratch space for torch hub to reside
# In your scratch space, make a directory .cache/torch/hub
# Paste the path to this directory into the command below
torch.hub.set_dir("/path/to/your/scratch/.cache/torch/hub")

def esmfold(fasta_file):
    with open(fasta_file, "r") as seqs:
        model = esm.pretrained.esmfold_v1()
        model = model.eval().cuda()

        # Optionally, uncomment to set a chunk size for axial attention. This can help reduce memory.
        # Lower sizes will have lower memory requirements at the cost of increased speed.
        # model.set_chunk_size(128)


        # reads a fasta file into an array
        seqs_array = []
        for element in seqs:
            seqs_array.append(str(element))

        # appends sequences to a sequence array
        clean_seq_array=[]
        for i in range(len(seqs_array)):
            if i % 2:
                clean_seq_array.append(seqs_array[i])

        # appends names to a names array
        clean_name_array=[]
        for i in range(len(seqs_array)):
            if seqs_array[i] not in clean_seq_array:
                clean_name_array.append(seqs_array[i])

        # tidies up the name array
        clean_name_array_final=[]
        for name in clean_name_array:
            clean_name_array_final.append(name[1:-1])

        # tidies up the seq array - to remove hemes and anything else that follows the hemes
        clean_seq_array_final=[]
        for seq in clean_seq_array:
            processed_seq = seq.split('X')[0]
            clean_seq_array_final.append(processed_seq)

        # Multimer prediction can be done with chains separated by ':'

        #defines a function to infer and write a pdb file
        def infer_and_write_result(seq, model, output_file):
            with torch.no_grad():
                output = model.infer_pdb(seq)
            with open(output_file, "w") as f:
                f.write(output)

        #loops though the arrays
        for seq, name, in zip(clean_seq_array_final, clean_name_array_final):
            output_file = f"{name}.pdb"
            infer_and_write_result(seq, model, output_file)

        import biotite.structure.io as bsio
        struct = bsio.load_structure("result.pdb", extra_fields=["b_factor"])
        print(struct.b_factor.mean())  # this will be the pLDDT
        # 88.3
        pass
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <fasta_file>")
        sys.exit(1)
        
    fasta_file = sys.argv[1]
    esmfold(fasta_file)
