from Cache import *
from Class import *
from Symbol import *

ptr = 0
num_index = 0
id_index = 0
eflag = 0
maintable = Table()
entrycode = Code('JMP', 0, None)


def nextptr():
    global ptr
    ptr += 1


def error(msg):
    global ptr
    msg = str(Position[ptr]) + '  ' + msg
    print(msg)
    exit(-1)


def get_num():
    global num_index
    number = NUMlist[num_index]
    num_index += 1
    return number


def get_id():
    global id_index
    name = IDlist[id_index]
    id_index += 1
    return name


def syntax_analyse(need_log):
    codelist.append(entrycode)
    tablelist.append(maintable)
    deal_program(maintable)
    outlog = open('log/mid_code_log.txt', 'w')
    for i, x in enumerate(codelist):
        outlog.writelines(str(i) + ':\t' + str(x) + '\n')
    outlog.close()
    if need_log=='Y' or need_log=='y':
        for i, x in enumerate(codelist):
            print(str(i) + ':\t\t' + str(x))
    return


def deal_program(table):
    if SYMBOL[ptr] != KEYWORDS['program']:
        msg = 'expect symbol \'program\''
        error(msg)
    nextptr()

    if SYMBOL[ptr] != identifier:
        msg = 'expect identifier after \'program\''
        error(msg)
    name = get_id()
    entry = Entry(name, KIND.PROCEDURE)
    table.add(entry)
    nextptr()

    if SYMBOL[ptr] != DELIMITERS[';']:
        msg = 'expect \';\''
        error(msg)
    nextptr()

    deal_block(table, entry)

    if ptr != len(SYMBOL):
        msg = 'default'
        error(msg)
    print('SyntaxAnalyser: no error detected')


def deal_block(table, entry):
    if SYMBOL[ptr] == KEYWORDS['const']:
        deal_condecl(table)

    if SYMBOL[ptr] == KEYWORDS['var']:
        deal_var(table)

    if SYMBOL[ptr] == KEYWORDS['procedure']:
        deal_procedure(table)

    if SYMBOL[ptr] != KEYWORDS['begin']:
        msg = 'expect <condecl> or <vardecl> or <proc> or <body>'
        error(msg)

    entry.adr = len(codelist)
    entrycode.a = len(codelist)
    codelist.append(Code('INT', 0, table.getSize()))
    deal_body(table)
    codelist.append(Code('OPR', 0, 0))


def deal_condecl(table):
    if SYMBOL[ptr] != KEYWORDS['const']:
        msg = 'expect \'const\''
        error(msg)
    nextptr()
    deal_const(table)
    while SYMBOL[ptr] == DELIMITERS[',']:
        nextptr()
        deal_const(table)
    if SYMBOL[ptr] == DELIMITERS[';']:
        nextptr()
    else:
        msg = 'expect \';\' after declaration'
        error(msg)


def deal_const(table):
    if SYMBOL[ptr] != identifier:
        msg = 'expect identifier'
        error(msg)
    name = get_id()
    nextptr()

    if SYMBOL[ptr] != OPERATORS[':=']:
        msg = 'expect \':=\' after identifier'
        error(msg)
    nextptr()

    if SYMBOL[ptr] != number:
        msg = 'number required in constant declaration'
        error(msg)
    val = get_num()
    nextptr()
    entry = Entry(name, KIND.CONSTANT, val)
    flag = table.add(entry)
    if flag == 1:
        msg = 'redeclaration: \'' + str(name) + '\''
        error(msg)


def deal_var(table):
    if SYMBOL[ptr] != KEYWORDS['var']:
        msg = 'expect \'var\''
        error(msg)
    nextptr()

    if SYMBOL[ptr] != identifier:
        msg = 'expect identifier'
        error(msg)

    name = get_id()
    entry = Entry(name, KIND.VARIABLE)
    flag = table.add(entry)
    if flag == 1:
        msg = 'redeclaration: \'' + str(name) + '\''
        error(msg)
    nextptr()

    while SYMBOL[ptr] == DELIMITERS[',']:
        nextptr()
        if SYMBOL[ptr] != identifier:
            msg = 'expect identifier'
            error(msg)
        name = get_id()
        entry = Entry(name, KIND.VARIABLE)
        flag = table.add(entry)
        if flag == 1:
            msg = 'redeclaration: \'' + str(name) + '\''
            error(msg)
        nextptr()

    if SYMBOL[ptr] == DELIMITERS[';']:
        nextptr()
    else:
        msg = 'expect \';\' after declaration'
        error(msg)


def deal_procedure(table):
    if SYMBOL[ptr] != KEYWORDS['procedure']:
        msg = 'expect \'procedure\''
        error(msg)
    nextptr()

    if SYMBOL[ptr] != identifier:
        msg = 'expect identifier'
        error(msg)

    tempname = get_id()
    tempentry = Entry(tempname, KIND.PROCEDURE)
    flag = table.add(tempentry)
    if flag == 1:
        msg = 'redeclaration: \'' + str(tempname) + '\''
        error(msg)
    newtable = Table(table)
    tablelist.append(newtable)
    nextptr()

    if SYMBOL[ptr] != DELIMITERS['(']:
        msg = 'expect \'()\' after procedure declaration'
        error(msg)
    nextptr()

    num_para = 0
    if SYMBOL[ptr] == identifier:
        num_para += 1
        tempname = get_id()
        newentry = Entry(tempname, KIND.VARIABLE)
        flag = newtable.add(newentry)
        if flag == 1:
            msg = 'redeclaration: \'' + str(tempname) + '\''
            error(msg)
        nextptr()
        while SYMBOL[ptr] == DELIMITERS[',']:
            nextptr()
            if SYMBOL[ptr] == identifier:
                num_para += 1
                tempname = get_id()
                newentry = Entry(tempname, KIND.VARIABLE)
                flag = newtable.add(newentry)
                if flag == 1:
                    msg = 'redeclaration: \'' + str(tempname) + '\''
                    error(msg)
                nextptr()
            else:
                msg = 'expect identifier'
                error(msg)

    tempentry.para = num_para
    if SYMBOL[ptr] == DELIMITERS[')']:
        nextptr()
    else:
        msg = 'expect \')\''
        error(msg)
    if SYMBOL[ptr] == DELIMITERS[';']:
        nextptr()
    else:
        msg = 'expect \';\' after declaration'
        error(msg)

    deal_block(newtable, tempentry)

    while SYMBOL[ptr] == DELIMITERS[';']:
        nextptr()
        if SYMBOL[ptr] == KEYWORDS['procedure']:
            deal_procedure(table)
        else:
            msg = 'expect \'procedure\' after \';\''
            error(msg)


def deal_body(table):
    if SYMBOL[ptr] != KEYWORDS['begin']:
        msg = 'expect \'begin\''
        error(msg)
    nextptr()

    deal_statement(table)

    while SYMBOL[ptr] != KEYWORDS['end']:
        if SYMBOL[ptr] == DELIMITERS[';']:
            nextptr()
            deal_statement(table)
        else:
            msg = 'expect \';\' before new statement'
            error(msg)
    if SYMBOL[ptr] == KEYWORDS['end']:
        nextptr()


def deal_statement(table):
    if SYMBOL[ptr] == identifier:
        deal_assign(table)
    elif SYMBOL[ptr] == KEYWORDS['if']:
        deal_if(table)
    elif SYMBOL[ptr] == KEYWORDS['while']:
        deal_while(table)
    elif SYMBOL[ptr] == KEYWORDS['call']:
        deal_call(table)
    elif SYMBOL[ptr] == OPERATORS['read']:
        deal_read(table)
    elif SYMBOL[ptr] == OPERATORS['write']:
        deal_write(table)
    elif SYMBOL[ptr] == KEYWORDS['begin']:
        deal_body(table)
    elif SYMBOL[ptr] != KEYWORDS['end']:
        msg = 'illegal statement'
        error(msg)


def deal_assign(table):
    name = get_id()
    nextptr()
    if SYMBOL[ptr] != OPERATORS[':=']:
        msg = 'expect \':=\' in assignment'
        error(msg)
    nextptr()
    deal_expr(table)
    (l, a, flag) = table.find(name)
    if a == 0:
        msg = 'undeclared identifier'
        error(msg)
    if flag == isConst:
        msg = 'can not assign constant'
        error(msg)
    if flag == isProc:
        msg = 'undeclared identifier'
        error(msg)
    else:
        codelist.append(Code('STO', l, a))


def deal_if(table):
    nextptr()
    deal_lexp(table)
    falseout = Code('JPC', 0, None)
    codelist.append(falseout)
    if SYMBOL[ptr] != KEYWORDS['then']:
        msg = 'expect \'then\' after \'if\''
        error(msg)
    else:
        nextptr()
        deal_statement(table)

    trueout = Code('JMP', 0, None)
    if SYMBOL[ptr] == KEYWORDS['else']:
        nextptr()
        codelist.append(trueout)
        falseout.a = len(codelist)
        deal_statement(table)
        trueout.a = len(codelist)
    else:
        falseout.a = len(codelist)


def deal_while(table):
    nextptr()
    current = len(codelist)
    deal_lexp(table)
    falseout = Code('JPC', 0, None)
    codelist.append(falseout)

    if SYMBOL[ptr] == KEYWORDS['do']:
        nextptr()
        deal_statement(table)
        codelist.append(Code('JMP', 0, current))
        falseout.a = len(codelist)
    else:
        msg = 'expect \'do\' after \'while\''
        error(msg)


def deal_read(table):
    nextptr()
    if SYMBOL[ptr] == DELIMITERS['(']:
        nextptr()
        if SYMBOL[ptr] == identifier:
            name = get_id()
            nextptr()
            (l, a, flag) = table.find(name)
            if a == 0:
                msg = 'undeclared identifier'
                error(msg)
            if flag == isConst:
                msg = 'can not assign constant'
                error(msg)
            if flag == isProc:
                msg = 'undeclared identifier'
                error(msg)
            else:
                codelist.append(Code('OPR', 0, OPERATORS['read']))
                codelist.append(Code('STO', l, a))
            while SYMBOL[ptr] == DELIMITERS[',']:
                nextptr()
                if SYMBOL[ptr] == identifier:
                    name = get_id()
                    nextptr()
                    (l, a, flag) = table.find(name)
                    if a == 0:
                        msg = 'undeclared identifier'
                        error(msg)
                    if flag == isConst:
                        msg = 'can not assign constant'
                        error(msg)
                    if flag == isProc:
                        msg = 'undeclared identifier'
                        error(msg)
                    else:
                        codelist.append(Code('OPR', 0, OPERATORS['read']))
                        codelist.append(Code('STO', l, a))
                else:
                    msg = 'expect variable in read()'
                    error(msg)

            if SYMBOL[ptr] == DELIMITERS[')']:
                nextptr()
            else:
                msg = 'expect \')\' after \'(\''
                error(msg)
        else:
            msg = 'expect variable in read()'
            error(msg)
    else:
        msg = 'expect \'(\' after \'read\''
        error(msg)


def deal_write(table):
    nextptr()
    if SYMBOL[ptr] == DELIMITERS['(']:
        nextptr()
        deal_expr(table)
        codelist.append(Code('OPR', 0, OPERATORS['write']))
        while SYMBOL[ptr] == DELIMITERS[',']:
            nextptr()
            deal_expr(table)
            codelist.append(Code('OPR', 0, OPERATORS['write']))
        if SYMBOL[ptr] == DELIMITERS[')']:
            nextptr()
        else:
            msg = 'expect \')\' after \'(\''
            error(msg)
    else:
        msg = 'expect \'(\' after \'write\''
        error(msg)


def deal_call(table):
    nextptr()
    if SYMBOL[ptr] != identifier:
        msg = 'expect identifier after \'call\''
        error(msg)

    procname = get_id()
    nextptr()
    if SYMBOL[ptr] != DELIMITERS['(']:
        msg = 'expect \'(\' after \'call\''
        error(msg)

    nextptr()
    para = 0
    if SYMBOL[ptr] == identifier or SYMBOL[ptr] == number:
        para += 1
        deal_expr(table)
        codelist.append(Code('OPR', 2 + para, OPERATORS['post']))
        while SYMBOL[ptr] == DELIMITERS[',']:
            nextptr()
            para += 1
            deal_expr(table)
            codelist.append(Code('OPR', 2 + para, OPERATORS['post']))
        if SYMBOL[ptr] == DELIMITERS[')']:
            nextptr()
        else:
            msg = 'expect \')\' after \'(\''
            error(msg)
    elif SYMBOL[ptr] == DELIMITERS[')']:
        nextptr()
    else:
        msg = 'expect \')\' after \'(\''
        error(msg)

    (l, a, flag) = table.find(procname)
    if flag != isProc:
        msg = 'procedure not declared'
        error(msg)
    if para != table.find_par(procname):
        msg = 'wrong number of parameters'
        error(msg)
    codelist.append(Code('CAL', l, a))


def deal_expr(table):
    if SYMBOL[ptr] == OPERATORS['+']:
        nextptr()
        deal_term(table)
    elif SYMBOL[ptr] == OPERATORS['-']:
        nextptr()
        deal_term(table)
        codelist.append(Code('LIT', 0, -1))
        codelist.append(Code('OPR', 0, OPERATORS['*']))
    else:
        deal_term(table)
    while SYMBOL[ptr] == OPERATORS['+'] or SYMBOL[ptr] == OPERATORS['-']:
        opr = SYMBOL[ptr]
        deal_aop(table)
        deal_term(table)
        codelist.append(Code('OPR', 0, opr))


def deal_term(table):
    deal_factor(table)
    while SYMBOL[ptr] == OPERATORS['*'] or SYMBOL[ptr] == OPERATORS['/']:  # 先乘除，后加减
        opr = SYMBOL[ptr]
        deal_mop(table)
        deal_factor(table)
        codelist.append(Code('OPR', 0, opr))


def deal_factor(table):
    if SYMBOL[ptr] == identifier:
        name = get_id()
        nextptr()
        (l, a, flag) = table.find(name)
        if a == 0 or a == isProc:
            msg = 'undeclared identifier'
            error(msg)
        if flag == isConst:
            codelist.append(Code('LIT', 0, a))
        else:
            codelist.append(Code('LOD', l, a))
    elif SYMBOL[ptr] == number:
        val = get_num()
        nextptr()
        codelist.append(Code('LIT', 0, val))
    elif SYMBOL[ptr] == DELIMITERS['(']:
        nextptr()
        deal_expr(table)
        if SYMBOL[ptr] == DELIMITERS[')']:
            nextptr()
        else:
            msg = 'expect \')\' after \'(\''
            error(msg)
    else:
        msg = 'expect factor in expression'
        error(msg)


def deal_lop(table):
    if SYMBOL[ptr] == OPERATORS['='] or SYMBOL[ptr] == OPERATORS['<>'] or SYMBOL[ptr] == OPERATORS['<'] or SYMBOL[ptr] == OPERATORS['<='] or SYMBOL[ptr] == OPERATORS['>'] or SYMBOL[ptr] == OPERATORS['>=']:
        opr = SYMBOL[ptr]
        nextptr()
        return opr
    else:
        msg = 'illegal lop'
        error(msg)


def deal_lexp(table):
    if SYMBOL[ptr] == OPERATORS['+'] or SYMBOL[ptr] == OPERATORS['-'] or SYMBOL[ptr] == identifier or SYMBOL[ptr] == number or SYMBOL[ptr] == DELIMITERS['(']:
        deal_expr(table)
        opr = deal_lop(table)
        deal_expr(table)
        codelist.append(Code('OPR', 0, opr))
    elif SYMBOL[ptr] == OPERATORS['odd']:
        nextptr()
        deal_expr(table)
        codelist.append(Code('OPR', 0, OPERATORS['odd']))
    else:
        msg = 'illegal lexp'
        error(msg)


def deal_aop(table):
    nextptr()


def deal_mop(table):
    nextptr()
