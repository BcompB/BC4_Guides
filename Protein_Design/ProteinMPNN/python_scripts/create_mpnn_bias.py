# Python script to generate a bias json for use with MPNN.
# author Tim Neary, tim.neary@@bristol.ac.uk

import json
import logging
import string
from pathlib import Path
from typing import Any, Dict, Iterable, List, NamedTuple, Tuple

import numpy as np
import numpy.typing as npt

_1_LETTER_CODES = list("ACDEFGHIKLMNPQRSTVWY-")
_3_LETTER_CODES = [
    "ALA",
    "CYS",
    "ASP",
    "GLU",
    "PHE",
    "GLY",
    "HIS",
    "ILE",
    "LYS",
    "LEU",
    "MET",
    "ASN",
    "PRO",
    "GLN",
    "ARG",
    "SER",
    "THR",
    "VAL",
    "TRP",
    "TYR",
    "GAP",
]

_3_TO_1 = {three: one for three, one in zip(_3_LETTER_CODES, _1_LETTER_CODES)}


class ResidueBias(NamedTuple):
    selection: Dict[str, npt.NDArray[np.bool_]]
    bias: npt.NDArray[np.floating]


def print_example() -> str:
    """Prints example bias command script."""
    return """
# This is a comment, any test after a "#" is considered as a comment.
# Residue selections may be over multiple lines.
# Each selection must end with a ";".

# The following is an example residue selection

# For residues with index 1-100, increase the bias of Alanine, Glycine, Tyrosine
# and Cysteine by 100 and reduce the bias of Tryptophan and Phenylalanine by 20.5.
select idx 1-100 res AGYC:100.,WF:-20.5;

# You can select multiple set of indices with comma separated values.
# The following selects residues 1-50, 134 and 55-100.
select idx 1-50,134,55-100 res H:2;

# You can include the chain when selecting index values with the following.
# Which will only fix the 
select idx A1-100 res AGYC:100.,WF:-20.5;

# This works for each index value as well.
select idx A5-10,B10-20 Y:4;


# Select all Glycine residues and increase their bias to Alanine by 10.
select name GLY,ALA res A:10;

# Select all non Cysteine residues and increase their bias to Cysteine by 220.5.
select name !CYS res C:220.5;
""".strip()


def strip_comments(contents: str) -> str:
    """Strips comments from the contents of a command file."""
    lines = contents.splitlines(keepends=False)
    return " ".join(l.split("#")[0] for l in lines)


def _to_one_letter_code(three_or_one: str) -> str:
    """Converts a 1 or 3 letter code to its corresponding 1 letter code."""
    n_chars = len(three_or_one)
    if n_chars != 1 and n_chars != 3:
        raise KeyError("Must provide a 1 or 3 letter amino acid code.")
    elif n_chars == 3 and three_or_one not in _3_TO_1:
        raise KeyError(f'Invalid 3 letter residue name: "{three_or_one}".')
    elif n_chars == 1 and three_or_one not in _3_TO_1.values():
        raise KeyError(f'Invalid 1 letter residue code: "{three_or_one}".')

    if len(three_or_one) == 1:
        return three_or_one
    return _3_TO_1[three_or_one]


def _parse_index_selection(index_selection: str, struct_dict: Dict[str, List[str]]) -> Dict[str, npt.NDArray[np.bool_]]:
    selections = index_selection.split(",")
    selected_res = {c.upper(): np.full((len(el),), False) for c, el in struct_dict.items()}

    for s in selections:
        invert = False
        if s.startswith("!"):
            invert = True
            s = s[1:]

        chain: Iterable[str] = selected_res.keys()
        if s[0].upper() in string.ascii_uppercase:
            chain = [s[0].upper()]
            s = s[1:]

        if "-" in s:
            start, end = tuple(int(el) for el in s.split("-"))
            slice_ = slice(start - 1, end)
        else:
            start = int(s)
            slice_ = slice(start - 1, start)

        for c in chain:
            selected_res[c][slice_] = True
            if invert:
                selected_res[c] = ~selected_res[c]

    return selected_res


def _parse_resname_selection(
    name_selection: str, struct_dict: Dict[str, List[str]]
) -> Dict[str, npt.NDArray[np.bool_]]:
    # TODO update with chain selection
    invert = False
    if name_selection.startswith("!"):
        invert = True
        name_selection = name_selection[1:]

    selected_res = {c.upper(): np.full((len(el),), False) for c, el in struct_dict.items()}
    restypes = {_to_one_letter_code(el) for el in name_selection.split(",")}

    for sele, chain in zip(selected_res.values(), struct_dict.values()):
        for idx, res in enumerate(chain):
            if res in restypes:
                sele[idx] = True

    if invert:
        return {c: ~s for c, s in selected_res.items()}
    return selected_res


def parse_command(command: str, struct_dict: Dict[str, List[str]]) -> ResidueBias:
    """Parses a single command and returns a `ResidueBias` corresponding to this selection."""
    _res_selections = {
        "idx": _parse_index_selection,
        "name": _parse_resname_selection,
    }

    cmd, *tokens, bias_kw, restypes = command.split()
    if cmd != "select":
        raise KeyError(f'Invalid token "{cmd}" at beginning of command: "{command}"')

    # Determine selected residues.
    selection = {c.upper(): np.full((len(el),), False) for c, el in struct_dict.items()}
    t, res = tokens[:2]
    if t not in _res_selections:
        valid_tokens = '", "'.join(_res_selections)
        raise KeyError(f'Invalid token "{t}" did you mean: "{valid_tokens}"')
    selection.update(_res_selections[t](res, struct_dict))

    for logic_op, t, res in zip(tokens[::3], tokens[1::3], tokens[2::3]):
        updated_selections = _res_selections[t](res, struct_dict)
        for chain, sele in updated_selections.values():
            if logic_op == "&" or logic_op == "and":
                selection[chain] &= sele
            elif logic_op == "|" or logic_op == "or":
                selection[chain] |= sele
            else:
                raise KeyError(f'Unknown logical operator "{logic_op}".')

    # Parse biases.
    if bias_kw != "res":
        raise KeyError(f'Invalid token "{bias_kw}", should be "res".')

    biases = np.zeros((len(_1_LETTER_CODES),))
    for bias in restypes.split(","):
        if ":" not in bias:
            raise ValueError(
                "Improperly formatted bias string, should be a list of 1 letter residue types followed by a bias value."
            )

        r, b = bias.split(":")
        for el in set(r):
            biases[_1_LETTER_CODES.index(el)] = float(b)

    return ResidueBias(selection, biases)


def parse_command_file(command_path: Path) -> List[str]:
    if not command_path.exists():
        raise FileNotFoundError(f'Could not find "{command_path}".')

    with command_path.open("r") as cf:
        commands = [el.strip() for el in strip_comments(cf.read()).split(";")]

    return list(filter(None, commands))


def get_protein_sequence(struct_json_path: Path) -> Tuple[Dict[str, List[str]], str]:
    struct_json_path = Path(struct_json_path)
    data = json.loads(struct_json_path.read_text())
    structure: Dict[str, List[str]] = {}

    name = data.get("name", None)
    if name is None:
        raise KeyError(f"Missing name in structure JSON file.")

    for chain, seq in data.items():
        if not chain.startswith("seq_"):
            continue

        chain_id = chain[-1].upper()
        if chain_id in structure:
            raise KeyError(f'Duplicate chain "{chain_id}" found.')

        structure[chain_id] = [_to_one_letter_code(el) for el in seq]

    return structure, name


def write_bias_json(
    struct_dict: Dict[str, List[str]], biases: List[ResidueBias], name: str, out_path: Path, overwrite: bool = False
) -> None:
    out_path = Path(out_path)
    if out_path.exists() and not overwrite:
        raise FileExistsError(f'"{out_path}" already exists.')

    json_out = {name: {k: np.zeros((len(v), len(_1_LETTER_CODES))) for k, v in struct_dict.items()}}
    # json_out = {name: {k: np.zeros((len(_1_LETTER_CODES), len(v))) for k, v in struct_dict.items()}}
    pdb = json_out[name]
    for b in biases:
        for chain, sele in b.selection.items():
            bias = np.tile(b.bias, (sele.sum(), 1))
            pdb[chain][sele] = np.where(b.bias != 0, bias, pdb[chain][sele])  # [non_zero]

    for k in pdb:
        pdb[k] = pdb[k].tolist()
    out_path.write_text(json.dumps(json_out))


def main() -> None:
    import argparse

    argument_parser = argparse.ArgumentParser(
        description="Generates a MPNN compatible JSON file with a given set of biases.",
    )
    argument_parser.add_argument(
        "-j",
        "--input_json",
        type=Path,
        required=True,
        help='Parsed structure json file. To generate one from a PDB use "parse_multiple_chains.py" '
        'May also provide a directory, in which case all files with a ".json" extension will be parsed.',
    )
    argument_parser.add_argument(
        "-o",
        "--out_path",
        type=Path,
        help="Output location to write biases JSON. May also specify a directory.",
        default=Path("./biases.json"),
    )
    group = argument_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-b",
        "--bias_file",
        type=Path,
        help="Path to biases file from which to generate biases from. See help for writing residue selections."
        'Use "-e" to print an example bias input.',
    )
    group.add_argument(
        "-s",
        "--bias_string",
        type=str,
        help="Selection string corresponding to given bias. Uses the same formatting as the bias file.",
    )
    argument_parser.add_argument("-e", dest="example", action="store_true", help="Prints example bias file.")
    argument_parser.add_argument(
        "--overwrite", action="store_true", help="Whether to allow overwritting existing files."
    )
    argument_parser.add_argument("-q", "--quiet", action="store_true", help="Whether to reduce output to the terminal.")
    args = argument_parser.parse_args()

    logging_level = logging.INFO if not args.quiet else logging.ERROR
    logging.basicConfig(level=logging_level)

    if args.example:
        print(print_example())
        raise SystemExit()

    commands = parse_command_file(args.bias_file) if args.bias_file is not None else []
    if args.bias_string:
        commands.extend([el.strip() for el in args.bias_string.split(";") if el])

    logging.info(f"Recieved the following commands:")
    for cmd in commands:
        logging.info("  - " + cmd)

    structure, name = get_protein_sequence(args.input_json)

    biases = [parse_command(cmd, structure) for cmd in commands]
    write_bias_json(structure, biases, name, out_path=args.out_path, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
