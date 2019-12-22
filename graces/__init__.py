name = "graces"


import os
import time
from .get_n_gram import load_ngram_new
import numpy as np
import math
from tqdm import tqdm
from .utils.dp import dp
from .utils.char_judge import is_chinese, is_alphabet
import numpy.linalg as LA

def sg(x):
    return x

def sg_l(x):
    def t(x): 
        if x == 0:
            return 0
        return math.log(x, 2)
    return t(x) - t(5)

class graces:
    def __init__(self, coef_md=1, coef_rm=0, coef_wk=50, coef_xw=5, max_word_length=6):
        print("Graph Cut Chinese Segment")
        start_time = time.time()
        self.uni_gram, self.bi_gram, self.tri_gram = load_ngram_new(coef_rm, coef_wk, coef_xw)
        self.bi_log_sd = np.std([sg_l(x[0]) for x in self.bi_gram.values()])
        self.weaken_set = set("未见可或行于及和的")
        self.weak_coef = 0.1
        self.punc_set = set("。，,！!？? \n\r\"\'“”、()（）[]【】:：;；")
        self.max_word_length = max_word_length
        end_time = time.time()
        print(f"Load model for {round(end_time - start_time, 2)}s.")

    def g(self, s, default=1):
        d = [default, 0, 0]
        assert 1 <= len(s) <= 3
        if len(s) == 1: return self.uni_gram.get(s, d)[0]
        if len(s) == 2: return self.bi_gram.get(s, d)[0]
        return self.tri_gram.get(s, d)[0]

    def split_sentence_by_punc(self, sentence):
        sentence = sentence.replace("\n"," ").replace("\r"," ")
        result = []
        now_string = ""
        for ch in sentence:
            if ch in self.punc_set:
                result += [now_string]
                if ch != "":
                    result += [ch]
                now_string = ""
            else:
                now_string += ch
        if now_string != "":
            result += [now_string]
        return result

    def calculate_bi(self, s, front=" ", back=" "):
        eps_l = [1e-9, 0, 0]
        if is_alphabet(s[0]) and is_alphabet(s[1]):
            return 80
        n_bc = self.bi_gram.get(s, eps_l)[0]
        if n_bc <= 1:
            return 0

        p_c_b = n_bc / self.uni_gram.get(s[0])[1]
        p_b_c = n_bc / self.uni_gram.get(s[1])[2]
        p_c_ab = 0
        p_b_cd = 0
        if front != " ":
            #p_c_ab = n_abc / n_ab
            n_abc = self.tri_gram.get(front + s, eps_l)[0]
            n_ab = self.bi_gram.get(front + s[0], eps_l)[1]
            if n_ab <= 1 or n_abc <= 1:
                p_c_ab = 0
            else:
                p_c_ab = n_abc / n_ab
        if back != " ":
            #p_b_cd = n_bcd / n_cd
            n_bcd = self.tri_gram.get(s + back, eps_l)[0]
            n_cd = self.bi_gram.get(s[1] + back, eps_l)[2]
            if n_bcd <= 1 or n_cd <= 1:
                p_b_cd = 0
            else:
                p_b_cd = n_bcd / n_cd
    
        weak_factor = 1
        if s[0] in self.weaken_set:
            weak_factor *= self.weak_coef
        if s[1] in self.weaken_set:
            weak_factor *= self.weak_coef
        return max(sg(p_c_ab), sg(p_b_cd), sg(p_c_b), sg(p_b_c)) * sg_l(n_bc) / self.bi_log_sd * weak_factor

    def calculate_sentence(self, sentence):
        w = [self.calculate_bi(sentence[0:2], back=sentence[2])]
        for i in range(len(sentence) - 3):
            w.append(self.calculate_bi(sentence[i + 1] + sentence[i + 2], sentence[i], sentence[i + 3]))
        w.append(self.calculate_bi(sentence[-2:], front=sentence[-3]))
        return w

    def cut_small_sentence(self, sentence, k=-1):
        sentence = sentence.strip()
        if len(sentence) <= 2: return [sentence]
        w = self.calculate_sentence(sentence) 
        return dp(sentence, w, k=k, c=self.max_word_length)

    def cut(self, sentence):
        seg_result = []
        small_sentence_list = self.split_sentence_by_punc(sentence)
        for small_sentence in small_sentence_list:
            seg_result += self.cut_small_sentence(small_sentence)
        return seg_result

    def cut_k(self, sentence, k):
        return self.cut_small_sentence(sentence, k)

    def cut_all(self, sentence):
        result_list = []
        for i in range(math.ceil(len(sentence) / self.max_word_length), len(sentence) + 1, 1):
            result_list.append(self.cut_k(sentence, i))
        return result_list

    def cut_file(self, input_file, output_file):
        start_time = time.time()

        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(output_file, "w", encoding="utf-8") as f:
            for line in lines:
                seg_line = " ".join(" ".join(self.cut(line)).split())
                f.write(seg_line + os.linesep)
            
        end_time = time.time()
        print(f"Use {round(end_time - start_time, 2)}s.")

gc = graces()
cut = gc.cut
cut_k = gc.cut_k
cut_file = gc.cut_file

