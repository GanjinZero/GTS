import numpy as np
import time
from tqdm import tqdm
import sys
import os

k_num = 4


def generate_test_batch(sentence):
    train_option = []
    final_word_option = []
    len_list = []
    word_option = sentence.split()
    sentence_comb = "".join(word_option)
    if k_num > 0:
        sentence_use = "_" * k_num + sentence_comb + "_" * k_num
    else:
        sentence_use = sentence_comb
    for word in word_option:
        len_list.append(len(word))
    len_list = [0] + len_list[0:-1]
    len_cum_list = np.cumsum(len_list)

    for i in range(len(word_option)):
        word = word_option[i]
        #if len(word) < 2:
        #    continue
        start = len_cum_list[i]
        end = len_cum_list[i] + len(word)
        prefix = sentence_use[start : start + k_num]
        suffix = sentence_use[end + k_num : end + k_num * 2]
        check_word = prefix + word + suffix
        train_option.append(check_word)
        final_word_option.append(word)

    return final_word_option, train_option

def test_on_user_text(user_text_file_path, output_path):
    start = time.clock()
    counter = 0
    word_option = []
    test_option = []
    with open(user_text_file_path, "r", encoding="utf-8") as f:
        use_line = f.readlines()
        length = len(use_line)
        pbar = tqdm(total=length)
        for line in use_line:
            counter += 1
            pbar.update(1)
            line = line.strip()
            batch_word, batch_train = generate_test_batch(line)
            for i in range(len(batch_train)):
                #if not batch_train[i] in test_option:
                word_option.append(batch_word[i])
                test_option.append(batch_train[i])
    print("Test set generate done.")
    pbar.close()

    with open(output_path, "w", encoding="utf-8") as f:
        for line in test_option:
            f.write("0\t" + line + os.linesep) 

if __name__ == "__main__":
    user_text = sys.argv[1]
    output_path = sys.argv[2]
    test_on_user_text(user_text, output_path)

