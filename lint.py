import os
import glob

PREFIX_ORDER = {
    "full:": 2,
    "domain:":3,
    "keyword:": 1,
    "regexp:": 0
}

def sort_rules(lines):
    unique_lines = set(
        line.strip()
        for line in lines
        if line.strip()
    )

    def sort_key(line):
        for prefix, order in PREFIX_ORDER.items():
            if line.startswith(prefix):
                return (order, line.lower())
        return (99, line.lower())

    return sorted(
        unique_lines,
        key=sort_key
    )

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    sorted_lines = sort_rules(lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted_lines))
        f.write("\n")

if __name__ == '__main__':
    files = glob.glob(
        os.path.join("./black_list", "*.txt")
    )

    for file in files:
        process_file(file)