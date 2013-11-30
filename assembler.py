#!/usr/bin/env python2
try:
	import os,sys,re,binascii
except ImportError:
	print "[!]Invalid or Missing Library !"
	sys.exit(0)

def DispErr(ErrTyp,LineNo,Label=None):
	'''
Error Types:
------------
1- Invalid instruction .
2- Invalid Number of Operand(s) .
3- Label doesn't exist .
4- Label exists .
5- Format 4 used with instruction less than 3 bytes .
6- Invalid Indexing Register .
7- Invalid Register Name .
8- Invalid Constant Number .
9- START instruction duplicated .
10- Starting Address is invalid .
11- Program exceeded memory limits .
	'''
	LineNo/=5
	if ErrTyp == 1:
		print "[!]Invalid instruction on line number %d\n"%(LineNo)
	elif ErrTyp == 2:
		print "[!]Invalid Number or type of Operand(s) on line number %d\n"%(LineNo)
	elif ErrTyp == 3:
		print "[!]Label ( %s ) used in line %d doesn't exist .\n"%(Label,LineNo)
	elif ErrTyp == 4:
		print "[!]Label ( %s ) used in line %d is already in use .\n"%(Label,LineNo)
	elif ErrTyp == 5:
		print "[!]Format 4 used with instruction ( %s ) ,which is less than 3 bytes on line number %d\n"%(Label,LineNo)
	elif ErrTyp == 6:
		print "[!]Invalid Indexing Register on line number %d\n"%(LineNo)
	elif ErrTyp == 7:
		print "[!]Invalid Register name used on line number %d\n"%(LineNo)
	elif ErrTyp == 8:
		print "[!]Invalid Constant number on line number %d\n"%(LineNo)
	elif ErrTyp == 9:
		print "[!]START instruction used more than once on line number %d\n"%(LineNo)
	elif ErrTyp == 10:
		print "[!]Starting Address used on line %d is invalid .\n"%(LineNo)
	elif ErrTyp == 11:
		print "[!]Program Exceeded Memory Limits which should remain smaller than 0xFFFFF (2^20 bytes ) on line %d .\n"%(LineNo)
	print "[!]Exiting assembler ..."
	sys.exit(0)

def CheckOP(di,aa,sym,LN):
	reg=['a','b','s','t','x','pc','sw','f']
	if di[aa[0]]['OPNUM']==0 and (len(aa[1].split(','))==2 or len(aa[1].split())==1):
		if len(aa[1].split(','))==1:
			if not(sym.has_key(aa[1])):
				DispErr(3,LN,Label=aa[1])
		elif len(aa[1].split(','))==2 and not(aa[1].split(',')[1].lower() == 'x') :
			DispErr(6,LN)
		elif len(aa[1].split(','))==2 and not(sym.has_key(aa[1].split(',')[0].lower())):
			DispErr(3,LN,Label=aa[1].split(',')[0])
		return
	else:
		DispErr(2,LN)
	if di[aa[0]]['OPNUM']==1 and len(aa[1].split(','))==2:
		if not(aa[1].split(',')[0].lower() in reg and aa[1].split(',')[1].lower() in reg):
			DispErr(7,LN)
		return
	else:
		DispErr(2,LN)
	if di[aa[0]]['OPNUM']==2 and len(aa[1].split(','))==1:
		if not(aa[1].split(',')[0].lower() in reg) :
			DispErr(7,LN)
		return
	else:
		DispErr(2,LN)
	if di[aa[0]]['OPNUM']==5 and len(aa[1].split(','))==2:
		if not(aa[1].split(',')[0].lower() in reg and aa[1].split(',')[1].isdigit()) :
			DispErr(7,LN)
		return
	else:
		DispErr(2,LN)
	if di[aa[0]]['OPNUM']==6 and len(aa[1].split(','))==1:
		if not(aa[1].isdigit()):
			DispErr(8,LN)
		return
	else:
		DispErr(2,LN)
	if di[aa[0]]['OPNUM']==0xF and len(aa)>1:
		DispErr(2,LN) 

try:
	f=open(sys.argv[1],'r')
except Exception,e:
	print "[!]srcfile.txt Not found in current directory .\n"
	sys.exit(0)
try:
	of=open('./intfile.txt','w+')
except IOError:
	print "[!]intfile.txt Cannot be created in current directory .\n"
	sys.exit(0)
of.write('Line\t\tLoc\t\tSource Statement\n\n')

stf,enf,LN,LOCCTR,SYMTAB,OPTAB=0,0,0,0,{},{}

#Operation Table :
#OPNUM values :
#0x0 ==> memory only operands .
#0x1 ==> 2 registers operands .
#0x2 ==> 1 register operands .
#0x5 ==> 1 register and 1 constant operands .
#0x6 ==> 1 constant operands .
#0xF ==> Nothing .

OPTAB['add']   = {'OPCODE':0x18,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['addf']  = {'OPCODE':0x58,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['addr']  = {'OPCODE':0x90,'OPLEN':0x2,'OPNUM':0x1}
OPTAB['and']   = {'OPCODE':0x40,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['clear'] = {'OPCODE':0xb4,'OPLEN':0x2,'OPNUM':0x2}
OPTAB['comp']  = {'OPCODE':0x28,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['compf'] = {'OPCODE':0x88,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['compr'] = {'OPCODE':0xa0,'OPLEN':0x2,'OPNUM':0x1}
OPTAB['div']   = {'OPCODE':0x24,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['divf']  = {'OPCODE':0x64,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['divr']  = {'OPCODE':0x9c,'OPLEN':0x2,'OPNUM':0x1}
OPTAB['fix']   = {'OPCODE':0xc4,'OPLEN':0x1,'OPNUM':0xF}
OPTAB['float'] = {'OPCODE':0xc0,'OPLEN':0x1,'OPNUM':0xF}
OPTAB['hio']   = {'OPCODE':0xf4,'OPLEN':0x1,'OPNUM':0xF}
OPTAB['j']     = {'OPCODE':0x3c,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['jeq']   = {'OPCODE':0x30,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['jgt']   = {'OPCODE':0x34,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['jlt']   = {'OPCODE':0x38,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['jsub']  = {'OPCODE':0x48,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['lda']   = {'OPCODE':0x00,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['ldb']   = {'OPCODE':0x68,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['ldch']  = {'OPCODE':0x50,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['ldf']   = {'OPCODE':0x70,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['ldl']   = {'OPCODE':0x08,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['lds']   = {'OPCODE':0x6c,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['ldt']   = {'OPCODE':0x74,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['ldx']   = {'OPCODE':0x04,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['lps']   = {'OPCODE':0xd0,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['mul']   = {'OPCODE':0x20,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['mulf']  = {'OPCODE':0x60,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['mulr']  = {'OPCODE':0x98,'OPLEN':0x2,'OPNUM':0x1}
OPTAB['norm']  = {'OPCODE':0xc8,'OPLEN':0x1,'OPNUM':0xF}
OPTAB['or']    = {'OPCODE':0x44,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['rd']    = {'OPCODE':0xd8,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['rmo']   = {'OPCODE':0xac,'OPLEN':0x2,'OPNUM':0x1}
OPTAB['rsub']  = {'OPCODE':0x4c,'OPLEN':0x3,'OPNUM':0xF}
OPTAB['shiftl']= {'OPCODE':0xa4,'OPLEN':0x2,'OPNUM':0x5}
OPTAB['shiftr']= {'OPCODE':0xa8,'OPLEN':0x2,'OPNUM':0x5}
OPTAB['sio']   = {'OPCODE':0xf0,'OPLEN':0x1,'OPNUM':0xF}
OPTAB['ssk']   = {'OPCODE':0xec,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['sta']   = {'OPCODE':0x0c,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['stb']   = {'OPCODE':0x78,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['stch']  = {'OPCODE':0x54,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['stf']   = {'OPCODE':0x80,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['sti']   = {'OPCODE':0xd4,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['stl']   = {'OPCODE':0x14,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['sts']   = {'OPCODE':0x7c,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['stsw']  = {'OPCODE':0xe8,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['stt']   = {'OPCODE':0x84,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['stx']   = {'OPCODE':0x10,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['sub']   = {'OPCODE':0x1c,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['subf']  = {'OPCODE':0x5c,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['subr']  = {'OPCODE':0x94,'OPLEN':0x2,'OPNUM':0x1}
OPTAB['svc']   = {'OPCODE':0xb0,'OPLEN':0x2,'OPNUM':0x6}
OPTAB['td']    = {'OPCODE':0xe0,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['tio']   = {'OPCODE':0xf8,'OPLEN':0x1,'OPNUM':0xF}
OPTAB['tix']   = {'OPCODE':0x2c,'OPLEN':0x3,'OPNUM':0x0}
OPTAB['tixr']  = {'OPCODE':0xb8,'OPLEN':0x2,'OPNUM':0x2}
OPTAB['wd']    = {'OPCODE':0xdc,'OPLEN':0x3,'OPNUM':0x0}

#OPTAB END

try:
	line=f.readline()
	while line[0]=='.':
		line=f.readline()
	line.split()[0],line.split()[1]
#	line=f.readline()
#	line.split()[0],line.split()[1]
#	line=f.readline()
#	line.split()[0],line.split()[1]
except IndexError:
	print "[!]Invalid SIC/XE file structure .\n\n[!]Exiting assembler ...\n\n"
	sys.exit(0)
f.seek(0)
while 1:
	LN+=5
	line=f.readline()
	if line == '':
		break
	if line[0]=='.':
		of.write('%d\t   \t\t        %s\n\n'%(LN,line.strip()))
		continue;
	elif line.split() ==[]:
		continue;
	aa=map(lambda x: x.lower(),line.strip().split())
	if LOCCTR >= 0xFFFFF:
		DispErr(11,LN)
	try:
		if aa[1] == 'start' :
			if len(aa) == 3:
				if stf==1:
					DispErr(9,LN);
				if int(aa[2],16) > 0x0 and int(aa[2],16) < 0xFFFFF:
					try:
						LOCCTR=int(aa[2],16)
						stf=1;
					except ValueError:
						print "[!]Invalid Hexadecimal Number at start instruction ."
						print "[!]Exiting assembler  ..."
						sys.exit(0)
				else:
					DispErr(10,LN)
			SYMTAB[aa[0]]=LOCCTR
			of.write('{}  {:^29}{:^14}\n'.format(LN,hex(LOCCTR)[2:],line))
			continue
	except IndexError:
		DispErr(1,LN)
	if len(aa) > 3:
		if aa[1] == 'byte':
			for z in range(3,len(aa)):
				aa[2]+=' '+aa[3];aa.pop(3)
		else:
			DispErr(2,LN)
	if len(aa) == 3:
		if SYMTAB.has_key(aa[0]):
			DispErr(4,LN,Label=aa[0])
		else:
			SYMTAB[aa[0]]=LOCCTR
			aa.pop(0)
	if aa[0] == 'end' and SYMTAB.has_key(aa[1]) :
		of.write('{}  \t\t\t       {:^43}\n'.format(LN,line.strip()))
		enf=1
		break
	elif aa[0]=='end' and not(SYMTAB.has_key(aa[1])) :
		DispErr(3,LN,Label=aa[1])
	if aa[0][0] == '+':
		if OPTAB.has_key(aa[0][1:]):
			if OPTAB[aa[0][1:]]['OPLEN'] < 3 :
				DispErr(5,LN,Label=aa[0][1:])
			
			of.write('{}  {:^28}{:^14}\n'.format(LN,hex(LOCCTR)[2:],line))
			LOCCTR+=4
		else:
			DispErr(1,LN)
	else:
		if OPTAB.has_key(aa[0]):
#			CheckOP(OPTAB,aa,SYMTAB,LN)    MUST BE IN PASS2
			of.write('{}  {:^28}{:^14}\n'.format(LN,hex(LOCCTR)[2:],line))
			LOCCTR+=OPTAB[aa[0]]['OPLEN']
		elif aa[0] == 'word':
			of.write('{}  {:^28}{:^14}\n'.format(LN,hex(LOCCTR)[2:],line))
			LOCCTR+=3
		elif aa[0] == 'resw':
			of.write('{}  {:^28}{:^14}\n'.format(LN,hex(LOCCTR)[2:],line))
			try:
				LOCCTR+=3*(int(aa[1]))
			except IndexError:
				DispErr(2,LN)
		elif aa[0] == 'byte':
			of.write('{}  {:^28}{:^14}\n'.format(LN,hex(LOCCTR)[2:],line))
			try:
				LOCCTR+=(len(aa[1][2:-1]))
			except IndexError:
				DispErr(2,LN)
		elif aa[0] == 'resb':
			of.write('{}  {:^28}{:^14}\n'.format(LN,hex(LOCCTR)[2:],line))
			try:
				LOCCTR+=int(aa[1])
			except IndexError:
				DispErr(2,LN)
		else:
			DispErr(1,LN)

if enf==0:
	print "[!]END instruction wasn't found in source code file .\n\n"
	print "[!]Exiting assembler ..."
	sys.exit(0)

of.write("\n\n\n")
of.write( "*"*15+"SYMBOLIC TABLE"+"*"*15+"\n\n")
of.write( "SYMBOL\t\tADDRESS\n\n")
for k,v in SYMTAB.iteritems():
	of.write( str(k)+"\t\t"+str(hex(v))[2:]+"\n")


