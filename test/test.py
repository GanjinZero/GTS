import sys
sys.path.append("../")
import graces

gc = graces.graces(coef_me=0,coef_rm=0,coef_wk=10,coef_xw=1,max_word_length=6)

def cut_weibo_test():
    file_path = "/media/sdc/GanjinZero/NLPCC-WordSeg-Weibo/datasets/nlpcc2016-wordseg-test.dat"
    gc.cut_file(file_path, "./weibo.txt")

def main():
    cut_weibo_test()

if __name__ == "__main__":
    main()
