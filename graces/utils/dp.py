import numpy as np
import ipdb
import math


def dp(s, w, k, c=8, tp='ratio_cut_problem', debug_mode=False):
    if k == 1: return [s]
    if k >= len(s): return list(s)

    # w is diagnoal of W
    # k is cut_count
    # c is max_length_word
    # time complexity: O(nkc)
    if tp != 'ratio_cut_problem':
        s_w = np.cumsum(w)
        #print(s_w)

    n = len(w) + 1
    F = np.ones((n + 1, k + 1)) * 100000
    u = np.zeros((n + 1, k + 1))
    F[0][0] = 0
    if debug_mode:
        print(w)
        print("i cut j")
    for i in range(1, n + 1, 1):
        #print(i, round((i-1)/c)+1, k-n+i, i + 1, k-round((n-i)/c)+ 1)
        for cut in range(max(round((i-1)/c)+1, k-n+i), min(i, k-round((n-i)/c)) + 1):
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
                if tp == 'ratio_cut_problem':
                    cut_part /= j
                else:
                    if i - j - 2 < 0:
                        down = s_w[min(n - 2, i - 1)]
                    else:
                        down = s_w[min(n - 2, i - 1)] - s_w[i - j - 2]
                    """
                    if down < 1e-5:
                        temp = 100000
                    """
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
    assert F[n][k] != 100000, f"No avaliable segment under len:{n}, cut:{k}, max_word_length:{c}"
    seg_list = []
    now = n
    now_cut = k
    cut_set = set()
    while now_cut != 0:
        now -= int(u[now][now_cut])
        now_cut -= 1
        cut_set.update([now])
    ret_s = ""
    for i in range(len(s)):
        ret_s += s[i]
        if i + 1 in cut_set:
            ret_s += " "
    return ret_s.split()

if __name__ == "__main__":
    
    s = "感染的证据"
    w = [5,0.1,0.6,4]
    k = 5
    c = 6
    
    #s = "乙状结肠系膜及腹主动脉旁多发小淋巴结"
    #w = [5.27,5.53,5.86,4.66,5.83,0.13,1.13,1.46,6.48,6.50,0.79,0.26,6.67,1.92,1.99,7.13,6.12]
    #k = 5
    #c = 8
    print(dp(s, w, k, c, debug_mode=True))
    #print(dp(s, w, k, c, debug_mode=True, tp='normal'))
    #print(dp(s, w, k, c, debug_mode=True, tp='mix'))
