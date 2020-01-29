import sys
sys.path.append("../")
import graces

graces.gc.change_max_word_length(8)
graces.gc.cut_file_all("/media/sdc/GanjinZero/ccks_cws/ccks100.txt", "/media/sdc/GanjinZero/ccks_cws/graces/ccks100_all.txt")
