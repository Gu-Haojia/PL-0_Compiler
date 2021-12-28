from Cache import *
from Class import *
from Symbol import *

ptr = 0  # 元素指针（SYMBOL)
num_index = 0  # 数字指针
id_index = 0  # 标识符指针
maintable = Table()  # 符号表母表
entrycode = Code('JMP', 0, None)  # 入口代码


# 下一个符号
def nextptr():
    global ptr
    ptr += 1


# 出错处理
def error(msg):
    global ptr
    msg = str(Position[ptr]) + '  ' + msg
    print(msg)
    exit(-1)


# 获取下一个数字
def get_num():
    global num_index
    number_val = NUMlist[num_index]
    num_index += 1
    return number_val


# 获取下一个标识符名称
def get_id():
    global id_index
    name = IDlist[id_index]
    id_index += 1
    return name


# 入口
def syntax_analyse(need_log):
    #  初始化元符号表和入口代码
    codelist.append(entrycode)
    tablelist.append(maintable)
    #  对prog单元进行规约
    deal_program(maintable)
    #  分析完成文件输出
    outlog = open('log/mid_code_log.txt', 'w')
    for i, x in enumerate(codelist):
        outlog.writelines(str(i) + ':\t' + str(x) + '\n')
    outlog.close()
    #  log输出
    if need_log == 'Y' or need_log == 'y':
        for i, x in enumerate(codelist):
            print(str(i) + ':\t\t' + str(x))
    return


# <prog> → program <id>；<block>
def deal_program(table):
    #  移进program
    if SYMBOL[ptr] != KEYWORDS['program']:
        msg = 'expect symbol \'program\''
        error(msg)
    nextptr()

    #  移进id
    if SYMBOL[ptr] != identifier:
        msg = 'expect identifier after \'program\''
        error(msg)
    #  prog名放入符号表
    name = get_id()
    entry = Entry(name, KIND.PROCEDURE)
    table.add(entry)
    nextptr()

    #  移进;
    if SYMBOL[ptr] != DELIMITERS[';']:
        msg = 'expect \';\''
        error(msg)
    nextptr()

    #  规约block
    deal_block(table, entry)

    #  多余代码出错
    if ptr != len(SYMBOL):
        msg = 'default'
        error(msg)
    print('SyntaxAnalyser: no error detected')


# <block> → [<condecl>][<vardecl>][<proc>]<body>
def deal_block(table, entry):
    #  规约condecl
    if SYMBOL[ptr] == KEYWORDS['const']:
        deal_condecl(table)

    #  规约vardecl
    if SYMBOL[ptr] == KEYWORDS['var']:
        deal_var(table)

    #  规约proc
    if SYMBOL[ptr] == KEYWORDS['procedure']:
        deal_procedure(table)

    #  未知语法单位出错处理
    if SYMBOL[ptr] != KEYWORDS['begin']:
        msg = 'expect <condecl> or <vardecl> or <proc> or <body>'
        error(msg)

    #  更新过程地址
    entry.adr = len(codelist)
    entrycode.a = len(codelist)
    #  分配数据区
    codelist.append(Code('INT', 0, table.getSize()))
    #  规约body
    deal_body(table)
    #  退栈
    codelist.append(Code('OPR', 0, 0))


# <condecl> → const <const>{,<const>};
def deal_condecl(table):
    #  移进const
    if SYMBOL[ptr] != KEYWORDS['const']:
        msg = 'expect \'const\''
        error(msg)
    nextptr()

    #  规约<const>
    deal_const(table)
    while SYMBOL[ptr] == DELIMITERS[',']:
        nextptr()
        deal_const(table)

    #  移进;
    if SYMBOL[ptr] == DELIMITERS[';']:
        nextptr()
    else:
        msg = 'expect \';\' after declaration'
        error(msg)


# <const> → <id>:=<integer>
def deal_const(table):
    #  移进id
    if SYMBOL[ptr] != identifier:
        msg = 'expect identifier'
        error(msg)
    name = get_id()
    nextptr()

    #  移进:=
    if SYMBOL[ptr] != OPERATORS[':=']:
        msg = 'expect \':=\' after identifier'
        error(msg)
    nextptr()

    #  移进num
    if SYMBOL[ptr] != number:
        msg = 'number required in constant declaration'
        error(msg)
    val = get_num()
    nextptr()

    #  常量添加至符号表
    entry = Entry(name, KIND.CONSTANT, val)
    flag = table.add(entry)
    if flag == 1:
        msg = 'redeclaration: \'' + str(name) + '\''
        error(msg)


# <vardecl> → var <id>{,<id>};
def deal_var(table):
    #  移进<var>
    if SYMBOL[ptr] != KEYWORDS['var']:
        msg = 'expect \'var\''
        error(msg)
    nextptr()

    #  移进id
    if SYMBOL[ptr] != identifier:
        msg = 'expect identifier'
        error(msg)

    #  添加进入符号表并处理重定义
    name = get_id()
    entry = Entry(name, KIND.VARIABLE)
    flag = table.add(entry)
    if flag == 1:
        msg = 'redeclaration: \'' + str(name) + '\''
        error(msg)
    nextptr()

    #  循环var定义
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

    #  移进;
    if SYMBOL[ptr] == DELIMITERS[';']:
        nextptr()
    else:
        msg = 'expect \';\' after declaration'
        error(msg)


# <proc> → procedure <id>（[<id>{,<id>}]）;<block>{;<proc>}
def deal_procedure(table):
    #  移进procedure
    if SYMBOL[ptr] != KEYWORDS['procedure']:
        msg = 'expect \'procedure\''
        error(msg)
    nextptr()

    #  移进id
    if SYMBOL[ptr] != identifier:
        msg = 'expect identifier'
        error(msg)

    #  proc id加入符号表并查重
    tempname = get_id()
    tempentry = Entry(tempname, KIND.PROCEDURE)
    flag = table.add(tempentry)
    if flag == 1:
        msg = 'redeclaration: \'' + str(tempname) + '\''
        error(msg)
    #  建立该proc的新符号表
    newtable = Table(table)
    tablelist.append(newtable)
    nextptr()

    #  移进(
    if SYMBOL[ptr] != DELIMITERS['(']:
        msg = 'expect \'()\' after procedure declaration'
        error(msg)
    nextptr()

    #  移进proc的形参
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

    #  登记proc形参个数
    tempentry.para = num_para
    #  移进）与;
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

    #  规约block（在新的符号表递归）
    deal_block(newtable, tempentry)

    #  规约可能的并列proc
    while SYMBOL[ptr] == DELIMITERS[';']:
        nextptr()
        if SYMBOL[ptr] == KEYWORDS['procedure']:
            deal_procedure(table)
        else:
            msg = 'expect \'procedure\' after \';\''
            error(msg)


# <body> → begin <statement>{;<statement>}end
def deal_body(table):
    #  移进begin
    if SYMBOL[ptr] != KEYWORDS['begin']:
        msg = 'expect \'begin\''
        error(msg)
    nextptr()

    #  规约statement
    deal_statement(table)

    while SYMBOL[ptr] != KEYWORDS['end']:
        if SYMBOL[ptr] == DELIMITERS[';']:
            nextptr()
            deal_statement(table)
        else:
            msg = 'expect \';\' before new statement'
            error(msg)

    #  移进end
    if SYMBOL[ptr] == KEYWORDS['end']:
        nextptr()


# <statement> →  <id> := <exp>
#                |if <lexp> then <statement>[else <statement>]
#                |while <lexp> do <statement>
#                |call <id>（[<exp>{,<exp>}]）
#                |<body>
#                |read (<id>{，<id>})
#                |write (<exp>{,<exp>})
def deal_statement(table):
    #  规约赋值
    if SYMBOL[ptr] == identifier:
        deal_assign(table)
    #  规约条件语句
    elif SYMBOL[ptr] == KEYWORDS['if']:
        deal_if(table)
    #  规约while
    elif SYMBOL[ptr] == KEYWORDS['while']:
        deal_while(table)
    #  规约call
    elif SYMBOL[ptr] == KEYWORDS['call']:
        deal_call(table)
    #  规约read
    elif SYMBOL[ptr] == OPERATORS['read']:
        deal_read(table)
    #  规约write
    elif SYMBOL[ptr] == OPERATORS['write']:
        deal_write(table)
    #  规约body
    elif SYMBOL[ptr] == KEYWORDS['begin']:
        deal_body(table)
    #  未知语句
    elif SYMBOL[ptr] != KEYWORDS['end']:
        msg = 'illegal statement'
        error(msg)


# <id> := <exp>
def deal_assign(table):
    #  移进id
    name = get_id()
    nextptr()

    #  移进:=
    if SYMBOL[ptr] != OPERATORS[':=']:
        msg = 'expect \':=\' in assignment'
        error(msg)
    nextptr()

    #  规约expr
    deal_expr(table)

    #  查找id位置
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
        #  生成赋值代码
        codelist.append(Code('STO', l, a))


# if <lexp> then <statement>[else <statement>]
def deal_if(table):
    #  移进if
    nextptr()
    #  规约lexp
    deal_lexp(table)
    #  设置假出口指针
    falseout = Code('JPC', 0, None)
    codelist.append(falseout)
    #  移进then
    if SYMBOL[ptr] != KEYWORDS['then']:
        msg = 'expect \'then\' after \'if\''
        error(msg)
    else:
        nextptr()
        #  规约statement
        deal_statement(table)

    #  设置真过程结束跳转位置指针
    trueout = Code('JMP', 0, None)
    #  根据else是否存在，规约可能的else部分
    if SYMBOL[ptr] == KEYWORDS['else']:
        nextptr()
        #  加入真出口
        codelist.append(trueout)
        #  回填假出口
        falseout.a = len(codelist)
        #  规约statement
        deal_statement(table)
        #  回填真出口
        trueout.a = len(codelist)
    else:
        #  回填假出口
        falseout.a = len(codelist)


# while <lexp> do <statement>
def deal_while(table):
    #  移进while
    nextptr()
    current = len(codelist)
    #  规约lexp
    deal_lexp(table)
    #  预置假出口
    falseout = Code('JPC', 0, None)
    codelist.append(falseout)
    #  移进do
    if SYMBOL[ptr] == KEYWORDS['do']:
        nextptr()
        #规约statement
        deal_statement(table)
        #  返回while开始
        codelist.append(Code('JMP', 0, current))
        #  回填假出口
        falseout.a = len(codelist)
    else:
        msg = 'expect \'do\' after \'while\''
        error(msg)


# read (<id>{，<id>})
def deal_read(table):
    #  移进read(
    nextptr()
    if SYMBOL[ptr] == DELIMITERS['(']:
        nextptr()
        if SYMBOL[ptr] == identifier:
            #  移进id
            name = get_id()
            nextptr()
            #  查找id判断是否能够赋值
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
                #  添加赋值代码
                codelist.append(Code('OPR', 0, OPERATORS['read']))
                codelist.append(Code('STO', l, a))
            #  处理可能的后续赋值
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


# write (<exp>{,<exp>})
def deal_write(table):
    #  移进write(
    nextptr()
    if SYMBOL[ptr] == DELIMITERS['(']:
        nextptr()
        #  规约expr
        deal_expr(table)
        #  添加write代码
        codelist.append(Code('OPR', 0, OPERATORS['write']))
        #  处理后续write
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


# call <id>（[<exp>{,<exp>}]）
def deal_call(table):
    #  移进call
    nextptr()
    #  移进id
    if SYMBOL[ptr] != identifier:
        msg = 'expect identifier after \'call\''
        error(msg)

    #  查找id名称
    procname = get_id()
    nextptr()
    #  移进(
    if SYMBOL[ptr] != DELIMITERS['(']:
        msg = 'expect \'(\' after \'call\''
        error(msg)
    nextptr()

    #  移进参数
    para = 0  #  记录参数个数
    if SYMBOL[ptr] == identifier or SYMBOL[ptr] == number:
        para += 1
        deal_expr(table)
        #  传参
        codelist.append(Code('OPR', 2 + para, OPERATORS['post']))
        while SYMBOL[ptr] == DELIMITERS[',']:
            nextptr()
            para += 1
            deal_expr(table)
            codelist.append(Code('OPR', 2 + para, OPERATORS['post']))
        #  移进)
        if SYMBOL[ptr] == DELIMITERS[')']:
            nextptr()
        else:
            msg = 'expect \')\' after \'(\''
            error(msg)
    #  移进)
    elif SYMBOL[ptr] == DELIMITERS[')']:
        nextptr()
    else:
        msg = 'expect \')\' after \'(\''
        error(msg)

    #  查找proc
    (l, a, flag) = table.find(procname)
    if flag != isProc:
        msg = 'procedure not declared'
        error(msg)
    #  确认参数个数是否匹配
    if para != table.find_par(procname):
        msg = 'wrong number of parameters'
        error(msg)
    #  生成call代码
    codelist.append(Code('CAL', l, a))


# <exp> → [+|-]<term>{<aop><term>}
def deal_expr(table):
    #  移进expr可能的开头aop
    if SYMBOL[ptr] == OPERATORS['+']:
        nextptr()
        #  规约term
        deal_term(table)
    elif SYMBOL[ptr] == OPERATORS['-']:
        nextptr()
        #  规约term
        deal_term(table)
        #  栈顶取反
        codelist.append(Code('LIT', 0, -1))
        codelist.append(Code('OPR', 0, OPERATORS['*']))
    else:
        deal_term(table)
    #  运算处理
    while SYMBOL[ptr] == OPERATORS['+'] or SYMBOL[ptr] == OPERATORS['-']:
        opr = SYMBOL[ptr]
        deal_aop()
        deal_term(table)
        codelist.append(Code('OPR', 0, opr))


# <term> → <factor>{<mop><factor>}
def deal_term(table):
    #  规约factor
    deal_factor(table)
    while SYMBOL[ptr] == OPERATORS['*'] or SYMBOL[ptr] == OPERATORS['/']:  # 先乘除，后加减
        opr = SYMBOL[ptr]
        #  规约mop
        deal_mop()
        #  规约factor
        deal_factor(table)
        #  生成运算
        codelist.append(Code('OPR', 0, opr))


# <factor>→<id>|<integer>|(<exp>)
def deal_factor(table):
    #  移进id
    if SYMBOL[ptr] == identifier:
        name = get_id()
        nextptr()
        #  查找id
        (l, a, flag) = table.find(name)
        if a == 0 or a == isProc:
            msg = 'undeclared identifier'
            error(msg)
        #  取常数
        if flag == isConst:
            codelist.append(Code('LIT', 0, a))
            #  取变量
        else:
            codelist.append(Code('LOD', l, a))
    #  置常数于栈顶
    elif SYMBOL[ptr] == number:
        val = get_num()
        nextptr()
        codelist.append(Code('LIT', 0, val))
    #  移进(
    elif SYMBOL[ptr] == DELIMITERS['(']:
        nextptr()
        #  规约expr
        deal_expr(table)
        #  移进)
        if SYMBOL[ptr] == DELIMITERS[')']:
            nextptr()
        else:
            msg = 'expect \')\' after \'(\''
            error(msg)
    else:
        msg = 'expect factor in expression'
        error(msg)


# <lop> → =|<>|<|<=|>|>=
def deal_lop():
    #  移进lop
    if SYMBOL[ptr] == OPERATORS['='] or SYMBOL[ptr] == OPERATORS['<>'] or SYMBOL[ptr] == OPERATORS['<'] or SYMBOL[ptr] == OPERATORS['<='] or SYMBOL[ptr] == OPERATORS['>'] or SYMBOL[ptr] == OPERATORS['>=']:
        opr = SYMBOL[ptr]
        nextptr()
        return opr
    else:
        msg = 'illegal lop'
        error(msg)


# <lexp> → <exp> <lop> <exp>|odd <exp>
def deal_lexp(table):
    #  规约exp lop exp
    if SYMBOL[ptr] == OPERATORS['+'] or SYMBOL[ptr] == OPERATORS['-'] or SYMBOL[ptr] == identifier or SYMBOL[ptr] == number or SYMBOL[ptr] == DELIMITERS['(']:
        deal_expr(table)
        #  规约lop
        opr = deal_lop()
        deal_expr(table)
        codelist.append(Code('OPR', 0, opr))
    # 规约odd情况
    elif SYMBOL[ptr] == OPERATORS['odd']:
        nextptr()
        deal_expr(table)
        codelist.append(Code('OPR', 0, OPERATORS['odd']))
    else:
        msg = 'illegal lexp'
        error(msg)


def deal_aop():
    #  移进aop
    nextptr()


def deal_mop():
    #  移进mop
    nextptr()
