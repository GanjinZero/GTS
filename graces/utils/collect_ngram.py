import argparse
import json
import os
import time
import string
from tqdm import tqdm
from pyserverchan import pyserver


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file_path")
parser.add_argument("-o", "--output_path")
parser.add_argument("-n", "--max_n", default="3")
parser.add_argument("-p", "--use_punc", default="0")
parser.add_argument("-e", "--use_number_english", default="1")
parser.add_argument("-m", "--min_freq", default="5")

args = parser.parse_args()
if os.path.isfile(args.file_path):
    file_path_list = [args.file_path] 
else:
    file_path_list = []
    for root, dirs, files in os.walk(args.file_path):
        for f in files:
            now_file_path = os.path.join(root, f)
            if os.path.isfile(now_file_path):
                file_path_list.append(now_file_path)

print(f"Found {len(file_path_list)} file(s) under {args.file_path}")

punc_set = set('＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏！？｡。 ' + '\t' + '\n' + '\r' + string.punctuation)

def is_punc(ch):
    if ch in punc_set:
        return 0
    return 1

def is_number_or_english(ch):
    if "a" <= ch <= "z" or "A" <= ch <= "Z" or "0" <= ch <= "9":
        return 0
    return 1

start_time = time.time()

class Text(object):
    def __init__(self, file_path_list):
        self.file_path_list = file_path_list

    def __iter__(self):
        file_count = 0
        for file_path in file_path_list:
            file_count += 1
            print(f"Now file name:{file_path}, now file count:{file_count}")
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    yield list(line.strip())

sentences = Text(file_path_list)

uni_gram = dict()
bi_gram = dict()
tri_gram = dict()
quad_gram = dict()

max_n = int(args.max_n)
assert 1 <= max_n <= 4, "-n should be 1, 2, 3, 4"

for line in tqdm(sentences):
    use = [1 for x in line]
    if args.use_punc != "1":
        use = [min(use[i], is_punc(line[i])) for i in range(len(line))]
    if args.use_number_english != "1":
        use = [min(use[i], is_number_or_english(line[i])) for i in range(len(line))]

    for i in range(len(line)):
        if use[i] == 1:
            if not line[i] in uni_gram:
                uni_gram[line[i]] = 1
            else:
                uni_gram[line[i]] += 1

    if max_n > 1:
        for i in range(len(line) - 1):
            if use[i] == 1 and use[i + 1] == 1:
                if not line[i] + line[i + 1] in bi_gram:
                    bi_gram[line[i] + line[i + 1]] = 1
                else:
                    bi_gram[line[i] + line[i + 1]] += 1
    
    if max_n > 2:
        for i in range(len(line) - 2):
            if use[i] == 1 and use[i + 1] == 1 and use[i + 2] == 1:
                s = line[i] + line[i + 1] + line[i + 2]
                if not s in tri_gram:
                    tri_gram[s] = 1
                else:
                    tri_gram[s] += 1

    if max_n > 3:
        for i in range(len(line) - 3):
            if use[i] + use[i + 1] + use[i + 2] + use[i + 3] == 4:
                s = line[i] + line[i + 1] + line[i + 2] + line[i + 3]
                if not s in quad_gram:
                    quad_gram[s] = 1
                else:
                    quad_gram[s] += 1

min_freq = int(args.min_freq)
uni_gram = {k: v for k, v in uni_gram.items() if v >= min_freq}
bi_gram = {k: v for k, v in bi_gram.items() if v >= min_freq}
tri_gram = {k: v for k, v in tri_gram.items() if v >= min_freq}
quad_gram = {k: v for k, v in quad_gram.items() if v >= min_freq}

# Save n_gram
os.system(f"mkdir {args.output_path}")
with open(os.path.join(args.output_path, "uni_gram.json"), "w", encoding="utf-8") as f:
    json.dump(uni_gram, f)
if max_n > 1:
    with open(os.path.join(args.output_path, "bi_gram.json"), "w", encoding="utf-8") as f:
        json.dump(bi_gram, f)
if max_n > 2:
    with open(os.path.join(args.output_path, "tri_gram.json"), "w", encoding="utf-8") as f:
        json.dump(tri_gram, f)
if max_n > 3:
    with open(os.path.join(args.output_path, "quad_gram.json"), "w", encoding="utf-8") as f:
        json.dump(quad_gram, f)

# Print count of n_gram
print(f"uni_gram:{len(uni_gram)}")
print(f"bi_gram:{len(bi_gram)}")
print(f"tri_gram:{len(tri_gram)}")
print(f"quad_gram:{len(quad_gram)}")

use_time = time.time() - start_time
log_text = f"Job_name:n-gram, Use_time:{str(use_time)}, Save_path:{args.output_path})"
svc = pyserver.ServerChan()
svc.output_to_weixin(log_text)

