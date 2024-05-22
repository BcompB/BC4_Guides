# Simple script to sort MPNN output file by score.
# author: Tim Neary, timdot10@gmail.com
from pathlib import Path
from typing import Any, Iterable, List, Union


def _chunk_list(l: List, chunk_size: int) -> Iterable:
    for idx in range(0, len(l), chunk_size):
        yield l[idx: idx + chunk_size]


def flatten(iterable: Iterable[Union[Iterable[Any], Any]]) -> Iterable[Any]:
    """Flattens an iterable (of iterables) to a single leveled iterable."""
    for el in iterable:
        if isinstance(el, Iterable) and not isinstance(el, str):
            yield from flatten(el)
        else:
            yield el


def get_score(fasta_description: str) -> float:
    score = fasta_description.split(",")[2]
    return float(score.split("=")[1])


def sort_scores(fasta_paths: List[Path]) -> List[str]:
    lines = list(flatten(el.read_text().splitlines() for el in fasta_paths))
    
    return sorted(_chunk_list(lines, 2), key=lambda el: get_score(el[0]))



def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Simple script to sort MPNN output file by score.")
    parser.add_argument("fasta_paths", type=Path, nargs="+", help="Path to MPNN fasta output.")
    parser.add_argument("-o", "--out_path", type=Path, default=Path("./sorted.fasta"), help="Path to output of sorted scores.")
    args = parser.parse_args()


    sorted_scores = sort_scores(args.fasta_paths)
    args.out_path.write_text("\n".join(flatten(sorted_scores)))


if __name__ == "__main__":
    main()