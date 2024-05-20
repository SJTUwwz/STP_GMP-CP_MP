import math
import subprocess
import time
import os
import sys
from itertools import combinations
sys.path.append("..")

from basic.basic import queryFalse, startSATsolver, solveSTP
from CIMINION.ciminion_lib import genVar, genWeightVar, genWeightVarxi, rangeVar, finalConstraint, NonzeroConstraint, roundConstraint, MonomialConstraintx, MonomialConstraintxi, NonzeroConstraintxi, CertainMonomialConstraintxi

# path of stp and cryptominisat
PATH_CRYPTOMINISAT = "/usr/local/bin/cryptominisat5"
PATH_STP = "/usr/local/bin/stp"

def searchHammingWeightx(n, r, testweight, mode):
	stp_file = "./tmp/ciminion_%s"%n + "_r%s"%r + "_x%s"%(xi) + ".cvc"
	fw = open(stp_file, "w")
	command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test weight " + "\n"

	fw.write(command)
	genVar(n, r, fw)
	genWeightVar(n, r, fw)
	finalConstraint(n, r, fw, mode)
	roundConstraint(n, r, fw)

	testdegree = "{:b}".format(testweight)
	testdegree = testdegree.zfill(n)
	command = "ASSERT wx = 0bin" + testdegree + ";\n"
	fw.write(command)
	queryFalse(fw)
	fw.close()
	result = solveSTP(stp_file)
	os.remove(stp_file)
	print(result)
	if "Invalid" in result:
		return 1
	else:
		return 0


def searchHammingWeightxi(n, r, testweight, mode, xi):
	stp_file = "./tmp/ciminion_%s"%n + "_r%s"%r + "_x%s"%(xi) + ".cvc"
	fw = open(stp_file, "w")
	command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test weight = " + str(testweight) + "\n"

	fw.write(command)
	genVar(n, r, fw)
	genWeightVarxi(n, r, fw, xi)
	finalConstraint(n, r, fw, mode)
	roundConstraint(n, r, fw)

	testdegree = "{:b}".format(testweight)
	testdegree = testdegree.zfill(n)
	if xi == 0:
		command = "ASSERT wxa = 0bin" + testdegree + ";\n"
	elif xi == 1:
		command = "ASSERT wxb = 0bin" + testdegree + ";\n"
	else:
		command = "ASSERT wxc = 0bin" + testdegree + ";\n"
	fw.write(command)
	queryFalse(fw)
	fw.close()
	result = solveSTP(stp_file)
	os.remove(stp_file)
	# print(result)
	if "Invalid" in result:
		return 1
	else:
		return 0

def searchMonomialxi(n, r, mon_exp, mode, xi):
	stp_file = "./tmp/Monomial_ciminion_n%s_r%s_i%s_o%s_x%s.cvc"%(n, r, xi, mode, mon_exp)
	fw = open(stp_file, "w")
	command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test exponent =" + str(mon_exp) + "\n"
	fw.write(command)

	genVar(n, r, fw)
	finalConstraint(n, r, fw, mode)
	roundConstraint(n, r, fw)
	NonzeroConstraintxi(fw, n, xi)

	MonomialConstraintxi(n, r, fw, mon_exp, xi)
	queryFalse(fw)
	fw.close()

	result = solveSTP(stp_file)
	os.remove(stp_file)

	if "Invalid" in result:
		return 1
	else:
		return 0

def searchCertainMonomialxi(n, r, mon_exp, mode, xi):
	stp_file = "./tmp/Monomial_certain_ciminion_n%s_r%s_i%s_o%s_x%s.cvc"%(n, r, xi, mode, mon_exp)
	fw = open(stp_file, "w")
	command = "%Block size: " + str(n) + "\n%Round = " + str(r) + "\n%Test exponent =" + str(mon_exp) + "\n"
	fw.write(command)

	genVar(n, r, fw)
	finalConstraint(n, r, fw, mode)
	roundConstraint(n, r, fw)
	# NonzeroConstraintxi(fw, n, xi)

	CertainMonomialConstraintxi(n, r, fw, mon_exp, xi)
	queryFalse(fw)
	fw.close()

	result = solveSTP(stp_file)
	os.remove(stp_file)

	if "Invalid" in result:
		return 1
	else:
		return 0



n = 64
mode = 2
xi = 0
Round = 70

# test function searchHammingWeightxi
# t1 = time.time()
# print(searchHammingWeightxi(n, 65, 63, mode, xi))
# print("Time for solving: ", time.time()-t1)
# estimate algebraic degree by GMP
f = open("record_result/CIMINION_algebraic_degree_n%s_i%s_o%s3.txt"%(n, xi, mode), "w")
exist_deg = [0, 1] + [i for i in range(1, 65)] + [64, 64, 64, 64, 64]
f.write("Round:\tPre_est\tPre_est_flag\n")
for i in range(0, Round):
	if i == 0:
		f.write("0\t0\t0\n")
	else:
		t1 = time.time()
		flag = searchHammingWeightxi(n, i, exist_deg[i], mode, xi)
		t2 = time.time()
		print(i, exist_deg[i], "Flag: ", flag, "Used Time:", t2-t1)
		f.write("%s\t%s\t%s\n"%(i, exist_deg[i], flag))
f.close()

# # test function searchMonomialxi
# for i in range(17):
# 	print("x^{}".format(i), searchMonomialxi(n, 4, i, mode, xi))

# read bound from file
# direct_bound = []
# GMP_bound = []
# f = open("record_result/estimated_result.txt")
# lines = f.readlines()
# for i in range(1, len(lines)):
# 	tmp_line = lines[i].rstrip("\n")
# 	tmp_list = tmp_line.split("\t")
# 	# print(tmp_list)
# 	direct_bound.append(int(tmp_list[1]))
# 	GMP_bound.append(int(tmp_list[2]))
# f.close()


# # 2**64-1 = 3 * 5 * 17 * 257 * 641 * 65537 * 6700417
# # Use multiplicative subgroup to find integral distinguisher
# f = open("record_result/all_subgroup_n%s_i%s_o%s.txt"%(n, xi, mode), "w")
# g = open("record_result/good_subgroup_n%s_i%s_o%s.txt"%(n, xi, mode), "w")
# g.write("Good results\n")
# factor_list = [3, 5, 17, 257, 641, 65537, 6700417]
# for i in range(1, len(factor_list)):
# 	print("Factor Number:{}".format(i))
# 	for com in combinations(factor_list, i):
# 		mul = 1
# 		mul_exp = ""
# 		for elem in com:
# 			mul *= elem
# 			mul_exp += str(elem) + " * "
# 		mul_exp = mul_exp[:-2]
# 		print("\tTesting subgroup with size {}, LogValue: {:.2f}".format(mul_exp, math.log(mul+1, 2)))
# 		f.write("Testing subgroup with size {}, LogValue: {:.2f}\n".format(mul_exp, math.log(mul+1, 2)))
# 		begin_round = math.ceil(math.log(mul, 2))
# 		before_flag = 1
# 		for test_round in range(begin_round, min((begin_round+5, Round))):
# 			flag = searchMonomialxi(n, test_round, mul, mode, xi)
# 			print("Round: {}, Direct_bound: {}, GMP_bound: {}, Exist_mon: {}".format(test_round, direct_bound[test_round], GMP_bound[test_round], flag))
# 			f.write("Round: {}, Direct_bound: {}, GMP_bound: {}, Exist_mon: {} \n".format(test_round, direct_bound[test_round], GMP_bound[test_round], flag))
# 			if flag:
# 				if (before_flag == 0) and (math.log(mul+1, 2) < GMP_bound[test_round-1]+1):
# 					g.write("Subgroup with size {}, Round: {}, LogValue: {:.2f}, GMP_bound: {}\n".format(mul_exp, test_round-1, math.log(mul, 2), GMP_bound[test_round-1]))
# 				break
# 			before_flag = flag
# 	f.write("\n")
# f.close()
# g.close()

# # test for maximal subgroup
# f = open("record_result/record_for_maxsubgroup.txt", "w")
# factor_list = [3, 5, 17, 257, 641, 65537, 6700417]
# f.write("Testing all possible subgroup with size 6 for high round.\n")
# for r in range(65, 71):
# 	print("Round:", r)
# 	f.write("Round: "+str(r)+"\n")
# 	mul = 5 * 17 * 257 * 641 * 65537 * 6700417
# 	mul_exp = "5 * 17 * 257 * 641 * 65537 * 6700417"
# 	flag = searchMonomialxi(n, r, mul, mode, xi)
# 	print("\tTesting subgroup with size {}, LogValue: {:.2f}, Result: {}".format(mul_exp, math.log(mul+1, 2), flag))
# 	f.write("\tTesting subgroup with size {}, LogValue: {:.2f}, Result: {}".format(mul_exp, math.log(mul+1, 2), flag))
# f.close()

# f = open("record_result/record_for_merge_subgroup.txt", "w")
# factor_list = [3, 5, 17, 257, 641, 65537, 6700417]
# for i in range(1, len(factor_list)):
# 	print("Factor Number:{}".format(i))
# 	for com in combinations(factor_list, i):
# 		mul = 1
# 		mul_exp = ""
# 		for elem in com:
# 			mul *= elem
# 			mul_exp += str(elem) + " * "
# 		mul_exp = mul_exp[:-2]
# 		print("\tTesting subgroup with size {}, LogValue: {:.2f}".format(mul_exp, math.log(mul+1, 2)))
# 		f.write("Testing subgroup with size {}, LogValue: {:.2f}\n".format(mul_exp, math.log(mul+1, 2)))
# 		begin_round = math.ceil(math.log(mul, 2))+1
# 		# while not searchMonomialxi(n, begin_round, mul, mode, xi):
# 		# 	begin_round += 1
# 		# print(begin_round, math.log(3*mul+1, 2), GMP_bound[begin_round]+1)
# 		while math.log(3*mul+1, 2) >= GMP_bound[begin_round]+1:
# 			begin_round += 1
# 		if begin_round >= Round:
# 			continue
# 		times = 1
# 		contain_times = []
# 		upper_index = min((2**(begin_round-1), 2**64-1))
# 		while times * mul <= upper_index:
# 			flag = searchCertainMonomialxi(n, begin_round, times * mul, mode, xi)
# 			if flag:
# 				contain_times.append(times)
# 			times += 1
# 		if len(contain_times) <= 4:
# 			f.write("\tRound: {}, Direct_bound: {}, GMP_bound: {}, MergeLog:{:.2f}, Cor_mon: {} \n".format(begin_round, direct_bound[begin_round], GMP_bound[begin_round], math.log(3*mul+1, 2), str(contain_times)))
# 		print("\t\tRound: {}, Direct_bound: {}, GMP_bound: {}, MergeLog:{:.2f}, Cor_mon: {}".format(begin_round, direct_bound[begin_round], GMP_bound[begin_round], math.log(3*mul+1, 2), str(contain_times)))
# 	f.write("\n")
# f.close()