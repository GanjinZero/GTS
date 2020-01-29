import sys
sys.path.append("../")
from graces import graces

gc = graces(coef_me=1,coef_rm=0,coef_wk=0,coef_xw=0,max_word_length=6,tp='normal')
gc.cut_file("/media/sdc/GanjinZero/ccks_cws/ccks100.txt", "/media/sdc/GanjinZero/ccks_cws/graces/ccks100_bert_ablation.txt", method="bert")
