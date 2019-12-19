import argparse
import os
from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file_path")
parser.add_argument("-o", "--output_path")
parser.add_argument("-d", "--exclude_dictionary", default="")
parser.add_argument("-m", "--min_freq", default=5)

args = parser.parse_args()

terms = dict()
with open(args.file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

exclude_dictionary = set()
if args.exclude_dictionary != "":
    with open(args.exclude_dictionary, "r", encoding="utf-8") as f:
        lines_e = f.readlines()
    exclude_dictionary.update([term.strip() for term in lines_e])

for line in tqdm(lines):
    term = line.split()
    for t in term:
        if len(t) > 1:
            if t in terms:
                terms[t] += 1
            else:
                terms[t] = 1

tmp_terms = [[v[1], v[0]] for v in terms.items()]
tmp_terms.sort(reverse=True)

with open(args.output_path, "w", encoding="utf-8") as f:
    for t in tmp_terms:
        if t[0] > int(args.min_freq) and not t[1] in exclude_dictionary:
            f.write(t[1] + " " + str(t[0]) + os.linesep)

