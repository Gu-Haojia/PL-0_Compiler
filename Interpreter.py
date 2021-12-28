from Cache import *
from Class import *
from Symbol import *


def push(Data_Stack, d,Reg):
    Data_Stack.append(d)
    Reg.inc()


def pop(Data_Stack, Reg):
    Reg.dec()
    return Data_Stack.pop()


def interpret():
    # 假想机结构
    code = codelist    # 存储器CODE，用来存放P的代码
    Data_Stack = []    # 数据存储器STACK（栈）用来动态分配数据空间
    I = Reg()    # 指令寄存器I:      存放当前要执行的代码
    P = Reg(0)   # 程序地址寄存器P:   存放下一条要执行的指令地址
    T = Reg(-1)  # 栈顶指示器寄存器T: 指向数据栈STACK的栈顶
    B = Reg(0)   # 基地址寄存器B:    存放当前运行过程的数据区在STACK中的起始地址
    # 该假想机没有共运算用的寄存器。
    # 所有运算都要在数据栈STACK的栈顶两个单元之间进行，并用运算结果取代原来的两个运算对象而保留在栈顶。

    Run_flag = 1
    while Run_flag:
        addr = P.get()  # 从程序地址寄存器中获取当前程序地址
        instruction = code[addr]
        I.set(instruction)  # 将当前指令赋值到指令寄存器中

        # LIT: 将常数放到运栈顶，a 域为常数
        if instruction.f == FUN.LIT:
            push(Data_Stack, instruction.a, T)
            P.inc()

        # LOD: 将变量放到栈顶。a 域为变量在所说明层中的相对位置，l 为调用层与说明层的层差值
        elif instruction.f == FUN.LOD:
            badr = B.get()
            if instruction.l > 0:
                for _ in range(1, instruction.l + 1):
                    badr = Data_Stack[badr + 2]
            push(Data_Stack, Data_Stack[badr + instruction.a], T)
            P.inc()

        # STO: 将栈顶的内容送到某变量单元中。a 域为变量在所说明层中的相对位置，l 为调用层与说明层的层差值
        elif instruction.f == FUN.STO:
            badr = B.get()
            if instruction.l > 0:
                for _ in range(1, instruction.l + 1):
                    badr = Data_Stack[badr + 2]
            Data_Stack[badr + instruction.a] = pop(Data_Stack, T)
            P.inc()

        # CAL: 调用过程的指令，a 域为变量在所说明层中的相对位置，l 为调用层与说明层的层差值
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

        # INT: 为被调用的过程（或主程序）在运行栈中开辟数据区 a 域为开辟的个数
        elif instruction.f == FUN.INT:
            while len(Data_Stack) < B.get() + instruction.a:
                push(Data_Stack, 0, T)
            P.inc()

        # JMP: 无条件转移指令，a 为转向地址
        elif instruction.f == FUN.JMP:
            P.set(instruction.a)

        # JPC: 条件转移指令，当栈顶的布尔值为False时，转向a 域的地址，否则顺序执行。
        elif instruction.f == FUN.JPC:
            if pop(Data_Stack, T) == 0:  # 为假
                P.set(instruction.a)
            else:  # 为真
                P.inc()

        # OPR:关系和算术运算。具体操作由a 域给出。运算对象为栈顶和次顶的内容进行运算，结果存放在次顶。a 域为0 时是退出数据区。
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
