from Cache import *
from Class import *
from Symbol import *


def push(data, d, T):
    data.append(d)
    T.inc()


def pop(data, T):
    T.dec()
    return data.pop()


def interpret():
    code=codelist
    data = []  # 数据段
    I = Reg()
    P = Reg()
    T = Reg()  # 数据栈栈顶指针
    B = Reg()
    P.set(0)
    T.set(-1)
    B.set(0)
    P_flag = 1
    while P_flag:
        addr = P.get()  # 获取地址
        instruction = code[addr]
        I.set(instruction)  # 读指令
        if instruction.f == FUN.LIT:  # 将常数放到运栈顶，a 域为常数。
            push(data, instruction.a, T)
            P.inc()
        elif instruction.f == FUN.LOD:  # 将变量放到栈顶。a 域为变量在所说明层中的相对位置，l 为调用层与说明层的层差值。
            badr = B.get()
            if instruction.l > 0:
                for _ in range(1, instruction.l + 1):
                    badr = data[badr + 2]
            push(data, data[badr + instruction.a], T)
            P.inc()
        elif instruction.f == FUN.STO:  # 将栈顶的内容送到某变量单元中。a,l 域的含义与LOD 的相同。
            badr = B.get()
            if instruction.l > 0:
                for _ in range(1, instruction.l + 1):
                    badr = data[badr + 2]
            data[badr + instruction.a] = pop(data, T)
            P.inc()
        elif instruction.f == FUN.CAL:  # 调用过程的指令。a 为被调用过程的目标程序的入中地址，l 为层差。
            if instruction.l == 0:  # 子过程调用,新过程的静态链为旧过程
                sl = B.get()
            else:  # 同级过程调用,新过程的静态链为旧过程的静态链
                sl = data[B.get() + 2]
            if T.get() + B.get() < len(data) - 1:
                data[T.get() + B.get() + 1] = P.get()
                data[T.get() + B.get() + 2] = B.get()
                data[T.get() + B.get() + 3] = sl
                P.set(instruction.a)  # 设定入口地址
                B.set(B + T + 1)  # 设置基址寄存器
                T.set(3)  # 设置栈指针寄存器
            else:
                data.append(P.get())  # 设定返回地址
                data.append(B.get())  # 设定动态链
                data.append(sl)  # 设定静态链
                P.set(instruction.a)  # 设定入口地址
                B.set(B + T + 1)  # 设置基址寄存器
                T.set(2)  # 设置栈指针寄存器
        elif instruction.f == FUN.INT:  # 为被调用的过程（或主程序）在运行栈中开辟数据区。a 域为开辟的个数。
            while len(data) < B.get() + instruction.a:
                push(data, 0, T)
            P.inc()
        elif instruction.f == FUN.JMP:  # 无条件转移指令，a 为转向地址。
            P.set(instruction.a)
        elif instruction.f == FUN.JPC:  # 条件转移指令，当栈顶的布尔值为非真时，转向a 域的地址，否则顺序执行。
            if pop(data, T) == 0:  # 为假
                P.set(instruction.a)
            else:  # 为真
                P.inc()
        elif instruction.f == FUN.OPR:  # 关系和算术运算。具体操作由a 域给出。运算对象为栈顶和次顶的内容进行运算，结果存放在次顶。a 域为0 时是退出数据区。
            if instruction.a == OPERATORS['+']:  # 加法
                b = pop(data, T)
                a = pop(data, T)
                push(data, a + b, T)
            elif instruction.a == OPERATORS['-']:  # 减法
                b = pop(data, T)
                a = pop(data, T)
                push(data, a - b, T)
            elif instruction.a == OPERATORS['*']:  # 乘法
                b = pop(data, T)
                a = pop(data, T)
                push(data, a * b, T)
            elif instruction.a == OPERATORS['/']:  # 除法
                b = pop(data, T)
                a = pop(data, T)
                push(data, a // b, T)
            elif instruction.a == OPERATORS['<>']:  # 不等于
                b = pop(data, T)
                a = pop(data, T)
                if a != b:
                    push(data, 1, T)
                else:
                    push(data, 0, T)
            elif instruction.a == OPERATORS['<']:  # 小于
                b = pop(data, T)
                a = pop(data, T)
                if a < b:
                    push(data, 1, T)
                else:
                    push(data, 0, T)
            elif instruction.a == OPERATORS['<=']:  # 小于等于
                b = pop(data, T)
                a = pop(data, T)
                if a <= b:
                    push(data, 1, T)
                else:
                    push(data, 0, T)
            elif instruction.a == OPERATORS['>']:  # 大于
                b = pop(data, T)
                a = pop(data, T)
                if a > b:
                    push(data, 1, T)
                else:
                    push(data, 0, T)
            elif instruction.a == OPERATORS['=']:  # 等于
                b = pop(data, T)
                a = pop(data, T)
                if a == b:
                    push(data, 1, T)
                else:
                    push(data, 0, T)
            elif instruction.a == OPERATORS['>=']:  # 大于等于
                b = pop(data, T)
                a = pop(data, T)
                if a >= b:
                    push(data, 1, T)
                else:
                    push(data, 0, T)
            elif instruction.a == OPERATORS['odd']:  # 判断奇数
                a = pop(data, T)
                if a % 2 == 1:
                    push(data, 1, T)
                else:
                    push(data, 0, T)
            elif instruction.a == OPERATORS['read']:  # 读
                s = input('input:')
                if not s.isdigit():
                    print('输入错误')
                    exit(-1)
                else:
                    push(data, int(s), T)
            elif instruction.a == OPERATORS['write']:  # 写
                print('output:' + str(pop(data, T)))

            elif instruction.a == OPERATORS['post']:  # post 传参
                post = pop(data, T)
                badr = T.get() + instruction.l + 1 + B.get()
                while badr >= len(data):
                    data.append(0)
                data[badr] = post

            elif instruction.a == 0:  # 退出数据区
                badr = data[B.get() + 1]  # 获取动态链
                P.set(data[B.get()])  # 恢复返回地址
                while len(data) > B.get():  # 退栈
                    data.pop()
                T.set(B.get() - 1)  # 恢复栈指针寄存器
                B.set(badr)  # 恢复基址寄存器
            P.inc()
        P_flag = True if (B.get() != 0 or P.get() != len(code) - 1) else False
