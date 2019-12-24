import ipdb
import graces
from graces.utils.visualize_graph import graph_information

def test(s):
    # split first and cut all
    s = "".join(s.split())
    if len(s) > 2:
        w = graces.gc.calculate_sentence(s)
        print(graph_information(s, w))
    print("optimal", graces.gc.cut(s))
    #cut_list = graces.gc.cut_all(s)
    #for cut in cut_list:
    #    print(cut)

test("测试测试功能能否使用？")
test("于 2 0 1 5 - 7 - 1 3")
test("宫 腔内 见 菜花 样 肿物 大小 为 5 * 4 * 3CM")
test("于 2 0 1 1 年 1 0 月 1 1 日")
test("11 月16日 行 TP （ 泰素 + 伯尔定 ） 方案 化疗 2 程")
test("我。")
test("牛逼")
test("GanjinZero")
ipdb.set_trace()

