from get_ngram import load_ngram_new
import numpy as np
import ipdb
import math
import os
from tqdm import tqdm
from dp import dp
from char_judge import is_chinese, is_alphabet
import numpy.linalg as LA


def sg(x):
    return x

def sg_l(x):
    def t(x): 
        if x == 0:
            return 0
        return math.log(x, 2) # np.power(x, 0.3)
    return t(x) - t(5)

coef_rm = 0
coef_wk = 50 # coef_wk = 0.1 * coef_rm
coef_xw = 5 # coef_xw = 0.1 * coef_wk
uni_gram, bi_gram, tri_gram = load_ngram_new(coef_rm, coef_wk, coef_xw) # coef_rm=200, coef_wk=20

weaken_set = set("未见可或行于及和的")

def g(s, default=1):
    d = [default, 0, 0]
    assert 1 <= len(s) <= 3
    if len(s) == 1: return uni_gram.get(s, d)[0]
    if len(s) == 2: return bi_gram.get(s, d)[0]
    return tri_gram.get(s, d)[0]

uni_list = [x[0] for x in uni_gram.values()]
uni_log_list = [sg_l(x) for x in uni_list]
bi_list = [x[0] for x in bi_gram.values()]
bi_log_list = [sg_l(x) for x in bi_list]
tri_list = [x[0] for x in tri_gram.values()]
tri_log_list = [sg_l(x) for x in tri_list]

uni_mean = np.mean(uni_list)
uni_sd = np.std(uni_list)
uni_log_mean = np.mean(uni_log_list)
uni_log_sd = np.std(uni_log_list)
bi_mean = np.mean(bi_list)
bi_sd = np.std(bi_list)
bi_log_mean = np.mean(bi_log_list)
bi_log_sd = np.std(bi_log_list)
tri_mean = np.mean(tri_list)
tri_sd = np.std(tri_list)
tri_log_mean = np.mean(tri_log_list)
tri_log_sd = np.std(tri_log_list)
param = [uni_mean, uni_sd, uni_log_mean, uni_log_sd,
         bi_mean, bi_sd, bi_log_mean, bi_log_sd,
         tri_mean, tri_sd, tri_log_mean, tri_log_sd]

eps = 1e-9
eps_l = [eps, 0, 0]
uni_count = len(uni_list)
bi_count = len(bi_list)
tri_count = len(tri_list)

def is_alphabet(ch):
    if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '0' <= ch <= '9':
        return True
    return False

def calculate_bi(s, front=" ", back=" "):
    # len(s) = 2 abcd
    if is_alphabet(s[0]) and is_alphabet(s[1]):
        return 80
    n_bc = bi_gram.get(s, eps_l)[0]
    if n_bc <= 1:
        return 0

    p_c_b = n_bc / uni_gram.get(s[0])[1]
    p_b_c = n_bc / uni_gram.get(s[1])[2]
    p_c_ab = 0
    p_b_cd = 0
    if front != " ":
        #p_c_ab = n_abc / n_ab
        n_abc = tri_gram.get(front + s, eps_l)[0]
        n_ab = bi_gram.get(front + s[0], eps_l)[1]
        if n_ab <= 1 or n_abc <= 1:
            p_c_ab = 0
        else:
            p_c_ab = n_abc / n_ab
    if back != " ":
        #p_b_cd = n_bcd / n_cd
        n_bcd = tri_gram.get(s + back, eps_l)[0]
        n_cd = bi_gram.get(s[1] + back, eps_l)[2]
        if n_bcd <= 1 or n_cd <= 1:
            p_b_cd = 0
        else:
            p_b_cd = n_bcd / n_cd
    
    weak_factor = 1
    weak_coef = 0.1
    if s[0] in weaken_set:
        weak_factor *= weak_coef
    if s[1] in weaken_set:
        weak_factor *= weak_coef
    return max(sg(p_c_ab), sg(p_b_cd), sg(p_c_b), sg(p_b_c)) * sg_l(n_bc) / bi_log_sd * weak_factor


def calculate_W(sentence):
    # s = "abcdefg"
    size = len(sentence)

    W = np.zeros((size, size))
    W[0, 1] = calculate_bi(sentence[0:2], back=sentence[2])
    W[1, 0] = W[0, 1]
    for i in range(size - 3):
        W[i + 1, i + 2] = calculate_bi(sentence[i + 1] + sentence[i + 2], sentence[i], sentence[i + 3])
        W[i + 2, i + 1] = W[i + 1, i + 2]
    W[size - 2, size - 1] = calculate_bi(sentence[-2:], front=sentence[-3])
    W[size - 1, size - 2] = W[size - 2, size - 1]

    return W

def seg_sentence_no_single(s, tp=1):
    if len(s) <= 2:
        return [s]

    W = calculate_W(s)
    
    D = np.diagflat(np.sum(W, 1))
    L = D - W
    eig_val, eig_vec = LA.eigh(L)
    
    k = len(s)
    checker = False
    while not checker or k == 3:
        checker = True
        seg = dp(s, W.diagonal(offset=1), k, c=6)
        l = [len(p) for p in seg]
        for i in range(len(l) - 1):
            if l[i] == 1 and l[i + 1] == 1 and chinese_judge(seg[i]) and chinese_judge(seg[i]):
                checker = False
                break
        k -= 1
    seg = dp(s, W.diagonal(offset=1), min(k+1, len(s)), c=6)
    return seg

def seg_sentence(s, tp=1, eig=1, offset=0):
    if len(s) <= 2:
        return [s]
    """
    tp = 0 spectral clustering
    tp = 1 dp_1
    tp = 2 dp_2
    tp = 3 dp_3   
    """

    W = calculate_W(s)
    
    D = np.diagflat(np.sum(W, 1))
    L = D - W
    eig_val, eig_vec = LA.eigh(L)

    if not isinstance(eig, str):
        k = min(max(sum(np.array(eig_val <= eig)) + offset, 3), len(s))
    else:
        if eig == "jieba":
            k = max(len(list(jieba.cut(s))) + offset, 3)
        if eig == "pkuseg":
            k = max(len(pku_seg.cut(s)) + offset, 3)
        if eig == "thulac":
            k = max(len(thu1.cut(s, text=True).split()) + offset, 3)

    if tp == 1:
        """
        #print(spec_word(s, W, verbose=1, eig_c=1))
        for k_i in [k]:#range(round(len(s)/10)+1, len(s)):
            #print(spec_word(s, W, verbose=1, eig_c=1))
            seg = dp(s, W.diagonal(offset=1), k_i, c=8)
            #print(seg, k_i, round(eig_val[k_i-1], 4))
        """
        seg = dp(s, W.diagonal(offset=1), k, c=8)
        while seg[0] != "。" or seg[-1] != "。":
            k += 1
            seg = dp(s, W.diagonal(offset=1), k, c=8)
    return seg

def seg_sentence_all(s):
    if len(s) <= 2:
        return [s]
    W = calculate_W(s)
    
    D = np.diagflat(np.sum(W, 1))
    L = D - W
    eig_val, eig_vec = LA.eigh(L)

    seg_list = []
    eig_list = []
    for k in range(max(math.floor((len(s) - 2) / 8) + 2, 3), len(s)):
        seg = dp(s, W.diagonal(offset=1), k, c=8)
        eig = eig_val[k-1]
        seg_list.append(seg)
        eig_list.append(eig)
    return seg_list, eig_list

def seg_f_all(input_name, output_name):
    with open(input_name, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(output_name, "w", encoding="utf-8") as f:
        for line in lines:
            seg_list, eig_list = seg_sentence_all("。"+line+"。")
            seg_list = [seg[1:-1] for seg in seg_list]
            for i in range(len(seg_list)):
                #f.write(" ".join(seg_list[i]) + " " + str(round(eig_list[i], 2)) + os.linesep)
                print(" ".join(seg_list[i]) + " " + str(round(eig_list[i], 2)))

def seg_f(input_name, output_name, eig=1, offset=0):
    with open(input_name, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(output_name, "w", encoding="utf-8") as f:
        for line in lines:
            if eig == "no_single":
                seg = " ".join(seg_sentence_no_single("。"+line+"。"))[1:-1].strip()
            elif eig == "no_single_no_split_dict":
                seg = " ".join(seg_sentence_no_single_no_split_dict("。"+line+"。"))[1:-1].strip()
            else:
                seg = " ".join(seg_sentence("。"+line+"。", eig=eig, offset=offset))[1:-1].strip()
            print(seg)
            f.write(seg + os.linesep)

if __name__ == "__main__":
    """
    s_list = ["，患者2008年9月3日因",
              "腹胀，发现腹部包块 在我院腹科行手术探查",
              "术中见盆腹腔肿物",
              "与肠管及子宫关系密切，遂行",
              "全子宫左附件切除+盆腔肿物切除+右半结肠切除+DIXON术",
              "术后病理示颗粒细胞瘤，诊断为颗粒细胞瘤IIIC期",
              "术后自2008年11月起行BEP方案化疗共4程",
              "末次化疗时间为2009年3月26日",
              "在阜外医院行冠脉支架植入术",
              "之后患者定期复查，2015-6-1，复查CT示",
              "髂嵴水平上腹部L5腰椎前见软组织肿块，大小约30MM×45MM",
              "密度欠均匀，边界尚清楚，轻度强化",
              "查肿瘤标志物均正常",
              "于2015-7-6行剖腹探查+膀胱旁肿物切除+骶前肿物切除+肠表面肿物切除术",
              "术程顺利"]
    #s_list = ["密度欠均匀，边界尚清楚，轻度强化","密度欠均匀","边界尚清楚","轻度强化"]
    all_s = ""
    for s in s_list:
        #calculate_sentence_tri(s)
        seg_sentence("。" + s + "。")
        print("")
        all_s += s + " "
    seg_sentence("。" + all_s + "。")
    ipdb.set_trace()
    """
    #seg_f("./data/context.txt", "/media/sdc/GanjinZero/ccks_cws/specter/specter_no_dict_max_6.txt")
    #seg_f_all("./data/test.txt", "/media/sdc/GanjinZero/ccks_cws/specter/test_all.txt")
    output_name = f"/media/sdc/GanjinZero/ccks_cws/specter/test_no_single_1_{coef_rm}_{coef_wk}_{coef_xw}.txt"
    seg_f("./data/test.txt", output_name, eig="no_single", offset=0)

