







<center><h1>
    《编译原理》课程设计
    </h1></center>
<center><h1>
    实验报告书
    </h1></center>


------

<center>
作者：顾浩嘉 姜玉先 赵安
    </center>
<center>
班级：1819002
    </center><center>
指导老师：杨志斌
</center><center>
地点：103实验室
</center><center>
时间：2021年12月27日
</center>




## 一、实验要求

​	设计一个 PASCAL 语言子集（PL/0）编译器。

​	PL/0 语言可以看成 PASCAL 语言的子集，它的编译程序是一个编译解释执行系统。PL/0 的目标程序为假想栈式计算机的汇编语言，与具体计算机无关。

​	PL/0 的编译程序和目标程序的解释执行程序可以采用 C、C++、Java 等高级语言书写。

​	（1）其编译过程采用一趟扫描方式，以语法分析程序为核心，词法分析和代码生成程序都作为一个独立的过程，当语法分析需要读单词时就调用词法分析程序，而当语法分析正确需要生成相应的中间代码时，则调用代码生成程序。

​	（2）用表格管理程序建立变量、常量和过程标识符的说明与引用之间的信息联系。

​	（3）用出错处理程序对词法和语法分析遇到的错误给出在源程序中出错的位置和错误性质。

​	（4）当源程序编译正确时，PL/0 编译程序自动调用解释执行程序，对中间代码进行解释执行，并按用户程序的要求输入数据和输出运行结果。



## 二、系统设计

### （1）语法图

```pascal
<prog> → program <id>；<block>
<block> → [<condecl>][<vardecl>][<proc>]<body>
<condecl> → const <const>{,<const>};
<const> → <id>:=<integer>
<vardecl> → var <id>{,<id>};
<proc> → procedure <id>（[<id>{,<id>}]）;<block>{;<proc>}
<body> → begin <statement>{;<statement>}end
<statement> → <id> := <exp>               
|if <lexp> then <statement>[else <statement>]
               |while <lexp> do <statement>
               |call <id>（[<exp>{,<exp>}]）
               |<body>
               |read (<id>{，<id>})
               |write (<exp>{,<exp>})
<lexp> → <exp> <lop> <exp>|odd <exp>
<exp> → [+|-]<term>{<aop><term>}
<term> → <factor>{<mop><factor>}
<factor>→<id>|<integer>|(<exp>)
<lop> → =|<>|<|<=|>|>=
<aop> → +|-
<mop> → *|/
<id> → l{l|d}  
<integer> → d{d}
```

​	注释：<prog>：程序 ；<block>：块、程序体 ；<condecl>：常量说明 ；<const>：常量；<vardecl>：变量说明 ；<proc>：分程序 ； <body>：复合语句 ；<statement>：语句；<exp>：表达式 ；<lexp>：条件 ；<term>：项 ； <factor>：因子 ；<aop>：加法运算符；<mop>：乘法运算符； <lop>：关系运算符。



### （2）核心数据结构

| 名称       | 类型 | 含义                     |
| ---------- | ---- | ------------------------ |
| SYMBOL     | list | 保留字符集               |
| Position   | list | 字符位置                 |
| IDENTIFIER | dict | 标识符字典               |
| IDlist     | list | 标识符名称（按顺序出现） |
| NUMlist    | list | 常数值（按顺序出现）     |
| codelist   | list | 代码存储器               |
| tablelist  | list | 符号表列表               |



### （3）程序目录

| python文件名       | 程序功能               |
| ------------------ | ---------------------- |
| Cache.py           | 存储主要数据结构       |
| Class.py           | 存储所有类             |
| Symbol.py          | 保留字符与运算符       |
| Compiler.py        | 主程序                 |
| LexicalAnalysis.py | 词法分析               |
| SyntaxAnalysis.py  | 语法分析及中间代码生成 |
| Interpreter.py     | 执行中间代码           |

### （4）中间代码表

| 代码            | 功能                                                        |
| --------------- | ----------------------------------------------------------- |
| LIT       0 ，a | 取常量a放入数据栈栈顶                                       |
| LOD    L ，a    | 取变量（相对地址为a，层差为L）放到数据栈的栈顶              |
| STO     L ，a   | 将数据栈栈顶的内容存入变量（相对地址为a，层次差为L）        |
| CAL     L ，a   | 调用过程（转子指令）（入口地址为a，层次差为L）              |
| INT      0 ，a  | 数据栈栈顶指针增加a                                         |
| JMP     0 ，a   | 无条件转移到地址为a的指令                                   |
| JPC      0 ，a  | 条件转移指令，转移到地址为a的指令                           |
| RED     L ，a   | 读数据并存入变量（相对地址为a，层次差为L）                  |
| WRT    0 ，0    | 将栈顶内容输出                                              |
| OPR    0  ,  0  | 过程调用结束后，返旧调用点并退栈                            |
| OPR    0  ,  11 | 从键盘读入一一个数字，置于栈项                              |
| OPR    0  ,  12 | 将栈顶元素输出到屏幕上                                      |
| OPR    0  ,  13 | 栈项元素的奇偶判断，结果值在栈顶                            |
| OPR    0  ,  14 | 次栈顶与栈顶是否相等，退两个栈元素，结果值进栈              |
| OPR    0  ,  16 | 次栈顶与栈顶相加，退两个栈元素，结果值进栈                  |
| OPR    0  ,  17 | 次栈项减去栈项，退两个栈元素，结果值进栈                    |
| OPR    0  ,  18 | 次栈顶乘以栈顶，退两个栈元素,结果值进栈                     |
| OPR    0  ,  19 | 次栈顶除以栈顶，迟两个栈元素，结果值进栈                    |
| OPR    0  ,  20 | 次栈顶与栈顶是否不等，退两个栈元素，结果值进栈              |
| OPR    0  ,  21 | 次栈项是否小于栈顶，退两个栈元系，结果值进栈                |
| OPR    0  ,  22 | 次栈顶是否小于等于栈顶，退两个栈元素，结果值进栈            |
| OPR    0  ,  23 | 次栈项是否大于栈顶，退两个栈元素，结果值进栈                |
| OPR    0  ,  24 | 次栈顶是否大于等于栈顶，退两个栈元素，结果值进栈            |
| OPR    0  ,  29 | 在调用子程序时，将参数传到变量对应的栈地址，a为变量的偏移量 |

### （5）数据流图

<img src="E:\Code\PL-0 Compiler\pic\pic1.png" alt="pic1" style="zoom:67%;" />

### （6）中间代码结构

<img src="E:\Code\PL-0 Compiler\pic\pic2.png" alt="pic2" style="zoom:67%;" />



## 三、系统实现

### （1）主要设计思路

**【词法分析设计思路】**

获取输入字符，按空格或界符分割，按首字母是数字还是字母进行条件区分，在Symbol中对应关键字类型。对于标识符，为其新建字典，并将对应查找标号按顺序放入一张列表之中。对于常数，将其值按顺序放入一张列表之中。并行进行错误处理。

**【语法分析与翻译设计思路】**

使用自上而下的递归下降分析法，由于PL-0语言文法在较大的语法单元几乎完全可以由唯一的终结符推导产生，这大大减少了程序的理解难度。对于一个语法单位（非终结符），基本过程是查找输入串对应终结符，查不到直接进入错误处理，按该终结符推导产生式，默认该产生式能被规约，直接递归调用该产生式对应的函数。
在翻译过程中，首先在开头预制JMP指令，在每个block处理结束时进行更新，以此生成入口代码。
对于每个block处理，过程会接收其直接外层过程的符号表作为参数，并建立该符号表的子表作为该过程的符号表。程序首先对所有定义进行处理，完成符号表，并计算该block需要的数据段长度，添加对应指令，接下来处理更小的部分。Block分析结束默认添加OPR，0,0指令来退栈。
对于过程调用，程序会无条件分配3个数据单元储存地址信息，再依据参数分配其它空间。
其它设计思路见对应注释。

**【解释执行模块】**

假想机由存储器CODE（列表）、数据存储器Data_Stack（栈）和四个寄存器构成 ，该假想机没有共运算用的寄存器，所有运算都要在数据栈STACK的栈顶两个单元之间进行，并用运算结果取代原来的两个运算对象而保留在栈顶，通过while循环对CODE中的中间代码进行解释执行，根据Run_flag（布尔变量）判断是否结束循环。



### （2）主要程序及函数实现

#### 1.主程序-Compiler.py

​	在主程序中，读入测试文件的路径，若无指定测试文件，则测试默认路径。

​	词法分析器中，一遍扫描文件中的字符，将词法分析结果保存在 lexical_log.txt 中。

​	从 lexical_log.txt 中读入单词，进行语法分析与语义分析，并生成中间代码，中间代码存放在文件 mid_code_log.txt 中。

​	最后从 mid_code_log.txt 中逐行读入并执行中间代码。

```python
if __name__ == '__main__':
    filename = input('请输入测试用例文件名（留空则默认测试）：')
    need_log = input('是否需要log?（输入非Y/y则不输出）：')
    print('------------------------------------------------')
    
    print('开始词法分析')
    lexical_analyse(filename, need_log)
    print('词法分析完成')
    print('------------------------------------------------')
    
    print('开始语法和语义分析')
    syntax_analyse(need_log)
    print('语法和语义分析完成')
    print('------------------------------------------------')
    
    print('开始解释执行')
    interpret()
    print('解释执行完成')
    print('------------------------------------------------')
```



#### 2. 词法分析器-LexicalAnalysis.py

处理关键字

```python
if word in KEYWORDS:
    SYMBOL.append(KEYWORDS[word])
    Position.append((line_num, index - len(word) + 1))
    olog.append(str(line_num)+' < ' + word + ',KEYWORD >')
    outlog.writelines('< ' + word + ',KEYWORD >' + '\n')
```

处理单词型操作符

```python
elif word in OPERATORS:
    SYMBOL.append(OPERATORS[word])
    Position.append((line_num, index - len(word) + 1))
    olog.append(str(line_num)+' < ' + word + ',OPERATOR >')
    outlog.writelines('< ' + word + ',OPERATOR >' + '\n')
```

处理标识符

```python
else:
    SYMBOL.append(identifier)
    Position.append((line_num, index - len(word) + 1))
    if word not in IDENTIFIER:  # 加入标识符列表
        IDENTIFIER[word] = IDindex  # 字典新增
        IDindex = IDindex + 1
    IDlist.append(word)
    olog.append(str(line_num)+' < ' + word + ',IDENTIFIER >')
    outlog.writelines('< ' + word + ',IDENTIFIER >' + '\n')
```

非法数字字母组合

```python
if line[index].isalpha():
    while line[index].isalpha() or line[index].isdigit():
        word += line[index]
        index += 1
    print('### ({},{}),error: character after number'.format(line_num, index - len(word) + 1))
    Error = 1
    outlog.writelines(
        '### ({},{}),error: character after number\n'.format(line_num, index - len(word) + 1))
```

处理数字

```python
else:
    SYMBOL.append(number)
    NUMlist.append(int(word))
    Position.append((line_num, index - len(word) + 1))
    olog.append(str(line_num)+' < ' + word + ',NUMBER >')
    outlog.writelines('< ' + word + ',NUMBER >' + '\n')
```

处理赋值

```python
elif line[index] == ':' and index + 1 < len(line):
    if line[index + 1] == '=':
        SYMBOL.append(OPERATORS[':='])
        Position.append((line_num, index + 1))
        olog.append(str(line_num)+' < ' + ':=' + ',ASSIGNMENT >')
        outlog.writelines('< ' + ':=' + ',ASSIGNMENT >' + '\n')
        index = index + 2
    else:
        print('### ({},{}),error: expect \'=\' after \':\''.format(line_num, index))
        Error = 1
        outlog.writelines('### ({},{}),expect \'=\' after \':\''.format(line_num, index) + '\n')
        index += 1
```

处理 <

```python
elif line[index] == '<' and index + 1 < len(line):
    if line[index + 1] == '=':
        SYMBOL.append(OPERATORS['<='])
        Position.append((line_num, index + 1))
        olog.append(str(line_num)+' < ' + '>=' + ',OPERATOR >')
        outlog.writelines('< ' + '>=' + ',OPERATOR >' + '\n')
        index = index + 2
    elif line[index + 1] == '>':
        SYMBOL.append(OPERATORS['<>'])
        Position.append((line_num, index + 1))
        olog.append(str(line_num)+' < ' + '<>' + ',OPERATOR >')
        outlog.writelines('< ' + '<>' + ',OPERATOR >' + '\n')
        index = index + 2
    else:
        SYMBOL.append(OPERATORS['<'])
        Position.append((line_num, index + 1))
        olog.append(str(line_num)+' < ' + '<' + ',OPERATOR >')
        outlog.writelines('< ' + '<' + ',OPERATOR >' + '\n')
        index += 1
```

处理 >

```python
elif line[index] == '>' and index + 1 < len(line):
    if line[index + 1] == '=':
        SYMBOL.append(OPERATORS['>='])
        Position.append((line_num, index + 1))
        olog.append(str(line_num)+' < ' + '>=' + ',OPERATOR >')
        outlog.writelines('< ' + '>=' + ',OPERATOR >' + '\n')
        index = index + 2
    else:
        SYMBOL.append(OPERATORS['>'])
        Position.append((line_num, index + 1))
        olog.append(str(line_num)+' < ' + '>' + ',OPERATOR >')
        outlog.writelines('< ' + '>' + ',OPERATOR >' + '\n')
        index += 1
```

处理其他操作符

```python
elif line[index] in OPERATORS:
    SYMBOL.append(OPERATORS[line[index]])
    Position.append((line_num, index + 1))
    olog.append(str(line_num)+' < ' + line[index] + ',OPERATOR >')
    outlog.writelines('< ' + line[index] + ',OPERATOR >' + '\n')
    index += 1
```

处理界符

```python
elif line[index] in DELIMITERS:
    SYMBOL.append(DELIMITERS[line[index]])
    Position.append((line_num, index + 1))
    olog.append(str(line_num)+' < ' + line[index] + ',DELIMITER >')
    outlog.writelines('< ' + line[index] + ',DELIMITER >' + '\n')
    index += 1
```

出错处理

```python
else:
    print('### ({},{}),error: illegal character'.format(line_num, index + 1), line[index])
    Error = 1
    outlog.writelines(
        '### ({},{}),error: illegal character'.format(line_num, index + 1) + line[index] + '\n')
    index += 1
if Error == 1:
   print("词法分析出错")
   exit(-1)
```



#### 3. 语法分析及中间代码生成器-SyntaxAnalysis.py

读入下一个符号

```python
def nextptr():
   global ptr
   ptr += 1
```

出错处理

```python
def error(msg):
    global ptr
    msg = str(Position[ptr]) + '  ' + msg
    print(msg)
    exit(-1)
```

读入下一个数字

```python
def get_num():
    global num_index
    number_val = NUMlist[num_index]
    num_index += 1
    return number_val
```

读入下一个标识符名称

```python
def get_id():
    global id_index
    name = IDlist[id_index]
    id_index += 1
    return name
```

入口函数

```python
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
```

<prog> → program <id>；<block>

```python
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
```

<block> → [<condeal>]  [<vardecl>]  [<proc>]   <body>

```python
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
```

<condecl> → const <const>{,<const>}

```python
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
```

<const> → <id>:=<integer>

```python
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
```

<vardecl> → var <id>{,<id>};

```python
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
```

<proc> → procedure <id>（[<id>{,<id>}]）;<block>{;<proc>}

```python
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
```

<body> → begin <statement>{;<statement>}end

```python
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
```

<statement> →  <id> := <exp>

​								|if <lexp> then <statement>[else <statement>]

​								|while <lexp> do <statement>

​								|call <id>（[<exp>{,<exp>}]）

​								|<body>

​								|read (<id>{，<id>})

​								|write (<exp>{,<exp>})

```python
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
```

<id> := <exp>

```python
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
```

if <lexp> then <statement>[else <statement>]

```python
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
```

while <lexp> do <statement>

```python
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
```

read (<id>{，<id>})

```python
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
```

write (<exp>{,<exp>})

```python
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
```

call <id>（[<exp>{,<exp>}]）

```python
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
```

<exp> → [+|-]<term>{<aop><term>}

```python
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
```

<term> → <factor>{<mop><factor>}

```python
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
```

<factor>→<id>|<integer>|(<exp>)

```python
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
```

<lop> → =|<>|<|<=|>|>=

```python
def deal_lop():
    #  移进lop
    if SYMBOL[ptr] == OPERATORS['='] or SYMBOL[ptr] == OPERATORS['<>'] or SYMBOL[ptr] == OPERATORS['<'] or SYMBOL[ptr] == OPERATORS['<='] or SYMBOL[ptr] == OPERATORS['>'] or SYMBOL[ptr] == OPERATORS['>=']:
        opr = SYMBOL[ptr]
        nextptr()
        return opr
    else:
        msg = 'illegal lop'
        error(msg)
```

<lexp> → <exp> <lop> <exp>|odd <exp>

```python
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
```

加法

```python
def deal_aop():
    #  移进aop
    nextptr()
```

乘法

```python
def deal_mop():
    #  移进mop
    nextptr()
```



#### 4. 执行中间代码-Interpreter.py

##### 假象机结构

存储器CODE：用来存放P的代码；
Data_Stack ：数据存储器STACK（栈）用来动态分配数据空间。
指令寄存器I:   存放当前要执行的代码
程序地址寄存器P:  存放下一条要执行的指令地址
栈顶指示器寄存器T: 指向数据栈STACK的栈顶
基地址寄存器B:  存放当前运行过程的数据区在STACK中的起始地址
该假想机没有共运算用的寄存器。
所有运算都要在数据栈STACK的栈顶两个单元之间进行，并用运算结果取代原来的两个运算对象而保留在栈顶。

```python
   code = codelist   
    Data_Stack = []   
    I = Reg()    
    P = Reg(0)   
    T = Reg(-1)  
    B = Reg(0)   
```

##### LTI

将常数放到运栈顶，a 域为常数.

```python
if instruction.f == FUN.LIT:
    push(Data_Stack, instruction.a, T)
    P.inc()
```

##### LOD

将变量放到栈顶。a 域为变量在所说明层中的相对位置，l 为调用层与说明层的层差值.

```python
elif instruction.f == FUN.LOD:
    badr = B.get()
    if instruction.l > 0:
        for _ in range(1, instruction.l + 1):
            badr = Data_Stack[badr + 2]
    push(Data_Stack, Data_Stack[badr + instruction.a], T)
    P.inc()
```

##### STO

将栈顶的内容送到某变量单元中。a 域为变量在所说明层中的相对位置，l 为调用层与说明层的层差值.

```python
elif instruction.f == FUN.STO:
    badr = B.get()
    if instruction.l > 0:
        for _ in range(1, instruction.l + 1):
            badr = Data_Stack[badr + 2]
    Data_Stack[badr + instruction.a] = pop(Data_Stack, T)
    P.inc()
```

##### CAL

调用过程的指令，a 域为变量在所说明层中的相对位置，l 为调用层与说明层的层差值

```python
elif instruction.f == FUN.CAL:
    if instruction.l == 0:  # 子过程调用,新过程的静态链为旧过程
        sl = B.get()
    else:  # 同级过程调用,新过程的静态链为旧过程的静态链
        sl = Data_Stack[B.get() + 2]
    if T.get() + B.get() < len(Data_Stack) - 1:
        Data_Stack[T.get() + B.get() + 1] = P.get()
        Data_Stack[T.get() + B.get() + 2] = B.get()
        Data_Stack[T.get() + B.get() + 3] = sl
        P.set(instruction.a)  # 设定入口地址
        B.set(B.get() + T.get() + 1)  # 设置基址寄存器
        T.set(3)  # 设置栈指针寄存器
    else:
        Data_Stack.append(P.get())  # 设定返回地址
        Data_Stack.append(B.get())  # 设定动态链
        Data_Stack.append(sl)  # 设定静态链
        P.set(instruction.a)  # 设定入口地址
        B.set(B.get() + T.get() + 1)  # 设置基址寄存器
        T.set(2)  # 设置栈指针寄存器
```

##### INT

为被调用的过程（或主程序）在运行栈中开辟数据区 a 域为开辟的个数.

```python
elif instruction.f == FUN.INT:
    while len(Data_Stack) < B.get() + instruction.a:
        push(Data_Stack, 0, T)
    P.inc()
```

##### JMP

无条件转移指令，a 为转向地址

```python
elif instruction.f == FUN.JMP:
    P.set(instruction.a)
```

##### JPC

条件转移指令，当栈顶的布尔值为False时，转向a 域的地址，否则顺序执行。

```python
elif instruction.f == FUN.JPC:
    if pop(Data_Stack, T) == 0:  # 为假
        P.set(instruction.a)
    else:  # 为真
        P.inc()
```

##### OPR

关系和算术运算。具体操作由a 域给出。运算对象为栈顶和次顶的内容进行运算，结果存放在次顶。a 域为0 时是退出数据区。

```python
elif instruction.f == FUN.OPR:
    if instruction.a == OPERATORS['+']:  # 加法
        b = pop(Data_Stack, T)  # 取出栈顶元素进行运算操作
        a = pop(Data_Stack, T)  # 取出栈顶元素进行运算操作
        push(Data_Stack, a + b, T)
    elif instruction.a == OPERATORS['-']:  # 减法
        b = pop(Data_Stack, T)
        a = pop(Data_Stack, T)
        push(Data_Stack, a - b, T)
    elif instruction.a == OPERATORS['*']:  # 乘法
        b = pop(Data_Stack, T)
        a = pop(Data_Stack, T)
        push(Data_Stack, a * b, T)
    elif instruction.a == OPERATORS['/']:  # 除法
        b = pop(Data_Stack, T)
        a = pop(Data_Stack, T)
        push(Data_Stack, a // b, T)
    elif instruction.a == OPERATORS['<>']:  # 不等于
        b = pop(Data_Stack, T)
        a = pop(Data_Stack, T)
        if a != b:
            push(Data_Stack, 1, T)
        else:
            push(Data_Stack, 0, T)
    elif instruction.a == OPERATORS['<']:  # 小于
        b = pop(Data_Stack, T)
        a = pop(Data_Stack, T)
        if a < b:
            push(Data_Stack, 1, T)
        else:
            push(Data_Stack, 0, T)
    elif instruction.a == OPERATORS['<=']:  # 小于等于
        b = pop(Data_Stack, T)
        a = pop(Data_Stack, T)
        if a <= b:
            push(Data_Stack, 1, T)
        else:
            push(Data_Stack, 0, T)
    elif instruction.a == OPERATORS['>']:  # 大于
        b = pop(Data_Stack, T)
        a = pop(Data_Stack, T)
        if a > b:
            push(Data_Stack, 1, T)
        else:
            push(Data_Stack, 0, T)
    elif instruction.a == OPERATORS['=']:  # 等于
        b = pop(Data_Stack, T)
        a = pop(Data_Stack, T)
        if a == b:
            push(Data_Stack, 1, T)
        else:
            push(Data_Stack, 0, T)
    elif instruction.a == OPERATORS['>=']:  # 大于等于
        b = pop(Data_Stack, T)
        a = pop(Data_Stack, T)
        if a >= b:
            push(Data_Stack, 1, T)
        else:
            push(Data_Stack, 0, T)
    elif instruction.a == OPERATORS['odd']:  # 判断奇数
        a = pop(Data_Stack, T)
        if a % 2 == 1:
            push(Data_Stack, 1, T)
        else:
            push(Data_Stack, 0, T)
    elif instruction.a == OPERATORS['read']:  # 读
        s = input('input:')
        if not s.isdigit():
            print('输入错误')
            exit(-1)
        else:
            push(Data_Stack, int(s), T)
    elif instruction.a == OPERATORS['write']:  # 写
        print('output:' + str(pop(Data_Stack, T)))

    elif instruction.a == OPERATORS['post']:  # post 传参
        post = pop(Data_Stack, T)
        badr = T.get() + instruction.l + 1 + B.get()
        while badr >= len(Data_Stack):
            Data_Stack.append(0)
        Data_Stack[badr] = post

    elif instruction.a == 0:  # OPR 0 0 退出数据区
        badr = Data_Stack[B.get() + 1]  # 获取动态链
        P.set(Data_Stack[B.get()])  # 恢复返回地址
        while len(Data_Stack) > B.get():  # 退栈
            Data_Stack.pop()
        T.set(B.get() - 1)  # 恢复栈顶指针寄存器
        B.set(badr)  # 恢复基址寄存器
    P.inc()
Run_flag = True if (B.get() != 0 or P.get() != len(code) - 1) else False
```



## 四、实验结果

### （1）测试1

#### 1.测试程序

​	程序功能：输入 b，输出结果为 2*(b+10).

```python
program test;
const  a:=10;
var    b,c;
procedure p();
  begin
    c:=b+a;
  end
begin
  read(b);
  while b>0 do
  begin
    call p();
    write(2*c);
    read(b)
  end
end
```

#### 2.词法分析结果

```python
< program,KEYWORD >
< test,IDENTIFIER >
< ;,DELIMITER >
< const,KEYWORD >
< a,IDENTIFIER >
< :=,ASSIGNMENT >
< 10,NUMBER >
< ;,DELIMITER >
< var,KEYWORD >
< b,IDENTIFIER >
< ,,DELIMITER >
< c,IDENTIFIER >
< ;,DELIMITER >
< procedure,KEYWORD >
< p,IDENTIFIER >
< (,DELIMITER >
< ),DELIMITER >
< ;,DELIMITER >
< begin,KEYWORD >
< c,IDENTIFIER >
< :=,ASSIGNMENT >
< b,IDENTIFIER >
< +,OPERATOR >
< a,IDENTIFIER >
< ;,DELIMITER >
< end,KEYWORD >
< begin,KEYWORD >
< read,OPERATOR >
< (,DELIMITER >
< b,IDENTIFIER >
< ),DELIMITER >
< ;,DELIMITER >
< while,KEYWORD >
< b,IDENTIFIER >
< >,OPERATOR >
< 0,NUMBER >
< do,KEYWORD >
< begin,KEYWORD >
< call,KEYWORD >
< p,IDENTIFIER >
< (,DELIMITER >
< ),DELIMITER >
< ;,DELIMITER >
< write,OPERATOR >
< (,DELIMITER >
< 2,NUMBER >
< *,OPERATOR >
< c,IDENTIFIER >
< ),DELIMITER >
< ;,DELIMITER >
< read,OPERATOR >
< (,DELIMITER >
< b,IDENTIFIER >
< ),DELIMITER >
< end,KEYWORD >
< end,KEYWORD >
```

#### 3.生成中间代码

```python
0:	JMP		0		7
1:	INT		0		3
2:	LOD		1		3
3:	LIT		0		10
4:	OPR		0		16
5:	STO		1		4
6:	OPR		0		0
7:	INT		0		5
8:	OPR		0		11
9:	STO		0		3
10:	LOD		0		3
11:	LIT		0		0
12:	OPR		0		23
13:	JPC		0		22
14:	CAL		0		1
15:	LIT		0		2
16:	LOD		0		4
17:	OPR		0		18
18:	OPR		0		12
19:	OPR		0		11
20:	STO		0		3
21:	JMP		0		10
22:	OPR		0		0
```

#### 4.运行结果

```python
开始解释执行
input:3
output:26
input:8
output:36
input:0
解释执行完成
```

### （2）测试2（以下省略词法）

#### 1.测试程序

​	程序功能：测试过程（procedure）的多重定义和调用

```python
program test;
var    c;
procedure p1();
  begin
    c:=1;
  end
;
procedure p2();
procedure p3();
  begin
    c:=3;
  end
  begin
    c:=2;
    call p3()
  end

begin
    call p1();
    call p2();
    write(c)
end
```

#### 2.生成中间代码

```python
0:		JMP		0		14
1:		INT		0		3
2:		LIT		0		1
3:		STO		1		3
4:		OPR		0		0
5:		INT		0		3
6:		LIT		0		3
7:		STO		2		3
8:		OPR		0		0
9:		INT		0		3
10:		LIT		0		2
11:		STO		1		3
12:		CAL		0		5
13:		OPR		0		0
14:		INT		0		4
15:		CAL		0		1
16:		CAL		0		9
17:		LOD		0		3
18:		OPR		0		12
19:		OPR		0		0
```

#### 3.运行结果

```python
开始解释执行
output:3
解释执行完成
```

### （3）测试3

#### 1.测试程序

​	程序功能：测试if   else

```python
program test;
var    a,b;

begin
    read(a);
    if a>0 then
        begin
            b:=1
        end
    else
        begin
            b:=2
        end;
    write(b)
end
```

#### 2.生成中间代码

```python
0:		JMP		0		1
1:		INT		0		5
2:		OPR		0		11
3:		STO		0		3
4:		LOD		0		3
5:		LIT		0		0
6:		OPR		0		23
7:		JPC		0		11
8:		LIT		0		1
9:		STO		0		4
10:		JMP		0		13
11:		LIT		0		2
12:		STO		0		4
13:		LOD		0		4
14:		OPR		0		12
15:		OPR		0		0
```

#### 3.运行结果

```python
开始解释执行
input:0
output:2
解释执行完成
开始解释执行
input:1
output:1
解释执行完成
```

### （4）测试4

#### 1.测试程序

​	程序功能：测试传参不匹配报错

```python
program test;
var    b,c;
procedure p1(b);
  begin
    c:=b;
  end
begin
    c:=1;
    call p1(2,3);
    write(c)
end
```

#### 2.运行结果

```python
开始语法和语义分析
(9, 17)  wrong number of parameters
```

### （5）测试5

#### 1.测试程序

​	程序功能：测试标识符作用域错误

```python
program test;
var    b,c;
procedure p1(b);
  var a;
  begin
    c:=b;
  end
begin
    c:=1;
    a:=2;
    call p1(2);
    write(c)
end
```

#### 2.运行结果

```python
开始语法和语义分析
(10, 9)  undeclared identifier
```



## 五、课程设计心得

​	通过课程设计的实现，加深了对《编译原理》课程内容的理解。

​	我们首先成功的实现了各个模块，从词法分析到语法分析，再到语义分析，然后生成中间代码，虽然缺少了优化和生成目标代码的过程，但是对程序编译的过程有了系统性的认识，尤其是对各模块之间的联系与接口的理解更加深刻，也认识到每一个环节的意义所在，以及它在整个流程中所扮演的角色。

​	对于不同的模块，我们综合考虑了不同的实现方法，针对本课程设计内容，选取最有效且容易实现的方法完成相关设计，如语法分析部分，我们采用LL(1)分析。这个过程既是设计的过程，也是学习巩固的过程，正是在这样思考与实践的过程中，让我们对课程知识点有了更详细的认识与记忆。

​	在做课程设计的过程中，我们对课程内容融汇贯通。与此同时，我们会想到很多杨老师在教学过程中渗透的思考方式与思维方法，初闻不知语中意，现在方得领悟。课程设计不只是对知识点的巩固，更是对老师解决问题的思维方法的掌握，后者更为重要，对我们的影响也更加深远。



## 六、建议和意见

​	1.建议课程设计的内容在课程起初就公布，一方面可以让我们预知将要学习的内容，有所准备与期待，另一方面提前准备，避免与期末复习冲突，造成不便。

​	2.建议在设计内容中添加优化部分的内容，有成员感觉本设计与八、九、十章内容相关性较弱。

## 七、小组分工

顾浩嘉：词法分析、语法分析、主程序

姜玉先：报告撰写

赵安：解释执行程序
