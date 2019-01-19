#!/usr/bin/env python3
#
# ./ocr.py : Perform optical character recognition, usage:
#     ./ocr.py train-image-file.png train-text.txt test-image-file.png
#
# (based on skeleton code by D. Crandall, Oct 2018)
# Report: Enclosed in the folder
#

from PIL import Image, ImageDraw, ImageFont
import sys
import math

CHARACTER_WIDTH=14
CHARACTER_HEIGHT=25


def load_letters(fname):
    im = Image.open(fname)
    px = im.load()
    (x_size, y_size) = im.size
    #print(im.size)
    #print(int(x_size / CHARACTER_WIDTH) * CHARACTER_WIDTH)
    result = []
    for x_beg in range(0, int(x_size / CHARACTER_WIDTH) * CHARACTER_WIDTH, CHARACTER_WIDTH):
        result += [ [ "".join([ '*' if px[x, y] < 1 else ' ' for x in range(x_beg, x_beg+CHARACTER_WIDTH) ]) for y in range(0, CHARACTER_HEIGHT) ], ]
    return result

def load_training_letters(fname):
    TRAIN_LETTERS="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789(),.-!?\"' "
    letter_images = load_letters(fname)
    return { TRAIN_LETTERS[i]: letter_images[i] for i in range(0, len(TRAIN_LETTERS) ) }

#####
# main program
(train_img_fname, train_txt_fname, test_img_fname) = sys.argv[1:]
train_letters = load_training_letters(train_img_fname)
test_letters = load_letters(test_img_fname)


## Below is just some sample code to show you how the functions above work.
# You can delete them and put your own code here!


# Each training letter is now stored as a list of characters, where black
#  dots are represented by *'s and white dots are spaces. For example,
#  here's what "a" looks like:
#print("\n".join([ r for r in train_letters['a'] ]))

# Same with test letters. Here's what the third letter of the test data
#  looks like:
#print("\n".join([ r for r in test_letters[2] ]))

def emission(test_index,train_index):
    TRAIN_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789(),.-!?\"' "
    tst = test_letters[test_index]
    ch=train_letters.get(TRAIN_LETTERS[train_index])
    emi=1
    found=0
    for i in range(len(tst)):
     for j in range(len(tst[i])):
            if tst[i][j] == ch[i][j]:
             emi=emi*0.9
             found=found+1
            else:
             emi =emi*0.1
    #return float(found)/(25*14)
    return emi

def find_sentence():
    global initial
    global transition
    global test_letters
    global intial_count
    got_from_list={}
    possibility={}
    global viterbi
    TRAIN_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789(),.-!?\"' "
    for test_index in range(len(test_letters)):
        if test_index==0:
            v = 0
            s = {}
            for train_indes in range(len(TRAIN_LETTERS)):
                if TRAIN_LETTERS[train_indes] in initial.keys():
                    v=math.log((float(initial[TRAIN_LETTERS[train_indes]])/intial_count))+math.log(float(emission(test_index,train_indes)));
                else:
                    v = math.log(float(1)/intial_count)+ math.log(float(emission(test_index, train_indes)));
                s[train_indes]=v;
            possibility[test_index]=s
        else:
            v = 0
            s = {}
            largest_prob=float("-inf")
            intermediate=-1
            got_from={}
            for train_index_inside in range(len(TRAIN_LETTERS)):
                for train_index in range(len(TRAIN_LETTERS)):
                    trans=TRAIN_LETTERS[train_index],TRAIN_LETTERS[train_index_inside]
                    if trans in transition.keys():
                        v=math.log(float(transition[trans])/transition_count)+possibility[test_index-1][train_index]
                    else:
                        v =math.log(float(1)/transition_count) + possibility[test_index - 1][train_index]
                    if largest_prob<v:
                        largest_prob=v
                        intermediate=train_index
                largest_prob=largest_prob+math.log(float(emission(test_index,train_index_inside)))
                s[train_index_inside]=largest_prob
                got_from[train_index_inside]=intermediate
                largest_prob=float("-inf")

            possibility[test_index]=s
            got_from_list[test_index]=got_from
    maxima=float("-inf")
    index=-1
    last_index=-1
    i=len(test_letters)-1
    printer=[]
    for j in range(len(TRAIN_LETTERS)):
        if maxima<possibility[i][j]:
           maxima=possibility[i][j]
           index=got_from_list[i][j]
           last_index=j
    printer.append(TRAIN_LETTERS[last_index])

    for i in range(len(test_letters)-2,-1,-1):
        printer.append(TRAIN_LETTERS[index])
        if i>0:
            index=got_from_list[i][index]
    #for i in reversed(printer):
    #   print(i+" ",end="")
    viterbi=''.join(reversed(printer))

def find_simple():
    global simple
    TRAIN_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789(),.-!?\"' "
    res = []
    for test_index in range(len(test_letters)):
        lis = []
        prev_value=float('-inf')
        for train_indes in range(len(TRAIN_LETTERS)):
            lis.append(emission(test_index, train_indes));

            if prev_value<max(lis):
                prev_value=max(lis)
                val=TRAIN_LETTERS[train_indes]
        res.append(val)
    simple=''.join(res)


viterbi=''
simple=''
def best_matcher():
    maxi = 0
    global simple
    global viterbi
    global best_match

    f1 = open(sys.argv[2], "r")
    for line in f1:
        simple_count = 0
        viterbi_count = 0
        for i in range(len(line)):
            if i < len(simple):
                if simple[i] == line[i]:
                    simple_count = simple_count + 1
            if i < len(viterbi):
                if viterbi[i] == line[i]:
                    viterbi_count = viterbi_count + 1
        if maxi < simple_count or maxi <= viterbi_count:
            # print(maxi)
            # print(viterbi_count)
            # print(simple_count)
            if simple_count <= viterbi_count and maxi <= viterbi_count:
                maxi = viterbi_count
                best_match = viterbi


            elif viterbi_count < simple_count and maxi < simple_count:
                maxi = simple_count
                best_match = simple


#initial=[]
transition=dict()
initial=dict()
intial_count=0
transition_count=0
#print("hey")
f = open(sys.argv[2],"r")
for line in f:
    if line[0] in initial:
        initial[line[0]]=initial[line[0]]+1
    else:
        initial[line[0]]=1
    intial_count=intial_count+1
    for i in range(len(line)-1):
        a=line[i],line[i+1]
        if a in transition:
            transition[a]=transition[a]+1
        else:
            transition[a]= 1
        transition_count=transition_count+1

best_match=''
find_sentence()
find_simple()
print("Simple :",simple)
print("Viterbi:",viterbi)
best_matcher()
print("Final answer:",best_match)
