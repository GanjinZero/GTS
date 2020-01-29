import sys
sys.path.append("../")
from graces import graces
import os

"""
coef_me = 0
coef_rm = 20
coef_wk = 10
coef_xw = 1
gc = graces(coef_me=coef_me,coef_rm=coef_rm,coef_wk=coef_wk,coef_xw=coef_xw,max_word_length=6)
"""

def cut_weibo_test():
    file_path = "/media/sdc/GanjinZero/NLPCC-WordSeg-Weibo/datasets/nlpcc2016-wordseg-test.dat"
    gc.cut_file(file_path, "./weibo.txt")

def cut_icwb2(coef_me, coef_rm, coef_wk, coef_xw):
    gc = graces(coef_me=coef_me,coef_rm=coef_rm,coef_wk=coef_wk,coef_xw=coef_xw,max_word_length=6,bert_model="news")
    output_dir_name = str(coef_me) + "_" + str(coef_rm) + "_" + str(coef_wk) + "_" + str(coef_xw)
    os.system(f"mkdir /media/sdc/GanjinZero/icwb2/graces-result/{output_dir_name}")
    input_path_msr = "/media/sdc/GanjinZero/icwb2/testing/msr_test.utf8"
    output_path_msr = f"/media/sdc/GanjinZero/icwb2/graces-result/{output_dir_name}/msr_bert.txt"
    gc.cut_file(input_path_msr, output_path_msr, method="bert")
    input_path_pku = "/media/sdc/GanjinZero/icwb2/testing/pku_test.utf8"
    output_path_pku = f"/media/sdc/GanjinZero/icwb2/graces-result/{output_dir_name}/pku_bert.txt"
    gc.cut_file(input_path_pku, output_path_pku, method="bert")
    
    """
    import numpy as np
    eig_list = np.linspace(0.1, 2, 20).tolist()
    for eig in eig_list:
        eig_p = '%.1f' % eig
        print(f'Now test: eig={eig_p}')
        gc.change_eig_cut(eig)
        output_path_msr = f"/media/sdc/GanjinZero/icwb2/graces-result/{output_dir_name}/msr_{eig_p}.txt"
        output_path_pku = f"/media/sdc/GanjinZero/icwb2/graces-result/{output_dir_name}/pku_{eig_p}.txt"
        gc.cut_file(input_path_msr, output_path_msr, method='eig_cut')
        gc.cut_file(input_path_pku, output_path_pku, method='eig_cut')
    """

def main():
    #cut_weibo_test()
    cut_icwb2(0,1,10,1)
    #cut_icwb2(0,1,0,0)
    #cut_icwb2(0,0,1,0)
    #cut_icwb2(0,0,0,1)

if __name__ == "__main__":
    main()
