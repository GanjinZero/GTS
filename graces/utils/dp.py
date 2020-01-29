import numpy as np
import math
from .char_judge import is_chinese_not_english
#from char_judge import is_chinese_not_english

def get_split_from_u(s, u, good_cut, k=-1):
    # Need debug or rewrite
    if k == -1:
        checker = True
        for i in good_cut:
            if not checker:
                break
            cut_set = set()
            i_cut = i
            now = len(s)
            while now != 0 and checker:
                if i_cut >= 1 and now >= 2:
                    #print(u[now][i_cut], u[now-1][i_cut-1], s[now-1], s[now-2])
                    if u[now][i_cut] == 1 and u[now-1][i_cut-1] == 1 and is_chinese_not_english(s[now-1]) and is_chinese_not_english(s[now-2]):
                        checker = False
                if checker:
                    now -= int(u[now][i_cut])
                    i_cut -= 1
                    cut_set.update([now])
            if now == 0 and checker:
                k = i
        #print(k, good_cut)
    k = min(max(k, min(good_cut)), max(good_cut))
    
    #assert k in good_cut, f"{k} cut for length {len(s)} is not avalible, good cut:{str(good_cut)}."
    #print(f"Choose {k}.")
    cut_set = set()
    i_cut = k
    now = len(s)
    while now != 0:
        now -= int(u[now][i_cut])
        i_cut -= 1
        cut_set.update([now])

    ret_s = ""
    for i in range(len(s)):
        ret_s += s[i]
        if i + 1 in cut_set:
            ret_s += " "
    return ret_s.split()

def dp(s, w, c=6, k=-1, tp='ratio', debug_mode=False):
    # w is diagnoal of W
    # c is max_length_word
    # time complexity: O(n2c)
    # k=-1 choose by algorithm, k=0 return all, k>0 split to k part
    if tp != 'ratio':
        s_w = np.cumsum(w)

    n = len(w) + 1
    F = np.ones((n + 1, n + 1)) * 999
    u = np.zeros((n + 1, n + 1))
    F[0][0] = 0
    if debug_mode:
        print(w)
        print("i cut i-j")
    for i in range(1, n + 1, 1):
        #print(i, round((i-1)/c)+1, k-n+i, i + 1, k-round((n-i)/c)+ 1)
        #for cut in range(max(round((i-1)/c)+1, k-n+i), min(i, k-round((n-i)/c)) + 1):
        #for cut in range(round((i-1)/c) + 1, i + 1):
        for cut in range(1, i + 1, 1):
            for j in range(1, min(c + 1, i + 1), 1):
                if debug_mode:
                    #print(i, cut, i-j)
                    pass
                temp = F[i - j][cut - 1]
                cut_part = 0
                if i - j > 0:
                    cut_part += w[i - j - 1]
                if i < n:
                    cut_part += w[i - 1]
                if tp == 'ratio':
                    cut_part /= j
                else:
                    if i - j - 2 < 0:
                        down = s_w[min(n - 2, i - 1)]
                    else:
                        down = s_w[min(n - 2, i - 1)] - s_w[i - j - 2]
                    if cut_part > 0:
                        if tp == 'normal':
                            cut_part /= down
                        if tp == 'mix':
                            cut_part /= (down + j)
                temp += cut_part
                if temp < F[i][cut]:
                    u[i][cut] = j
                    F[i][cut] = temp

    if debug_mode:
        np.set_printoptions(precision=2, suppress=True) 
        print(F)
        print(u)
    good_cut = []
    for i in range(1, n + 1, 1):
        if F[n, i] < 999.:
            good_cut.append(i)
    if k != 0:
        return get_split_from_u(s, u, good_cut, k)
    else:
        result = []
        for i in good_cut:
            result.append(get_split_from_u(s, u, good_cut, i))
        return result

if __name__ == "__main__":
    """    
    s = "感染的证据"*2
    w = [5,0.1,0.6,4,0]+[5,0.1,0.6,4]
    c = 6
    
    #s = "乙状结肠系膜及腹主动脉旁多发小淋巴结"
    #w = [5.27,5.53,5.86,4.66,5.83,0.13,1.13,1.46,6.48,6.50,0.79,0.26,6.67,1.92,1.99,7.13,6.12]
    #k = 5
    #c = 8
    print(dp(s[0:2], w[0:1], c, debug_mode=False))
    print(dp(s[0:3], w[0:2], c, debug_mode=False))
    print(dp(s[0:4], w[0:3], c, debug_mode=False))
    print(dp(s[0:5], w[0:4], c, debug_mode=False))
    print(dp(s[0:6], w[0:5], c, debug_mode=False))
    print(dp(s[0:7], w[0:6], c, debug_mode=False))
    print(dp(s[0:8], w[0:7], c, k=2, debug_mode=False))
    #print(dp(s, w, k, c, debug_mode=True, tp='normal'))
    #print(dp(s, w, k, c, debug_mode=True, tp='mix'))
    """
    #print(dp("今天真的是个好天气吗",w,k=-1))
    """
    s = "今2019-3-5我可以战斗"
    w = [1,80,80,80,0,0,0,0,0.1,0,0,0.5,2]
    print(dp(s,w))
    """
    s = "一二三四五六七八九十"
    w = [5,0.1,0.6,4,0]+[5,0.1,0.6,4]
    print(dp(s, w, c=6, k=0, debug_mode=True))
