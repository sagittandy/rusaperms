"""Count the number of permanents in each .csv file
so that we can make an index only of non-empty maps.
"""
import csv
import pathlib

from typing import List, Tuple

DATA_DIR = "data"

def perm_counts() -> List[Tuple[str, int]]:
    """Result looks like {"AL": 3, "OR": 10, ... }"""
    counts = [ ]
    data_dir = pathlib.Path(DATA_DIR)
    csv_files = data_dir.glob("*.csv")
    for file_name in csv_files:
        csv_path = pathlib.Path(file_name)
        state = csv_path.stem
        with open(file_name, "r") as f:
            lines = f.readlines()
            # Each file includes a header row
            data_lines = len(lines) - 1
            if data_lines > 0:
                counts.append((state, data_lines))
    return counts

def main():
    """"Smoke test"""
    counts = perm_counts()
    print(sorted(counts))

if __name__ == "__main__":
    main()


