# lib of CIMINION
import sys
sys.path.append("..")

from basic.basic import queryFalse, xorOperation, andOperation, copyOperation, startSATsolver, solveSTP

def genVar(n, r, fw):
	command = ""
	# state variables
	for i in range(r+1):
		command += "a_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "b_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "c_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
	command += "\n"

	for i in range(r):
		# auxiliary variables
		command += "acopy0_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "acopy1_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "bcopy0_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "bcopy1_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "d_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "e_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "ecopy0_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "ecopy1_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "f_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "fcopy0_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "fcopy1_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "g_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "h_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		# constant
		command += "t_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "u_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "v_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
		command += "w_" + str(i) + ": BITVECTOR(" + str(n) + ");\n"
	command += "\n"
	fw.write(command)


def genWeightVar(n, r, fw):
	addstr = "0bin" + "0".zfill(n-1)
	command = ""
	command += "wx : BITVECTOR(" + str(n) + ");\n"
	command += "ASSERT wx = BVPLUS({}".format(n)
	for b in range(n):
		command += "," + addstr + "@(a_0[{}:{}]".format(b,b)
		command += "," + addstr + "@(b_0[{}:{}]".format(b,b)
		command += "," + addstr + "@(c_0[{}:{}]".format(b,b)
	command += ");\n\n"
	command += "\n"
	fw.write(command)


def genWeightVarxi(n, r, fw, xi):
	addstr = "0bin" + "0".zfill(n-1)
	command = ""

	if xi == 0:
		command += "wxa : BITVECTOR(" + str(n) + ");\n" 
		command += "ASSERT wxa = BVPLUS({}".format(n)
		for b in range(n):
			command += "," + addstr + "@(a_0[{}:{}])".format(b,b)
		command += ");\n\n"
		command += "\n"
	elif xi == 1:
		command += "wxb : BITVECTOR(" + str(n) + ");\n" 
		command += "ASSERT wxb = BVPLUS({}".format(n)
		for b in range(n):
			command += "," + addstr + "@(b_0[{}:{}])".format(b,b)
		command += ");\n\n"
		command += "\n"
	else:
		command += "wxc : BITVECTOR(" + str(n) + ");\n" 
		command += "ASSERT wxc = BVPLUS({}".format(n)
		for b in range(n):
			command += "," + addstr + "@(c_0[{}:{}])".format(b,b)
		command += ");\n\n"
		command += "\n"
	fw.write(command)



def rangeVar(n, r, fw):
	command = ""

	degree_str = "{:b}".format(pow(2,n)-1)
	degree_str = "0bin" + degree_str.zfill(n)

	for i in range(r+1):
		command += "ASSERT BVLE( a_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( a_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( b_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( b_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( c_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( c_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"

	for i in range(r):
		command += "ASSERT BVLE( acopy0_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( acopy0_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( acopy1_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( acopy1_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( bcopy0_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( bcopy0_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( bcopy1_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( bcopy1_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( d_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( d_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( e_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( e_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( ecopy0_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( ecopy0_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( ecopy1_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( ecopy1_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( f_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( f_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( fcopy0_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( fcopy0_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( fcopy1_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( fcopy1_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( g_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( g_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( h_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( h_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( t_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( t_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( u_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( u_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( v_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( v_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
		command += "ASSERT BVLE( w_" + str(i) + ", " + degree_str + ");\n"
		command += "ASSERT BVGE( w_" + str(i) + ", 0bin" + "0".zfill(n) + ");\n"
	command += "\n"
	fw.write(command)

# different modes for different output indices
def finalConstraint(n, r, fw, mode):
	command = ""
	test_degree0 = "{:b}".format(0)
	test_degree1 = "{:b}".format(1)

	if mode == 0:
		command += "ASSERT a_" + str(r) + " = 0bin" + test_degree1.zfill(n) + ";\n"
		command += "ASSERT b_" + str(r) + " = 0bin" + test_degree0.zfill(n) + ";\n"
		command += "ASSERT c_" + str(r) + " = 0bin" + test_degree0.zfill(n) + ";\n"
	elif mode == 1:
		command += "ASSERT a_" + str(r) + " = 0bin" + test_degree0.zfill(n) + ";\n"
		command += "ASSERT b_" + str(r) + " = 0bin" + test_degree1.zfill(n) + ";\n"
		command += "ASSERT c_" + str(r) + " = 0bin" + test_degree0.zfill(n) + ";\n"
	else:
		command += "ASSERT a_" + str(r) + " = 0bin" + test_degree0.zfill(n) + ";\n"
		command += "ASSERT b_" + str(r) + " = 0bin" + test_degree0.zfill(n) + ";\n"
		command += "ASSERT c_" + str(r) + " = 0bin" + test_degree1.zfill(n) + ";\n"

	fw.write(command)

def NonzeroConstraint(fw, n):
    command = ""
    command += "ASSERT BVGT( a_0, 0bin" + "0".zfill(n) + ");\n"
    command += "ASSERT BVGT( b_0, 0bin" + "0".zfill(n) + ");\n"
    command += "ASSERT BVGT( c_0, 0bin" + "0".zfill(n) + ");\n"
    fw.write(command)

def NonzeroConstraintxi(fw, n, xi):
    command = ""
    if xi == 0:
    	command += "ASSERT BVGT( a_0, 0bin" + "0".zfill(n) + ");\n"
    elif xi == 1:
    	command += "ASSERT BVGT( b_0, 0bin" + "0".zfill(n) + ");\n"
    else:
    	command += "ASSERT BVGT( c_0, 0bin" + "0".zfill(n) + ");\n"
    fw.write(command)

def roundConstraint(n, r, fw):
	# a -COPY-> (acopy0, acopy1), b -COPY-> (bcopy0, bcopy1), (acopy0, bcopy0) -AND-> d,
	# (c, d) -XOR-> e, e -COPY->(ecopy0, ecopy1), (ecopy0, bcopy1) -XOR-> f,
	# f -COPY-> (fcopy0, fcopy1), (fcopy0, t) -AND-> g, (g, acopy1) -XOR-> h,
	# (ecopy1, u) -XOR-> a', (h, v) -XOR-> b', (fcopy1, w) -XOR-> c'
	command = ""
	for i in range(r):
		# a -COPY-> (acopy0, acopy1)
		command = copyOperation("a_{}".format(i), ["acopy0_{}".format(i), "acopy1_{}".format(i)], n, command)
		command += "\n"

		# b -COPY-> (bcopy0, bcopy1)
		command = copyOperation("b_{}".format(i), ["bcopy0_{}".format(i), "bcopy1_{}".format(i)], n, command)
		command += "\n"

		# (acopy0, bcopy0) -AND-> d
		command = andOperation(["acopy0_{}".format(i), "bcopy0_{}".format(i)], "d_{}".format(i), n ,command)
		command += "\n"

		# (c, d) -XOR-> e
		command = xorOperation(["c_{}".format(i), "d_{}".format(i)], "e_{}".format(i), n, command)
		command += "\n"

		# e -COPY->(ecopy0, ecopy1)
		command = copyOperation("e_{}".format(i), ["ecopy0_{}".format(i), "ecopy1_{}".format(i)], n, command)
		command += "\n"

		# (ecopy0, bcopy1) -XOR-> f
		command = xorOperation(["ecopy0_{}".format(i), "bcopy1_{}".format(i)], "f_{}".format(i), n, command)
		command += "\n"

		# f -COPY-> (fcopy0, fcopy1)
		command = copyOperation("f_{}".format(i), ["fcopy0_{}".format(i), "fcopy1_{}".format(i)], n, command)
		command += "\n"

		# (fcopy0, t) -AND-> g
		command = andOperation(["fcopy0_{}".format(i), "t_{}".format(i)], "g_{}".format(i), n ,command)
		command += "\n"

		# (g, acopy1) -XOR-> h
		command = xorOperation(["g_{}".format(i), "acopy1_{}".format(i)], "h_{}".format(i), n, command)
		command += "\n"

		# (ecopy1, u) -XOR-> a'
		command = xorOperation(["ecopy1_{}".format(i), "u_{}".format(i)], "a_{}".format(i+1), n, command)
		command += "\n"

		# (h, v) -XOR-> b'
		command = xorOperation(["h_{}".format(i), "v_{}".format(i)], "b_{}".format(i+1), n, command)
		command += "\n"

		# (fcopy1, w) -XOR-> c'
		command = xorOperation(["fcopy1_{}".format(i), "w_{}".format(i)], "c_{}".format(i+1), n, command)
		command += "\n"

	fw.write(command)

def MonomialConstraintx(n, r, fw, deg0, deg1, deg2):
	command = ""
	command += "rem0 : BITVECTOR(" + str(n) + ");\n" 
	monstr = "{:b}".format(deg0).zfill(n)
	command += "ASSERT rem0 = BVMOD( {}, a_0, 0bin{});\n".format(n, monstr)
	command += "ASSERT rem0 = 0bin{};\n".format("0".zfill(n))
	command += "rem1 : BITVECTOR(" + str(n) + ");\n" 
	monstr = "{:b}".format(deg1).zfill(n)
	command += "ASSERT rem1 = BVMOD( {}, b_0, 0bin{});\n".format(n, monstr)
	command += "ASSERT rem1 = 0bin{};\n".format("0".zfill(n))
	command += "rem2 : BITVECTOR(" + str(n) + ");\n" 
	monstr = "{:b}".format(deg2).zfill(n)
	command += "ASSERT rem2 = BVMOD( {}, c_0, 0bin{});\n".format(n, monstr)
	command += "ASSERT rem2 = 0bin{};\n".format("0".zfill(n))
	fw.write(command)

def MonomialConstraintxi(n, r, fw, deg, xi):
	command = ""
	command += "rem : BITVECTOR(" + str(n) + ");\n" 
	monstr = "{:b}".format(deg).zfill(n)
	if xi == 0:
		command += "ASSERT rem = BVMOD( {}, a_0, 0bin{});\n".format(n, monstr)
		command += "ASSERT rem = 0bin{};\n".format("0".zfill(n))
	elif xi == 1:
		command += "ASSERT rem = BVMOD( {}, b_0, 0bin{});\n".format(n, monstr)
		command += "ASSERT rem = 0bin{};\n".format("0".zfill(n))
	else:
		command += "ASSERT rem = BVMOD( {}, c_0, 0bin{});\n".format(n, monstr)
		command += "ASSERT rem = 0bin{};\n".format("0".zfill(n))
	fw.write(command)

def CertainMonomialConstraintxi(n, r, fw, deg, xi):
	command = ""
	monstr = "{:b}".format(deg).zfill(n)
	if xi == 0:
		command += "ASSERT a_0 = 0bin{};\n".format(monstr)
	elif xi == 1:
		command += "ASSERT b_0 = 0bin{};\n".format(monstr)
	else:
		command += "ASSERT c_0 = 0bin{};\n".format(monstr)
	fw.write(command)


def ConstantTermConstraintxi(n, r, fw, xi):
	command = ""
	if xi == 0:
		command += "ASSERT a_0 = 0bin{};\n".format("0".zfill(n))
	elif xi == 1:
		command += "ASSERT b_0 = 0bin{};\n".format("0".zfill(n))
	else:
		command += "ASSERT c_0 = 0bin{};\n".format("0".zfill(n))
	fw.write(command)