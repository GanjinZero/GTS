import sys
sys.path.append("../")
import graces

graces.cut_file("/media/sdc/GanjinZero/ccks_cws/ccks100.txt", "/media/sdc/GanjinZero/ccks_cws/graces/ccks100_graces.txt")
graces.cut_file("/media/sdc/GanjinZero/ccks_cws/ccks100.txt", "/media/sdc/GanjinZero/ccks_cws/graces/ccks100_eig_1.txt", method="eig_cut")
