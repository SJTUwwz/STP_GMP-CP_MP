import math
import subprocess
import time
import os
import sys
from itertools import combinations
sys.path.append("..")

from basic.basic import queryFalse, startSATsolver,solveSTP
from MiMC.mimc_lib import genVariable, genWeightVariable, rangeVariable, finalConstraint, roundConstraint, gcd, MonomialConstraint, CertainMonomialConstraint

# path of stp and cryptominisat
PATH_CRYPTOMINISAT = "/usr/local/bin/cryptominisat5"
PATH_STP = "/usr/local/bin/stp"

 
# search the algebraic degree of MiMC

def searchHammingWeight(n,r,d,testweight):
    stp_file = "./tmp/mimc_block_%s"%n + "_d%s"%(d) + "_r%s"%(r)+".cvc"
    
    fw = open(stp_file,"w")
    command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test weight " + "\n"
    
    # generate stp file
    fw.write(command)
    genVariable(n,r,fw)
    genWeightVariable(n,r,fw)
    rangeVariable(n,r,fw)
    finalConstraint(n,r,fw)
    roundConstraint(n,r,d,fw)

    testdegree = "{:b}".format(testweight)
    testdegree = testdegree.zfill(n)

    # initial constraints
    command = "ASSERT wx = 0bin" + testdegree + ";\n"
    fw.write(command)
    queryFalse(fw)
    fw.close()

    result = solveSTP(stp_file)
    # print(result)
    os.remove(stp_file)
   
    if "Invalid" in result:
        # print("Exsit x^({})".format(testweight))
        return 1
    else:
        # print("Non-exsit x^({})".format(testweight))
        return 0

def searchMonomial(n,r,d,mon_degree):
    stp_file = "./subfield/mimc_block_%s"%n + "_d%s"%(d) + "_r%s"%(r)+"_fs%s"%(mon_degree)+".cvc"
    
    fw = open(stp_file,"w")
    command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test monomial " + "\n"
    
    # generate stp file
    fw.write(command)
    genVariable(n,r,fw)
    # genWeightVariable(n,r,fw)
    rangeVariable(n,r,fw)
    finalConstraint(n,r,fw)
    roundConstraint(n,r,d,fw)

    # initial constraints
    MonomialConstraint(n,r,d,fw,mon_degree)
    queryFalse(fw)
    fw.close()

    result = solveSTP(stp_file)
    # print(result)
    os.remove(stp_file)
   
    if "Invalid" in result:
        # print("Exsit x^(c*{})".format(mon_degree))
        return 1
    else:
        # print("Non-Exsit x^(c*{})".format(mon_degree))
        return 0

def searchCertainMonomial(n,r,d,mon_degree):
    stp_file = "./tmp/mimc_block_%s"%n + "_d%s"%(d) + "_r%s"%(r)+"_x^%s"%(mon_degree)+".cvc"
    
    fw = open(stp_file,"w")
    command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test monomial " + "\n"
    
    # generate stp file
    fw.write(command)
    genVariable(n,r,fw)
    # genWeightVariable(n,r,fw)
    rangeVariable(n,r,fw)
    finalConstraint(n,r,fw)
    roundConstraint(n,r,d,fw)

    # initial constraints
    CertainMonomialConstraint(n,r,d,fw,mon_degree)
    queryFalse(fw)
    fw.close()

    result = solveSTP(stp_file)
    # print(result)
    os.remove(stp_file)
   
    if "Invalid" in result:
        # print("Exsit x^({})".format(mon_degree))
        return 1
    else:
        # print("Non-Exsit x^({})".format(mon_degree))
        return 0
        

d = 33
n = 129
Round = math.ceil(n * math.log(2)/math.log(d))+1
print("Round function power: ", d)
print("Block size : ", n )
print("Max round number : {}\n".format( Round ))

# if (gcd(pow(2,n)-1,d)) == 1:

#     for testRound in range(80, Round + 1):
        
#         print("Test round number : ", testRound )
        
#         if testRound <= 81:
#             maxdegree = math.floor (math.log(pow(d,testRound)+1)/math.log(2))
#         else:
#             maxdegree = n-1
#         for testweight in range(maxdegree,0,-1):
#             #print("Test weight : ",testweight)
#             flag = searchMonomial(n,testRound,d,testweight)
#             if (flag == 1) :
#                 print("Test round : {}\tWeight = {}\n".format(testRound,testweight))
#                 print("==========================")
#                 break

# for testRound in range(28, 32):
#     maxdegree = math.floor (math.log(pow(d,testRound)+1)/math.log(2))
#     print("maxdegree for {} Round is {}".format(testRound, maxdegree))
#     for testweight in range(maxdegree,0,-1):
#         #print("Test weight : ",testweight)
#         flag = searchHammingWeight(n,testRound,d,testweight)
#         if flag == 1:
#             print("Test round : {}\tWeight = {}\n".format(testRound,testweight))
#             print("==========================")
#             if testweight >= 43:
#                 newflag = searchMonomial(n,testRound,d,43)
#             break

# Get the direct algebraic degree and GMP algebraic degree
# f = open("mimc_degree_129/mimc_degree_129_{}.txt".format(d), "w")
# for i in range(Round):
#     maxdegree = math.floor (math.log(pow(d,i)+1)/math.log(2))
#     for testweight in range(maxdegree,0,-1):
#         flag = searchHammingWeight(n,i,d,testweight)
#         if flag == 1:
#             print("round:{}, maxdegree:{}, maxhammingweight:{}".format(i, maxdegree, testweight))
#             f.write("round:{}, maxdegree:{}, maxhammingweight:{}\n".format(i, maxdegree, testweight))
#             break
# f.close()

# size_list = [7, 431, 9719, 2099863, 11053036065049294753459639]
# for i in range(73, 76):
#     print("round:{}".format(i))
#     searchMonomial(n, i, d, 7 * 431 * 2099863 * 11053036065049294753459639)
#     print("==========================\n")

direct_bound = []
GMP_bound = []
g = open("mimc_degree_129/mimc_degree_129_{}.txt".format(d), "r")
lines = g.readlines()
for line in lines:
    line = line.rstrip("\n")
    aindex = line.find("maxdegree:")
    bindex = line.find(", maxhammingweight:")
    # print(line[aindex+10:bindex], line[bindex+19:len(line)])
    direct_bound.append(int(line[aindex+10:bindex]))
    GMP_bound.append(int(line[bindex+19:len(line)]))
g.close()

# Search all possible subgroup itself(only detect whether x^(c*size) exist)
f = open("record/record_subgroup_d{}.txt".format(d), 'w')
g = open("record/record_good_subgroup_d{}.txt".format(d), 'w')
g.write("Good_results_for_degree:{}\n".format(d))
size_list = [7, 431, 9719, 2099863, 11053036065049294753459639]
for i in range(1, len(size_list)+1):
    print("Element Nuber:{}".format(i))
    for com in combinations(size_list, i):
        mul = 1
        mul_exp = ""
        for elem in com:
            mul *= elem
            mul_exp += str(elem) +" * "
        mul_exp = mul_exp[:-2]
        print("\tTesting subgroup with size {}, LogValue: {:.2f}".format(mul_exp, math.log(mul, 2)))
        f.write("Testing subgroup with size {}, LogValue: {:.2f}\n".format(mul_exp, math.log(mul, 2)))
        begin_round = math.floor(math.log(mul, d))
        before_flag = 1
        for test_round in range(begin_round, min((begin_round+5, Round))):
            flag = searchMonomial(n, test_round, d, mul)
            f.write("Round: {}, Direct_bound: {}, GMP_bound: {}, Exist_mon: {} \n".format(test_round, direct_bound[test_round], GMP_bound[test_round], flag))
            if (before_flag == 0) and (flag == 1):
                if math.log(mul, 2) < GMP_bound[test_round-1]+1:
                    g.write("Subgroup with size {}, Round: {}, LogValue: {:.2f}, GMP_bound: {}\n".format(mul_exp, test_round-1, math.log(mul, 2), GMP_bound[test_round-1]))
                break
            before_flag = flag
    f.write("\n")
f.close()
g.close()

# Detect certain monomial exactly
f = open("record/record_subgroup_mon_d{}.txt".format(d), 'w')
size_list = [7, 431, 9719, 2099863, 11053036065049294753459639]
for i in range(1, len(size_list)+1):
    print("Element Nuber:{}".format(i))
    for com in combinations(size_list, i):
        mul = 1
        mul_exp = ""
        for elem in com:
            mul *= elem
            mul_exp += str(elem) +" * "
        mul_exp = mul_exp[:-2]
        print("\tTesting subgroup with size {}, LogValue: {:.2f}".format(mul_exp, math.log(mul, 2)))
        f.write("Testing subgroup with size {}, LogValue: {:.2f}\n".format(mul_exp, math.log(mul, 2)))
        test_round = math.ceil(math.log(mul, d))
        max_len_contain_times = 0
        while max_len_contain_times <= 3:
            times = 1
            contain_times = []
            if test_round >= Round:
                break
            upper_index = min((d ** test_round, 2**129-1))
            # print(times * mul <= upper_index, upper_index)
            while times * mul <= upper_index:
                flag = searchCertainMonomial(n, test_round, d, times * mul)
                # print(times, flag)
                if flag:
                    contain_times.append(times)
                times += 1
            f.write("Round: {}, Direct_bound: {}, GMP_bound: {}, Cor_mon: {} \n".format(test_round, direct_bound[test_round], GMP_bound[test_round], str(contain_times)))
            test_round += 1
            max_len_contain_times = max((max_len_contain_times, len(contain_times)))
    f.write("\n")
f.close()

# mul = 7
# for test_round in range(2, 8):
#     times = 1
#     contain_times = []
#     if test_round > 82:
#         break
#     upper_index = min((d ** test_round, 2**129-1))
#     # print(times * mul <= upper_index, upper_index)
#     while times * mul <= upper_index:
#         flag = searchCertainMonomial(n, test_round, d, times * mul)
#         # print(times, flag)
#         if flag:
#             contain_times.append(times)
#         times += 1
#     print(test_round, contain_times)

# a = 7 * 431 * 9719 * 2099863 * 11053036065049294753459639
# print(len("{:b}".format(a).zfill(129)), "{:b}".format(a).zfill(129))
# print(math.log(a, 2))
