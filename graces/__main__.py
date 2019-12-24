import graces
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--input_file", default="")
parser.add_argument("-o", "--output_file", default="")
parser.add_argument("-s", "--sentence", default="")

args = parser.parse_args()
if args.sentence != "":
    print(graces.cut(args.sentence))

if args.input_file != "" and args.output_file != "":
    graces.cut_file(args.input_file, args.output_file)

if args.input_file != "" and args.output_file == "":
    print("No -o output_file")

if args.input_file == "" and args.output_file != "":
    print("No -f input_file")

