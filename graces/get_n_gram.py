import os
import ujson
from .utils.char_judge import is_chinese
from tqdm import tqdm

model_path = "/home/veritas/GanjinZero/specter/model/"


def load_ngram(use_dictionary=False, coef=5000):
    with open(os.path.join(model_path, "char_dict_new.json"), "r", encoding="utf-8") as f:
        char_dict = ujson.load(f)
    print(f"Uni-gram count:{len(char_dict)}")

    bi_gram = dict()
    with open(os.path.join(model_path, "info_new.txt"), "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        tmp = line.split()
        n_count = int(tmp[1][1:len(tmp[1]) - 1])
        bi_gram[tmp[0]] = n_count
    print(f"Bi-gram count:{len(lines)}")

    tri_gram = dict()
    with open(os.path.join(model_path, "info3_new.txt"), "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        tmp = line.split()
        n_count = int(tmp[1][1:len(tmp[1]) - 1])
        tri_gram[tmp[0]] = n_count
    print(f"Tri-gram count:{len(lines)}")

    if use_dictionary:
        print(f"Load dictionary into n_gram, coef={coef}")
        user_dictionary_path = "../medical_term_judger/dictionary/all_dictionary.txt"
        with open(user_dictionary_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in tqdm(lines):
            line = line.strip()
            for term in line.split(","):
                ch_judge = [chinese_judge(x) for x in term]
                for i in range(len(term)):
                    if ch_judge[i]:
                        if term[i] in char_dict:
                            char_dict[term[i]] += coef
                        else:
                            char_dict[term[i]] = coef
                for i in range(len(term) - 1):
                    if ch_judge[i] and ch_judge[i + 1]:
                        now_bi = term[i] + term[i + 1]
                        if now_bi in bi_gram:
                            bi_gram[now_bi] += coef
                        else:
                            bi_gram[now_bi] = coef
                for i in range(len(term) - 2):
                    if ch_judge[i] and ch_judge[i + 1] and ch_judge[i + 2]:
                        now_tri = term[i] + term[i + 1] + term[i + 2]
                        if now_tri in tri_gram:
                            tri_gram[now_tri] += coef
                        else:
                            tri_gram[now_tri] = coef
        print(f"Uni-gram count:{len(char_dict)}")
        print(f"Bi-gram count:{len(bi_gram)}")
        print(f"Tri-gram count:{len(tri_gram)}")

    return char_dict, bi_gram, tri_gram

def load_ngram_file(uni_gram_path, bi_gram_path, tri_gram_path):
    print(uni_gram_path, bi_gram_path, tri_gram_path)
    with open(uni_gram_path, "r", encoding="utf-8") as f:
        uni_gram = ujson.load(f)
    print(f"Uni-gram count:{len(uni_gram)}")
    with open(bi_gram_path, "r", encoding="utf-8") as f:
        bi_gram = ujson.load(f)
    print(f"Bi-gram count:{len(bi_gram)}")
    with open(tri_gram_path, "r", encoding="utf-8") as f:
        tri_gram = ujson.load(f)
    print(f"Tri-gram count:{len(tri_gram)}")
    return uni_gram, bi_gram, tri_gram

def migrate_ngram(uni_gram_list, bi_gram_list, tri_gram_list, coef_list):
    all_uni_gram = dict()
    all_bi_gram = dict()
    all_tri_gram = dict()
    for i in range(len(coef_list)):
        uni_gram = uni_gram_list[i]
        bi_gram = bi_gram_list[i]
        tri_gram = tri_gram_list[i]
        for uni in uni_gram:
            if uni in all_uni_gram:
                all_uni_gram[uni] += uni_gram[uni] * coef_list[i]
            else:
                all_uni_gram[uni] = uni_gram[uni] * coef_list[i]
        for bi in bi_gram:
            if bi in all_bi_gram:
                all_bi_gram[bi] += bi_gram[bi] * coef_list[i]
            else:
                all_bi_gram[bi] = bi_gram[bi] * coef_list[i]
        for tri in tri_gram:
            if tri in all_tri_gram:
                all_tri_gram[tri] += tri_gram[tri] * coef_list[i]
            else:
                all_tri_gram[tri] = tri_gram[tri] * coef_list[i]
    return all_uni_gram, all_bi_gram, all_tri_gram
    

def build_new_ngram(uni_gram, bi_gram, tri_gram):
    """
    motivation: sum_X n(XA) != n(A)
    """
    new_uni_gram = dict()
    new_bi_gram = dict()
    new_tri_gram = dict()
    for uni in uni_gram:
        new_uni_gram[uni] = [uni_gram[uni], 0, 0]
    for bi in bi_gram:
        new_bi_gram[bi] = [bi_gram[bi], 0, 0]
        new_uni_gram[bi[0]][1] += bi_gram[bi]
        new_uni_gram[bi[1]][2] += bi_gram[bi]
    for tri in tri_gram:
        s0 = tri[0:2]
        new_bi_gram[s0][1] += tri_gram[tri]
        s1 = tri[1:3]
        new_bi_gram[s1][2] += tri_gram[tri]
        new_tri_gram[tri] = [tri_gram[tri], 0, 0]
    print("Build new n-gram done.")
    return new_uni_gram, new_bi_gram, new_tri_gram


def ngram(rm_coef, wk_coef, xw_coef):
    u_g, b_g, t_g = load_ngram()
    u_g_list = [u_g]
    b_g_list = [b_g]
    t_g_list = [t_g]
    coef_list = [1]
    if rm_coef > 0:
        rm_u_g, rm_b_g, rm_t_g = load_ngram_file("/media/sdc/GanjinZero/rmrb/ngram/uni_gram.json",
                                                "/media/sdc/GanjinZero/rmrb/ngram/bi_gram.json",
                                                "/media/sdc/GanjinZero/rmrb/ngram/tri_gram.json")
        u_g_list.append(rm_u_g)
        b_g_list.append(rm_b_g)
        t_g_list.append(rm_t_g)
        coef_list.append(rm_coef)
    if wk_coef > 0:
        wk_u_g, wk_b_g, wk_t_g = load_ngram_file("/media/sdc/GanjinZero/wiki_cn/ngram/uni_gram.json",
                                                "/media/sdc/GanjinZero/wiki_cn/ngram/bi_gram.json",
                                                "/media/sdc/GanjinZero/wiki_cn/ngram/tri_gram.json")
        u_g_list.append(wk_u_g)
        b_g_list.append(wk_b_g)
        t_g_list.append(wk_t_g)
        coef_list.append(wk_coef)
    if xw_coef > 0:
        xw_u_g, xw_b_g, xw_t_g = load_ngram_file("/media/sdc/GanjinZero/news2016zh/ngram/uni_gram.json",
                                                "/media/sdc/GanjinZero/news2016zh/ngram/bi_gram.json",
                                                "/media/sdc/GanjinZero/news2016zh/ngram/tri_gram.json")
        u_g_list.append(xw_u_g)
        b_g_list.append(xw_b_g)
        t_g_list.append(xw_t_g)
        coef_list.append(xw_coef)
    if rm_coef > 0 or wk_coef > 0 or xw_coef > 0:
        all_u_g, all_b_g, all_t_g = migrate_ngram(u_g_list, b_g_list, t_g_list, coef_list)
    else:
        all_u_g, all_b_g, all_t_g = u_g, b_g, t_g
    return build_new_ngram(all_u_g, all_b_g, all_t_g)

def save_ngram(rm_coef, wk_coef, xw_coef):
    u_g, b_g, t_g = ngram(rm_coef, wk_coef, xw_coef)
    rm_part = ""
    wk_part = ""
    if rm_coef > 0:
        rm_part = f"rm_{str(rm_coef)}_"
    if wk_coef > 0:
        wk_part = f"wk_{str(wk_coef)}"
    if xw_coef > 0:
        xw_part = f"xw_{str(xw_coef)}"
    save_folder_name = "/media/sdc/GanjinZero/ngram/" + "medical_1_" + rm_part + wk_part + xw_part
    os.system(f"mkdir {save_folder_name}")
    with open(os.path.join(save_folder_name, "uni_gram.json"), "w", encoding="utf-8") as f:
        ujson.dump(u_g, f)
    with open(os.path.join(save_folder_name, "bi_gram.json"), "w", encoding="utf-8") as f:
        ujson.dump(b_g, f)
    with open(os.path.join(save_folder_name, "tri_gram.json"), "w", encoding="utf-8") as f:
        ujson.dump(t_g, f)
    return None

def load_ngram_new(rm_coef, wk_coef, xw_coef):
    rm_part = ""
    wk_part = ""
    xw_part = ""
    if rm_coef > 0:
        rm_part = f"rm_{str(rm_coef)}_"
    if wk_coef > 0:
        wk_part = f"wk_{str(wk_coef)}"
    if xw_coef > 0:
        xw_part = f"xw_{str(xw_coef)}"
    load_folder_name = "/media/sdc/GanjinZero/ngram/" + "medical_1_" + rm_part + wk_part + xw_part
    if not os.path.exists(load_folder_name):
        save_ngram(rm_coef, wk_coef, xw_coef)
    with open(os.path.join(load_folder_name, "uni_gram.json"), "r", encoding="utf-8") as f:
        u_g = ujson.load(f)
    with open(os.path.join(load_folder_name, "bi_gram.json"), "r", encoding="utf-8") as f:
        b_g = ujson.load(f)
    with open(os.path.join(load_folder_name, "tri_gram.json"), "r", encoding="utf-8") as f:
        t_g = ujson.load(f)
    return u_g, b_g, t_g
    

if __name__ == "__main__":
    u_g, b_g, t_g = load_ngram()
    u_g, b_g, t_g = build_new_ngram(u_g, b_g, t_g)

