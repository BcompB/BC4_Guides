import argparse

def main(args):
    import glob
    import random
    import numpy as np
    import json
    
    mpnn_alphabet = 'ACDEFGHIKLMNPQRSTVWYX'
    
    mpnn_alphabet_dict = {'A': 0,'C': 1,'D': 2,'E': 3,'F': 4,'G': 5,'H': 6,'I': 7,'K': 8,'L': 9,'M': 10,'N': 11,'P': 12,'Q': 13,'R': 14,'S': 15,'T': 16,'V': 17,'W': 18,'Y': 19,'X': 20}
     
    with open(args.input_path, 'r') as json_file:
        json_list = list(json_file)   
 
    my_dict = {}
    for json_str in json_list:
        result = json.loads(json_str)
        all_chain_list = [item[-1:] for item in list(result) if item[:10]=='seq_chain_']
        bias_by_res_dict = {}
        for chain in all_chain_list:
            chain_length = len(result[f'seq_chain_{chain}'])
            bias_per_residue = np.zeros([chain_length, 21])


            if chain == 'A':
                residues = [3, 7, 13, 14, 21, 24, 25, 27, 31, 34, 35, 42, 49, 52, 53, 54, 57, 61, 64, 65, 72, 78, 79, 81, 82, 83, 84, 85, 88, 89, 93, 95, 99, 100, 106, 107] #surface no loops
                amino_acids = [0, 13, 3, 14, 8] #[A,Q,E,R,K]
                for res in residues:
                    for aa in amino_acids:
                        bias_per_residue[res, aa] = 2.0

            if chain == 'A':
                residues = [25, 26, 27, 28, 29, 52, 53, 54, 55, 56, 57, 58, 59, 83, 84, 85, 86, 87] #loops
                amino_acids = [0, 13, 3, 14, 8, 5, 15, 16, 2, 12] #[A,Q,E,R,K,G,S,T,D,P]
                for res in residues:
                    for aa in amino_acids:
                        bias_per_residue[res, aa] = 2.0



            bias_by_res_dict[chain] = bias_per_residue.tolist()
        my_dict[result['name']] = bias_by_res_dict

    with open(args.output_path, 'w') as f:
        f.write(json.dumps(my_dict) + '\n')


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument("--input_path", type=str, help="Path to the parsed PDBs")
    argparser.add_argument("--output_path", type=str, help="Path to the output dictionary")

    args = argparser.parse_args()
    main(args) 
