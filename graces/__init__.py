name = "graces"


import os
import time
from .utils.dp import dp
from .utils.char_judge import is_chinese, is_alphabet, is_english_or_number
from .get_n_gram import load_ngram_new, build_new_ngram, load_ngram_file
import numpy as np
import math
from tqdm import tqdm
import numpy.linalg as LA
from .bert.Predictor import bert_predictor
from .bert.make_test import generate_test_batch


def sg(x):
    return x

def sg_l(x):
    def t(x): 
        if x == 0:
            return 0
        return math.log(x, 2)
    return t(x) - t(5)

class graces:
    def __init__(self, coef_me=1, coef_rm=5, coef_wk=50, coef_xw=5, max_word_length=6, eig_cut=1., bert_model="ccks", language="chinese", tp="ratio"):
        print("Graph Cut Chinese Segment")
        self.initialized = False
        self.bert_initialized = False

        self.coef_me = coef_me
        self.coef_rm = coef_rm
        self.coef_wk = coef_wk
        self.coef_xw = coef_xw
        self.weaken_set = set("未见可或行于及和的")
        self.weak_coef = 0.1
        self.punc_set = set("。，,！!？? \n\r\"\'“”、()（）[]【】:：;；+-*/＋－＊／-+/")
        self.max_word_length = max_word_length
        self.postprocess_alphabet_number = True
        self.eig_cut = eig_cut
        self.language = language
        self.tp = tp
        self.jp_uni = "/media/sdc/GanjinZero/wiki_ja/ngram/uni_gram.json"
        self.jp_bi = "/media/sdc/GanjinZero/wiki_ja/ngram/bi_gram.json"
        self.jp_tri = "/media/sdc/GanjinZero/wiki_ja/ngram/tri_gram.json"

        # Bert config
        self.max_sequence_length = 24
        self.bert_config_file = "/media/sdc/GanjinZero/graces/graces/bert/medical_model/bert_config.json"
        self.vocab_file = '/media/sdc/GanjinZero/graces/graces/bert/medical_model/vocab.txt'
        self.bert_model = bert_model
        self.medical_model_path = '/media/sdc/GanjinZero/graces/graces/bert/medical_model/model.ckpt-30000'
        self.news_model_path = '/media/sdc/GanjinZero/graces/graces/bert/news_model/model.ckpt-23437'
        self.ccks_model_path = '/media/sdc/GanjinZero/graces/graces/bert/ccks_model/model.ckpt-3694'

    def initialize(self):
        start_time = time.time()
        if self.language == "chinese":
            self.uni_gram, self.bi_gram, self.tri_gram = load_ngram_new(self.coef_me, self.coef_rm, self.coef_wk, self.coef_xw)
            self.bi_log_sd = np.std([sg_l(x[0]) for x in self.bi_gram.values()])
        if self.language == "japanese":
            u, b, t = load_ngram_file(self.jp_uni, self.jp_bi, self.jp_tri)
            self.uni_gram, self.bi_gram, self.tri_gram = build_new_ngram(u, b, t)
            self.bi_log_sd = np.std([sg_l(x[0]) for x in self.bi_gram.values()])
        end_time = time.time()
        print(f"Load model for {round(end_time - start_time, 2)}s.")
        self.initialized = True

    def bert_initialize(self):
        if self.bert_model == "medical":
            self.predictor = bert_predictor(self.max_sequence_length, self.bert_config_file, self.medical_model_path, self.vocab_file)
        if self.bert_model == "news":
            self.predictor = bert_predictor(self.max_sequence_length, self.bert_config_file, self.news_model_path, self.vocab_file)
        if self.bert_model == "ccks":
            self.predictor = bert_predictor(self.max_sequence_length, self.bert_config_file, self.ccks_model_path, self.vocab_file)
        self.bert_initialized = True

    def change_eig_cut(self, eig_cut):
        self.eig_cut = eig_cut

    def change_max_word_length(self, max_word_length):
        self.max_word_length = max_word_length

    def g(self, s, default=1):
        if not self.initialized:
            self.initalize()

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
            if ch in self.punc_set or is_english_or_number(ch):
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
        if not self.initialized:
            self.initialize()

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
        if s[0] in self.weaken_set or s[1] in self.weaken_set:
            weak_factor *= self.weak_coef
        #if s[1] in self.weaken_set:
        #    weak_factor *= self.weak_coef
        return max(sg(p_c_ab), sg(p_b_cd), sg(p_c_b), sg(p_b_c)) * sg_l(n_bc) / self.bi_log_sd * weak_factor
        #return sg_l(n_bc) * weak_factor

    def calculate_sentence(self, sentence):
        w = [self.calculate_bi(sentence[0:2], back=sentence[2])]
        for i in range(len(sentence) - 3):
            w.append(self.calculate_bi(sentence[i + 1] + sentence[i + 2], sentence[i], sentence[i + 3]))
        w.append(self.calculate_bi(sentence[-2:], front=sentence[-3]))
        return w

    def calculate_eig_count(self, w, eig_cut):
        # calculate the count of Laplacian matrix which eigenvalue is smaller than eig_cut
        L = np.zeros((len(w) + 1, len(w) + 1))
        L[0][0] = w[0]
        L[-1][-1] = w[-1]
        for i in range(len(w)):
            L[i][i + 1] = -w[i]
            L[i + 1][i] = -w[i]
            if i < len(w) - 1:
                L[i + 1][i + 1] = w[i] + w[i + 1]
        eig_val, _ = np.linalg.eigh(L)
        count = 0
        for eig in eig_val:
            if eig <= eig_cut:
                count += 1
        return count

    def postprocess(self, seg_list):
        # Put alphabet together
        seg_list = [seg for seg in seg_list if len(seg) > 0]
        if len(seg_list) == 0:
            seg_list = [""]
        seg_new = [seg_list[0]]
        for i in range(len(seg_list) - 1):
            if is_alphabet(seg_list[i][-1]) and is_alphabet(seg_list[i + 1][0]):
                seg_new[-1] = seg_new[-1] + seg_list[i + 1]
            else:
                seg_new += [seg_list[i + 1]]

        return seg_new

    def cut_small_sentence(self, sentence, k=-1):
        sentence = sentence.strip()
        if len(sentence) <= 2: return [sentence]
        w = self.calculate_sentence(sentence) 
        if k == -2: # use calculate eig count
            k = self.calculate_eig_count(w, eig_cut=self.eig_cut)
        return dp(sentence, w, k=k, c=self.max_word_length, tp=self.tp)

    def cut_small_sentence_bert(self, sentence, debug=False):
        if not self.bert_initialized:
            self.bert_initialize()

        option_cut = self.cut_all(sentence)
        if self.postprocess_alphabet_number:
            option_cut = [self.postprocess(cut) for cut in option_cut]
        if len(option_cut) == 1:
            return option_cut[0]

        all_input = []
        for cut in option_cut:
            sen = " ".join(cut)
            _, batch_input = generate_test_batch(sen)
            all_input.extend(batch_input)

        bert_score = self.predictor.predict(all_input)
        #print(len(bert_score))

        count = 0
        optimal_cut = []
        now_score = -1
        for cut in option_cut:
            score = 0
            for word in cut:
                score += bert_score[count] * len(word)
                count += 1
            score = round(score / len(sentence), 2)
            if debug:
                print(cut, score)
            if score >= now_score - 0.01:
                now_score = score
                optimal_cut = cut
        return optimal_cut 

    def cut(self, sentence, method="no_two_char"):
        seg_result = []
        small_sentence_list = self.split_sentence_by_punc(sentence)
        for small_sentence in small_sentence_list:
            if method == "no_two_char":
                seg_result += self.cut_small_sentence(small_sentence)
            if method == "eig_cut":
                seg_result += self.cut_small_sentence(small_sentence, k=-2)
            if method == "bert":
                seg_result += self.cut_small_sentence_bert(small_sentence)
        if self.postprocess_alphabet_number:
            return self.postprocess(seg_result)
        return seg_result

    def cut_k(self, sentence, k):
        return self.cut_small_sentence(sentence, k)

    def cut_all(self, sentence):
        sentence = sentence.strip()
        if len(sentence) <= 2: return [[sentence]]
        w = self.calculate_sentence(sentence)
        return dp(sentence, w, k=0, c=self.max_word_length, tp=self.tp)

    def cut_file(self, input_file, output_file, method="no_two_char"):
        """
        if method == "bert":
            self.cut_file_bert(input_file, output_file)
            return
        """

        start_time = time.time()

        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(output_file, "w", encoding="utf-8") as f:
            for line in tqdm(lines):
                seg_line = " ".join(" ".join(self.cut(line, method)).split())
                f.write(seg_line + os.linesep)
            
        end_time = time.time()
        print(f"Use {round(end_time - start_time, 2)}s.")

    def cut_file_all(self, input_file, output_file):
        start_time = time.time()

        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(output_file, "w", encoding="utf-8") as f:
            for line in tqdm(lines):
                small_sentence_list = self.split_sentence_by_punc(line)
                for sentence in small_sentence_list:
                    cut_list = self.cut_all(sentence)
                    for cut in cut_list:
                        seg_line = " ".join(" ".join(cut).split())
                        f.write(seg_line + os.linesep)
            
        end_time = time.time()
        print(f"Use {round(end_time - start_time, 2)}s.")

    def cut_file_bert(self, input_file, output_file):
        start_time = time.time()

        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if not self.bert_initialized:
            self.bert_initialize()

        option_cut_dict = dict()
        all_input = []
        for i in tqdm(range(len(lines))):
            line = lines[i]
            small_sentence_list = self.split_sentence_by_punc(line)
            for small_sentence in small_sentence_list:
                option_cut = self.cut_all(small_sentence)
                if self.postprocess_alphabet_number:
                    option_cut = [self.postprocess(cut) for cut in option_cut]
                option_cut_dict[small_sentence] = option_cut

                for cut in option_cut:
                    sen = " ".join(cut)
                    _, batch_input = generate_test_batch(sen)
                    all_input.extend(batch_input)

        bert_score = self.predictor.predict(all_input, verbose=1)
        #print(len(bert_score))

        count = 0
        with open(output_file, "w", encoding="utf-8") as f:
            for i in tqdm(range(len(lines))):
                line = lines[i]
                if line.strip() == "":
                    f.write(os.linesep)
                    continue

                small_sentence_list = self.split_sentence_by_punc(line)
                seg_result = []
                for small_sentence in small_sentence_list:
                    optimal_cut = []
                    now_score = -1
                    for cut in option_cut_dict[small_sentence]:
                        score = 0
                        for word in cut:
                            score += bert_score[count] * len(word)
                            count += 1
                        score = round(score / len(small_sentence), 2)
                        # print(cut, score)
                        if score >= now_score - 0.01:
                            now_score = score
                            optimal_cut = cut
                    seg_result += optimal_cut
                if self.postprocess_alphabet_number:
                    seg_result = self.postprocess(seg_result)
                f.write(" ".join(" ".join(seg_result).split()) + os.linesep)

        end_time = time.time()
        print(f"Use {round(end_time - start_time, 2)}s.")


gc = graces()
cut = gc.cut
cut_k = gc.cut_k
cut_file = gc.cut_file

