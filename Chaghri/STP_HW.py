import subprocess
import math
import os
from itertools import combinations

block_size = 63
d = 32
h = 3
PATH_CRYPTOMINISAT = "/usr/local/bin/cryptominisat5"
PATH_STP = "/usr/local/bin/stp"

###################################################################################


"""
Return CryptoMiniSat process started with the given stp_file.
"""
def startSATsolver(stp_file):

    # Start STP to construct CNF
    subprocess.check_output([PATH_STP, "--exit-after-CNF", "--output-CNF", stp_file, "--CVC", "--disable-simplifications"])
 
    #if test
    # Find the number of solutions with the SAT solver
    sat_params = [ PATH_CRYPTOMINISAT, "--maxsol", str(1000000000 ),
                "--verb", "0", "--printsol", "0", "output_0.cnf"]

    sat_process = subprocess.Popen(sat_params, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    return sat_process

'''
Returns the solution for the given SMT problem using STP.
'''
def solveSTP(stp_file):

    stp_parameters = [PATH_STP, stp_file, "--CVC"]
    result = subprocess.check_output(stp_parameters)

    return result.decode("utf-8")


def Mn(num):
    if num % (2**block_size-1) == 0 and num != 0:
        return 2**block_size-1
    else:
        return num % (2**block_size-1)

def print_list_info(lis):
    info = ""
    for i in range(len(lis)):
        if lis[i] != 0:
            info += ("index: " + str(i) + " val: " + str(lis[i]) + " \t")
    print(info)

def recursive_compute_univar(ini_vec, round_num):
    new_vec = ini_vec
    for i in range(round_num):
        tmp_vec = []
        for j in range(block_size):
            tmp_vec.append(new_vec[(j-d-h) % block_size]+new_vec[(j-h) % block_size])
            # print(j-d-h, (j-d-h) % block_size, j-h, (j-h) % block_size)
        new_vec = tmp_vec
        # print_list_info(new_vec)
    return new_vec

def searchHammingWeight(round_num, weight):
    stp_file = "./tmp/chaghri_%s"%round_num +"_w%s"%weight +".cvc"

    fw = open(stp_file, "w")
    command = "%block_size: " + str(block_size) + "\n%Round: " + str(round_num) + "\n"
    fw.write(command)

    # compute N^r_i iteratively
    init_vec = [0 for i in range(block_size)]
    init_vec[0] = 1
    final_N = recursive_compute_univar(init_vec, round_num)
    nonzero_index = []
    for i in range(len(final_N)):
        if final_N[i] != 0:
            nonzero_index.append(i)
    print_list_info(final_N)

    # generate variable
    command = ""
    for i in range(len(nonzero_index)):
        command += "x" + str(i) + ": BITVECTOR(" + str(block_size) + ");\n"
    fw.write(command)

    # range constraint
    command = ""
    for i in range(len(nonzero_index)):
        upbound_str = "{:b}".format(final_N[nonzero_index[i]])
        upbound_str = "0bin" + upbound_str.zfill(block_size)
        command += "ASSERT BVLE( x" + str(i) + ", " + upbound_str + ");\n"
        command += "ASSERT BVGE( x" + str(i) + ", 0bin" + "0".zfill(block_size) + ");\n"
    command += "\n"
    fw.write(command)

    # add add_res = \sum_i 2^i r_i
    command = ""
    command += "addres : BITVECTOR(" + str(block_size) + ");\n"
    command += "ASSERT addres = BVPLUS( {}".format(block_size)
    for i in range(len(nonzero_index)):
        if nonzero_index[i] == 0:
            command += " , " + "x{}".format(i)
        else:
            command += " , " + "x{}[{}:{}]@x{}[{}:{}]".format(i, block_size-nonzero_index[i]-1, 0, i, block_size-1, block_size-nonzero_index[i])
    command += ");\n\n"
    fw.write(command)

    # Hamming weight constraint
    addstr = "0bin" + "0".zfill(block_size-1)
    command = ""
    command += "hw : BITVECTOR(" + str(block_size) + ");\n"
    command += "ASSERT hw = BVPLUS({}".format(block_size)
    for i in range(block_size):
        command += "," + addstr + "@addres[{}:{}]".format(i, i)
    command += ");\n"
    weight_str = "0bin" + "{:b}".format(weight).zfill(block_size)
    command += "ASSERT hw = " + weight_str + ";\n\n"
    fw.write(command)

    fw.write("QUERY FALSE;\nCOUNTEREXAMPLE;\n")
    fw.close()

    result = solveSTP(stp_file)
    # os.remove(stp_file)
    # print(result)

    if "Invalid" in result:
        # print("Weight:{} can be achieved at Round:{}!".format(weight, round_num))
        return 1
    else:
        # print("Unfortunelly, weight:{} can not be achieved at Round:{}!".format(weight, round_num))
        return 0


def searchMonomial(round_num, mon_degree):
    stp_file = "./tmp/chaghri_%s"%round_num +"_x^%s"%mon_degree +".cvc"

    fw = open(stp_file, "w")
    command = "%block_size: " + str(block_size) + "\n%Round: " + str(round_num) + "\n"
    fw.write(command)

    # compute N^r_i iteratively
    init_vec = [0 for i in range(block_size)]
    init_vec[0] = 1
    final_N = recursive_compute_univar(init_vec, round_num)
    nonzero_index = []
    for i in range(len(final_N)):
        if final_N[i] != 0:
            nonzero_index.append(i)
    # print_list_info(final_N)

    # generate variable
    command = ""
    for i in range(len(nonzero_index)):
        command += "x" + str(i) + ": BITVECTOR(" + str(block_size) + ");\n"
    fw.write(command)

    # range constraint
    command = ""
    for i in range(len(nonzero_index)):
        upbound_str = "{:b}".format(final_N[nonzero_index[i]])
        upbound_str = "0bin" + upbound_str.zfill(block_size)
        command += "ASSERT BVLE( x" + str(i) + ", " + upbound_str + ");\n"
        command += "ASSERT BVGE( x" + str(i) + ", 0bin" + "0".zfill(block_size) + ");\n"
    command += "\n"
    fw.write(command)

    # add add_res = \sum_i 2^i r_i
    command = ""
    command += "addres : BITVECTOR(" + str(block_size) + ");\n"
    command += "ASSERT addres = BVPLUS( {}".format(block_size)
    for i in range(len(nonzero_index)):
        if nonzero_index[i] == 0:
            command += " , " + "x{}".format(i)
        else:
            command += " , " + "x{}[{}:{}]@x{}[{}:{}]".format(i, block_size-nonzero_index[i]-1, 0, i, block_size-1, block_size-nonzero_index[i])
    command += ");\n"
    command += "ASSERT BVGT (addres, 0bin" + "0".zfill(block_size) + ");\n\n"
    fw.write(command)

    # Mod constraint
    mon_str = "0bin" + "{:b}".format(mon_degree).zfill(block_size)
    command = ""
    command += "rem : BITVECTOR(" + str(block_size) + ");\n"
    command += "ASSERT rem = BVMOD( {}, addres, {});\n".format(block_size, mon_str)
    command += "ASSERT rem = 0bin{};\n".format("0".zfill(block_size))
    fw.write(command)

    fw.write("QUERY FALSE;\nCOUNTEREXAMPLE;\n")
    fw.close()

    result = solveSTP(stp_file)
    os.remove(stp_file)
    # print(result)

    if "Invalid" in result:
        # print("c*x^{} can be achieved at Round:{}!".format(mon_degree, round_num))
        return 1
    else:
        # print("Unfortunelly, c*x^{} can not be achieved at Round:{}!".format(mon_degree, round_num))
        return 0

def find_all_monomial(round_num, mon_degree):
    stp_file = "./tmp/chaghri_%s"%round_num +"_x^%s"%mon_degree +".cvc"

    base_text = "%block_size: " + str(block_size) + "\n%Round: " + str(round_num) + "\n"

    # compute N^r_i iteratively
    init_vec = [0 for i in range(block_size)]
    init_vec[0] = 1
    final_N = recursive_compute_univar(init_vec, round_num)
    nonzero_index = []
    for i in range(len(final_N)):
        if final_N[i] != 0:
            nonzero_index.append(i)
    # print_list_info(final_N)

    # generate variable
    for i in range(len(nonzero_index)):
        base_text += "x" + str(i) + ": BITVECTOR(" + str(block_size) + ");\n"

    # range constraint
    for i in range(len(nonzero_index)):
        upbound_str = "{:b}".format(final_N[nonzero_index[i]])
        upbound_str = "0bin" + upbound_str.zfill(block_size)
        base_text += "ASSERT BVLE( x" + str(i) + ", " + upbound_str + ");\n"
        base_text += "ASSERT BVGE( x" + str(i) + ", 0bin" + "0".zfill(block_size) + ");\n"
    base_text += "\n"

    # add add_res = \sum_i 2^i r_i
    base_text += "addres : BITVECTOR(" + str(block_size) + ");\n"
    base_text += "ASSERT addres = BVPLUS( {}".format(block_size)
    for i in range(len(nonzero_index)):
        if nonzero_index[i] == 0:
            base_text += " , " + "x{}".format(i)
        else:
            base_text += " , " + "x{}[{}:{}]@x{}[{}:{}]".format(i, block_size-nonzero_index[i]-1, 0, i, block_size-1, block_size-nonzero_index[i])
    base_text += ");\n"
    base_text += "ASSERT BVGT (addres, 0bin" + "0".zfill(block_size) + ");\n\n"

    # Mod constraint
    mon_str = "0bin" + "{:b}".format(mon_degree).zfill(block_size)
    base_text += "rem : BITVECTOR(" + str(block_size) + ");\n"
    base_text += "ASSERT rem = BVMOD( {}, addres, {});\n".format(block_size, mon_str)
    base_text += "ASSERT rem = 0bin{};\n".format("0".zfill(block_size))

    final_text = "QUERY FALSE;\nCOUNTEREXAMPLE;\n"

    mid_text = ""
    all_pos_mon = []
    while True:
        fw = open(stp_file, "w")
        fw.write(base_text)
        fw.write(mid_text)
        fw.write(final_text)
        fw.close()
        result = solveSTP(stp_file)
        # print(result)
        # print("\n")
        if "Invalid" in result:
            begin_index = result.find("addres")
            tmp_value = result[begin_index+9:begin_index+74]
            # print(begin_index, tmp_value, int(tmp_value, 2), len(tmp_value))
            all_pos_mon.append(int(int(tmp_value, 2)/mon_degree))
            # print("\n")
            mid_text += "ASSERT BVGT(addres, "+ tmp_value +") OR BVLT(addres, "+ tmp_value +");\n"
        else:
            break
    os.remove(stp_file)
    return all_pos_mon

if __name__ == "__main__":
    f = open("tmp/record_subgroup_mon4.txt", 'w')
    al_deg = [1, 2, 3, 5, 7, 9, 12, 14, 17, 19, 22, 24, 27, 30, 32, 35, 37, 40, 42, 45, 47, 50, 52, 55, 58, 60, 63]
    size_list = [7, 7, 73, 127, 337, 92737, 649657]
    for i in range(1, len(size_list)+1):
        print("Element Number:{}".format(i))
        output_list = []
        for com in combinations(size_list, i):
            mul = 1
            mul_exp = ""
            for elem in com:
                mul *= elem
                mul_exp += str(elem) +" * "
            mul_exp = mul_exp[:-2]
            if mul_exp not in output_list:
                output_list.append(mul_exp)
            else:
                continue
            print("\tTesting subgroup with size {}".format(mul_exp))
            f.write("Testing subgroup with size {}\n".format(mul_exp))
            hmw = 0
            for elem in bin(mul)[2:]:
                if elem == '1':
                    hmw += 1
            print("\tHamming weight:%i"%hmw, "LogValue:%.2f"%math.log(mul, 2))
            for test_round in range(1, 27):
                flag = searchMonomial(test_round, mul)
                if flag == 1:
                    print("\t\tc*x^{} can ben achieved at round {}.".format(mul, test_round))
                    f.write("Hamming weight:%i"%hmw + ", LogValue:%.2f"%math.log(mul, 2) + ", Round:%i"%(test_round-1) + ", AL degree:%i"%al_deg[test_round-1])
                    if math.log(mul, 2) < al_deg[test_round-1]+1:
                        f.write(", Good candidate\n")
                    else:
                        f.write(", Bad candidate\n")
                    break
        f.write("\n")
    f.close()
    
    # find_all_monomial(4, 73)

    # g = open("tmp/good_merge_result.txt", "w")
    # al_deg = [1, 2, 3, 5, 7, 9, 12, 14, 17, 19, 22, 24, 27, 30, 32, 35, 37, 40, 42, 45, 47, 50, 52, 55, 58, 60, 63]
    # size_list = [7, 7, 73, 127, 337, 92737, 649657]
    # for i in range(1, len(size_list)):
    #     print("Element Number:{}".format(i))
    #     output_list = []
    #     for com in combinations(size_list, i):
    #         mul = 1
    #         mul_exp = ""
    #         for elem in com:
    #             mul *= elem
    #             mul_exp += str(elem) +" * "
    #         mul_exp = mul_exp[:-2]
    #         if mul_exp not in output_list:
    #             output_list.append(mul_exp)
    #         else:
    #             continue
    #         for test_round in range(1, 27):
    #             flag = searchMonomial(test_round, mul)
    #             if flag == 1:
    #                 if math.log(3*mul+1, 2) < al_deg[test_round]+1:
    #                     pos_re = find_all_monomial(test_round, mul)
    #                     rec_info = "Subgroup: {}= {}, Round: {}, ALDeg: {}, LogValue:{:.2f}, MegreLog:{:.2f}, all_mons:{}".format(mul_exp, mul, test_round, al_deg[test_round], math.log(mul+1, 2),  math.log(3*mul+1, 2), pos_re)
    #                     print(rec_info)
    #                     if (len(pos_re) == 1):
    #                         g.write(rec_info+"\n")
    #                 break
    #     g.write("\n")
    # g.close()


