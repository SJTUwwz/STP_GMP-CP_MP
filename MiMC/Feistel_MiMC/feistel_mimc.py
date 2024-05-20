import math
import subprocess
import time
import os
import sys
from itertools import combinations
sys.path.append("..")

from basic.basic import queryFalse, startSATsolver,solveSTP
from Feistel_MiMC.feistel_mimc_lib import genVariable, genWeightVariable, rangeVariable,  finalConstraint, roundConstraint, MonomialConstraintx, MonomialConstraintxi, NonzeroConstraint, NonzeroConstraintxi

# path of stp and cryptominisat
PATH_CRYPTOMINISAT = "/usr/local/bin/cryptominisat5"
PATH_STP = "/usr/local/bin/stp"


# Search the algebraic degree of Feistel MiMC
#   - mode = 0 : the left branch 
#   - mode = 1 : the right branch

def searchHammingWeightx(n,r,d,testweight,mode):
    stp_file = "./tmp/feistel_mimc_block_%s"%n + "_r%s"%(r) + "_x.cvc"
    
    fw = open(stp_file,"w")

    command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test weight " + "\n"
    
    # generate stp file
    fw.write(command)
    genVariable(n,r,fw)
    genWeightVariable(n,r,fw)
    # rangeVariable(n,r,fw)

    finalConstraint(n,r,fw,mode)
    roundConstraint(n,r,d,fw)

    testdegree = "{:b}".format(testweight)
    testdegree = testdegree.zfill(n)

     # initial constraints
    command = "ASSERT wx = 0bin" + testdegree + ";\n"
    fw.write(command)
    queryFalse(fw)
    fw.close()

    result = solveSTP(stp_file)
    os.remove(stp_file)


    if "Invalid" in result:
        #print("Exist monomial x of weight {}!".format(testweight))
        return 1
    else:
        #print("Non-exsit monomial x of weight {}!".format(testweight))
        return 0


# Search the univariate degree of Feistel MiMC
#   - mode = 0 : the left branch 
#   - mode = 1 : the right branch
#   - xi   = 0 : search univariate degree if x0
#   - xi   = 1 : search univariate degree if x1

def searchHammingWeightxi(n,r,d,testweight,mode,xi):
    
    stp_file = "./tmp/feistel_mimc_block_%s"%n + "_r%s"%(r) + "x%s"%(xi) + ".cvc"
    
    fw = open(stp_file,"w")

    command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test weight " + "\n"
    
    # generate stp file
    fw.write(command)
    genVariable(n,r,fw)
    genWeightVariable(n,r,fw)
    # rangeVariable(n,r,fw)
    finalConstraint(n,r,fw,mode)
    roundConstraint(n,r,d,fw)

    testdegree = "{:b}".format(testweight)
    testdegree = testdegree.zfill(n)

    # initial constraints
    command = "ASSERT wx{} = 0bin".format(xi) + testdegree + ";\n"
    fw.write(command)
    queryFalse(fw)
    fw.close()

    result = solveSTP(stp_file)
    os.remove(stp_file)


    if "Invalid" in result:
        #print("Exist monomial x{} of weight {}!".format(xi,testweight))
        return 1
    else:
        #print("Non-exsit monomial x{} of weight {}!".format(xi,testweight))
        return 0

# Search the monomial of Feistel MiMC
#   - mode = 0 : the left branch 
#   - mode = 1 : the right branch
def searchMonomialx(n,r,d,mode,mon_degree0,mon_degree1):
    stp_file = "./tmp/feistel_mimc_block_%s"%n + "_r%s"%(r) + "_fs0^%s"%(mon_degree0) + "_fs1^%s"%(mon_degree1) + ".cvc"
    
    fw = open(stp_file,"w")

    command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test monomial x0^{}x1^{}".format(mon_degree0, mon_degree1) + "\n"
    
    # generate stp file
    fw.write(command)
    genVariable(n,r,fw)
    # rangeVariable(n,r,fw)
    finalConstraint(n,r,fw,mode)
    roundConstraint(n,r,d,fw)
    NonzeroConstraint(fw,n)

    # initial constraints
    MonomialConstraintx(n,r,d,fw,mon_degree0,mon_degree1)
    queryFalse(fw)
    fw.close()

    result = solveSTP(stp_file)
    os.remove(stp_file)

    # print(result)
    if "Invalid" in result:
        # print("Exist monomial x0^(c0*{})x1^(c1*{})!".format(mon_degree0,mon_degree1))
        return 1
    else:
        # print("Non-exsit monomial x0^(c0*{})x1^(c1*{})!".format(mon_degree0,mon_degree1))
        return 0

# Search the univariate monomial of Feistel MiMC
#   - mode = 0 : the left branch 
#   - mode = 1 : the right branch
#   - xi   = 0 : search univariate monomial if x0
#   - xi   = 1 : search univariate monomial if x1
def searchMonomialxi(n,r,d,mode,mon_degree,xi):
    stp_file = "./tmp/feistel_mimc_block_%s"%n + "_r%s"%(r) + "_x%s"%xi+"^%s"%(mon_degree) + ".cvc"
    
    fw = open(stp_file,"w")

    command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test monomial x{}^{}".format(xi, mon_degree) + "\n"
    
    # generate stp file
    fw.write(command)
    genVariable(n,r,fw)
    # rangeVariable(n,r,fw)
    finalConstraint(n,r,fw,mode)
    roundConstraint(n,r,d,fw)
    NonzeroConstraintxi(fw,n,xi)

    # initial constraints
    MonomialConstraintxi(n,r,d,fw,mon_degree, xi)
    queryFalse(fw)
    fw.close()

    result = solveSTP(stp_file)
    os.remove(stp_file)

    # print(result)
    if "Invalid" in result:
        # print("Exist monomial x{}^(c*{})!".format(xi,mon_degree))
        return 1
    else:
        # print("Non-exsit monomial x{}^(c*{})!".format(xi,mon_degree))
        return 0


d = 3
n = 129
mode = 0
# Round = math.ceil(2 * n * math.log(2)/math.log(d))+3
# print(searchHammingWeightxi(n,1,d,1,mode,1))
# print("Block size : ", n )
# print("Max round number : {}\n".format( Round ))

# for testRound in range(83):

#     # R0 = math.log(pow(2,n-1))/math.log(d) + 1
#     # if testRound < R0:
#     #     maxdegree00 = min(math.floor(math.log(pow(d,testRound)+1)/math.log(2)),n)
#     #     maxdegree10 = min(math.floor(math.log(pow(d,testRound-1)+1)/math.log(2)),n)
#     #     maxdegree = maxdegree00 + maxdegree10
#     # else:
#     #     maxdegree = 2*n-1
#     #     maxdegree00 = n
#     #     maxdegree10 = n

#     # print("maxdegree : {}\t maxdegree00 : {}".format(maxdegree,maxdegree00))
#     # maxdegree = 2*n-1
#     # for testweight in range(maxdegree,0,-1):
#     #     print(testRound, testweight)
#     #     flag = searchHammingWeightx(n,testRound,d,testweight,mode)
#     #     if (flag == 1) :
#     #         print("Test round : {}\tWeight of x = {}".format(testRound,testweight))
#     #         # print("==========================")
#     #         break

#     maxdegree10 = min(math.floor(math.log(pow(d,testRound)+1)/math.log(2)),n)
#     for testweight in range(maxdegree10,0,-1):
#         flag = searchHammingWeightxi(n,testRound,d,testweight,mode,0)
#         if (flag == 1) :
#             print("Test round : {} Weight of x0 = {}".format(testRound,testweight))
#             # print("==========================")
#             break

# t1 = time.time()

# for testweight in range(258,0,-1):
   
#     flag = searchMonomialx(n,124,d,testweight,mode)
#     if (flag == 1) :
#         print("Test round : {}\tWeight of x = {}".format(124,testweight))
#         #print("==========================")
#         break

# print("Cost Time:{}".format(time.time()-t1))

# searchMonomialxi(n, 14, d, mode=0, mon_degree=431*9719, xi=0)

# # Try subgroup of univariate
# Round = math.ceil(n * math.log(2)/math.log(d))
# print("Block size : ", n )
# print("Max round number : {}\n".format( Round ))

# Read direct bound and GMP bound from file
direct_bound = [0]
GMP_bound = [0]
Round = 82
f = open("feistel_output0_x1.txt", "r")
lines = f.readlines()
for i in range(Round):
    tmp_line = lines[i].rstrip("\n")
    tmp_index = tmp_line.find("x1")
    direct_bound.append(min((math.floor(math.log(pow(d,i)+1)/math.log(2)),n)))
    GMP_bound.append(int(tmp_line[tmp_index+5:len(tmp_line)]))
f.close()

# Search all possible subgroup itself(only detect whether x^(c*size) exist)
f = open("record/record_subgroup_x1.txt", 'w')
g = open("record/record_good_subgroup_x1.txt", 'w')
g.write("Good_results\n")
size_list = [7, 431, 9719, 2099863, 11053036065049294753459639]
for i in range(1, len(size_list)):
    print("Element Nuber:{}".format(i))
    for com in combinations(size_list, i):
        mul = 1
        mul_exp = ""
        for elem in com:
            mul *= elem
            mul_exp += str(elem) +" * "
        mul_exp = mul_exp[:-2]
        print("\tTesting subgroup with size {}, LogValue: {:.2f}".format(mul_exp, math.log(mul+1, 2)))
        f.write("Testing subgroup with size {}, LogValue: {:.2f}\n".format(mul_exp, math.log(mul+1, 2)))
        begin_round = math.floor(math.log(mul, d))
        before_flag = 1
        for test_round in range(begin_round, min((begin_round+5, Round))):
            flag = searchMonomialxi(n, test_round, d, mode=0, mon_degree=mul, xi=1)
            print("Round: {}, Direct_bound: {}, GMP_bound: {}, Exist_mon: {}".format(test_round, direct_bound[test_round], GMP_bound[test_round], flag))
            f.write("Round: {}, Direct_bound: {}, GMP_bound: {}, Exist_mon: {} \n".format(test_round, direct_bound[test_round], GMP_bound[test_round], flag))
            if flag:
                if (before_flag == 0) and (math.log(mul+1, 2) < GMP_bound[test_round-1]+1):
                    g.write("Subgroup with size {}, Round: {}, LogValue: {:.2f}, GMP_bound: {}\n".format(mul_exp, test_round-1, math.log(mul, 2), GMP_bound[test_round-1]))
                break
            before_flag = flag
    f.write("\n")
f.close()
g.close()

# # Try subgroup of multivariate (THIS PART only find trivial distinguishers)
# Round = 110
# print("Block size : ", n )
# print("Max round number : {}\n".format( Round ))
# direct_bound = [1]
# GMP_bound = [1]
# f = open("feistel_cjm_output.txt", "r")
# lines = f.readlines()
# for i in range(Round*4):
#     if i % 4 == 0:
#         tmp_line = lines[i].rstrip("\n")
#         tmp_index = tmp_line.find("maxdegree00")
#         # print(tmp_line[tmp_index:len(tmp_line)], tmp_line[tmp_index+14:len(tmp_line)])
#         direct_bound.append(int(tmp_line[tmp_index+14:len(tmp_line)]))
#     if i % 4 == 1:
#         tmp_line = lines[i].rstrip("\n")
#         tmp_index = tmp_line.find("x")
#         # print(tmp_line[tmp_index:len(tmp_line)], tmp_line[tmp_index+5:len(tmp_line)])
#         GMP_bound.append(int(tmp_line[tmp_index+4:len(tmp_line)]))
# f.close()

# # # original subgroup find
# # f = open("record/record_subgroup_mul.txt", 'w')
# # g = open("record/record_good_subgroup_mul.txt", 'w')
# # g.write("Good_results\n")
# # size_list = [7, 431, 9719, 2099863, 11053036065049294753459639]
# # # traverse x0 subgroup
# # for i in range(1, len(size_list)):
# #     print("Element Nuber of x0 subgroup:{}".format(i))
# #     for com0 in combinations(size_list, i):
# #         mul0 = 1
# #         mul_exp0 = ""
# #         for elem in com0:
# #             mul0 *= elem
# #             mul_exp0 += str(elem) +" * "
# #         mul_exp0 = mul_exp0[:-2]
# #         print("\tTesting subgroup of x0 with size {}, LogValue: {:.2f}".format(mul_exp0, math.log(mul0+1, 2)))
# #         # f.write("Testing subgroup with of x0 size {}, LogValue: {:.2f}\n".format(mul_exp, math.log(mul+1, 2)))
# #         begin_round0 = math.floor(math.log(mul0, d))
# #         # traverse x1 subgroup
# #         for j in range(1, len(size_list)):
# #             print("Element Nuber of x1 subgroup:{}".format(j))
# #             for com1 in combinations(size_list, j):
# #                 mul1 = 1
# #                 mul_exp1 = ""
# #                 for elem in com1:
# #                     mul1 *= elem
# #                     mul_exp1 += str(elem) +" * "
# #                 mul_exp1 = mul_exp1[:-2]
# #                 print("\tTesting subgroup of x1 with size {}, LogValue: {:.2f}".format(mul_exp1, math.log(mul1+1, 2)))
# #                 f.write("Testing subgroup with size [{},{}], LogValue: [{:.2f},{:.2f}]\n".format(mul_exp0, mul_exp1,  math.log(mul0+1, 2), math.log(mul1+1, 2)))
# #                 before_flag = 1
# #                 begin_round1 = math.floor(math.log(mul1, d))
# #                 begin_round = max((begin_round0, begin_round1))
# #                 for test_round in range(begin_round, min((begin_round+5, Round))):
# #                     flag = searchMonomialx(n, test_round, d, mode=0, mon_degree0=mul0, mon_degree1=mul1)
# #                     f.write("Round: {}, Direct_bound: {}, GMP_bound: {}, Exist_mon: {} \n".format(test_round, direct_bound[test_round], GMP_bound[test_round], flag))
# #                     if (before_flag == 0) and (flag == 1):
# #                         if math.log((mul0+1)*(mul1+1), 2) < GMP_bound[test_round-1]+1:
# #                             g.write("Subgroup with size [{},{}], Round: {}, LogValue: [{:.2f},{:.2f}], GMP_bound: {}\n".format(mul_exp0, mul_exp1, test_round-1, math.log(mul0+1, 2), math.log(mul1+1, 2), GMP_bound[test_round-1]))
# #                         break
# #                     before_flag = flag
# #             f.write("\n")
# #     f.write("=======================================================\n")
# # f.close()
# # g.close()

# # new subgroup find
# f = open("record/record_subgroup_mul2.txt", 'w')
# g = open("record/record_good_subgroup_mul2.txt", 'w')
# h = open("record/record_mistake2.txt", "w")
# g.write("Good_results\n")
# size_list = [7, 431, 9719, 2099863, 11053036065049294753459639]
# # traverse x0 subgroup
# for i in range(1, len(size_list)):
#     print("Element Nuber of x0 subgroup:{}".format(i))
#     for com0 in combinations(size_list, i):
#         mul0 = 1
#         mul_exp0 = ""
#         for elem in com0:
#             mul0 *= elem
#             mul_exp0 += str(elem) +" * "
#         mul_exp0 = mul_exp0[:-2]
#         print("\tTesting subgroup of x0 with size {}, LogValue: {:.2f}".format(mul_exp0, math.log(mul0+1, 2)))
#         # f.write("Testing subgroup with of x0 size {}, LogValue: {:.2f}\n".format(mul_exp, math.log(mul+1, 2)))
#         begin_round0 = math.floor(math.log(mul0, d))
#         # traverse x1 subgroup
#         for j in range(1, len(size_list)):
#             print("Element Nuber of x1 subgroup:{}".format(j))
#             for com1 in combinations(size_list, j):
#                 mul1 = 1
#                 mul_exp1 = ""
#                 for elem in com1:
#                     mul1 *= elem
#                     mul_exp1 += str(elem) +" * "
#                 mul_exp1 = mul_exp1[:-2]
#                 if mul1 > mul0:
#                     continue
#                 print("\tTesting subgroup of x1 with size {}, LogValue: {:.2f}".format(mul_exp1, math.log(mul1+1, 2)))
#                 f.write("Testing subgroup with size [{},{}], LogValue: [{:.2f},{:.2f}]\n".format(mul_exp0, mul_exp1,  math.log(mul0+1, 2), math.log(mul1+1, 2)))
#                 before_flag = 1
#                 begin_round1 = math.floor(math.log(mul1, d))
#                 begin_round = max((begin_round0, begin_round1))
#                 for test_round in range(begin_round, min((begin_round+5, Round))):
#                     try:
#                         flag = searchMonomialx(n, test_round, d, mode=0, mon_degree0=mul0, mon_degree1=mul1)
#                     except Exception as e:
#                         h.write("Round: {}, Subgroup with size [{},{}], Error: {}\n".format(test_round, mul_exp0, mul_exp1, e))
#                         break
#                     else:
#                         f.write("Round: {}, Direct_bound: {}, GMP_bound: {}, Exist_mon: {} \n".format(test_round, direct_bound[test_round], GMP_bound[test_round], flag))
#                         if (before_flag == 0) and (flag == 1):
#                             if math.log((mul0+1)*(mul1+1), 2) < GMP_bound[test_round-1]+1:
#                                 g.write("Subgroup with size [{},{}], Round: {}, LogValue: [{:.2f},{:.2f}], GMP_bound: {}\n".format(mul_exp0, mul_exp1, test_round-1, math.log(mul0+1, 2), math.log(mul1+1, 2), GMP_bound[test_round-1]))
#                             break
#                         before_flag = flag
#             f.write("\n")
#     f.write("=======================================================\n")
# f.close()
# g.close()
# h.close()

# Try subgroup of multivariate deg(x0)=129
# Round = 124
# print("Block size : ", n )
# print("Max round number : {}\n".format( Round ))
# direct_bound = [1]
# GMP_bound = [1]
# f = open("feistel_output_R0.txt", "r")
# lines = f.readlines()
# for i in range(len(lines)):
#     tmp_line = lines[i].rstrip("\n")
#     tmp_index = tmp_line.find("x")
#     # print(tmp_line[tmp_index:len(tmp_line)], tmp_line[tmp_index+5:len(tmp_line)])
#     GMP_bound.append(int(tmp_line[tmp_index+4:len(tmp_line)]))
# f.close()
# print(len(GMP_bound), GMP_bound)
# f = open("record/record_R0.txt", 'w')
# g = open("record/record_good_R0.txt", 'w')
# h = open("record/record_mistake_R0.txt", "w")
# g.write("Good_results\n")
# size_list = [7, 431, 9719, 2099863, 11053036065049294753459639]
# for com in combinations(size_list, 4):
#     mul = 1
#     mul_exp = ""
#     for elem in com:
#         mul *= elem
#         mul_exp += str(elem) +" * "
#     mul_exp = mul_exp[:-2]
#     print("\tTesting subgroup with size {}, LogValue: {:.2f}".format(mul_exp, math.log(mul+1, 2)))
#     f.write("Testing subgroup with size {}, LogValue: {:.2f}\n".format(mul_exp, math.log(mul+1, 2)))
#     begin_round = 82
#     if com == (431, 9719, 2099863, 11053036065049294753459639):
#         begin_round = 100
#     before_flag = 1
#     for test_round in range(begin_round, 125):
#         try:
#             flag = searchMonomialx(n, test_round, d, mode=0, mon_degree0=mul, mon_degree1=int(2**n-1))
#             print("Round:{}, Exist_mon:{}".format(test_round, flag))
#         except Exception as e:
#             h.write("Round: {}, Subgroup with size [{},2**129], Error: {}\n".format(test_round, mul_exp, e))
#             break
#         else:
#             f.write("Round: {}, Direct_bound: {}, GMP_bound: {}, Exist_mon: {} \n".format(test_round, 257, GMP_bound[test_round], flag))
#             if flag == 1:
#                 if (before_flag == 0) and (math.log(mul+1, 2) < GMP_bound[test_round-1]-129+1):
#                     g.write("Subgroup with size [{},2**129], Round: {}, LogValue: [129.00 ,{:.2f}], GMP_bound: {}\n".format(mul_exp, test_round-1, math.log(mul+1, 2), GMP_bound[test_round-1]))
#                 break
#             before_flag = flag
# f.close()
# g.close()
# h.close()
# mul = 431 * 9719 * 2099863 * 11053036065049294753459639
# print("Subgroup size :({}, 2^129)".format(mul))
# for i in range(90, 100):
#     flag = searchMonomialx(n, i, d, mode=0, mon_degree1=int(2**n-1), mon_degree0=mul)
#     print("Round:{}, Exist_mon:{}".format(i, flag))
#     if flag:
#         break

# try:
#     flag = searchMonomialxi(n, 52, d, mode=0, mon_degree=11053036065049294753459639, xi=0)
# except Exception as e:
#     print(e)
#     print("fail to solve!")
# else:
#     print(flag)
#     print("Succeed!")