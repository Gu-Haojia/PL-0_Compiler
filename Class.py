from enum import Enum

FUN = Enum('FUN', ('LIT', 'LOD', 'STO', 'CAL', 'INT', 'JMP', 'JPC', 'OPR'))
KIND = Enum('KIND', ('CONSTANT', 'VARIABLE', 'PROCEDURE'))
isConst = 0
isVar = 1
isProc=2


class Code:
    def __init__(self, f, l, a):
        f = f.upper()  # 操作码
        if f in FUN.__members__:
            self.f = FUN[f]
        else:
            print('未定义的操作码')
            exit(-1)
        self.l = l  # 层次差
        self.a = a  # 位移量

    def __str__(self):
        return self.f.name + '\t\t' + str(self.l) + '\t\t' + str(self.a)


class Table:
    def __init__(self, parent=None):
        self.parent = parent
        self.entries = {}
        self.dx = 3
        if parent == None:
            self.level = 0
        else:
            self.level = parent.level + 1

    def add(self, entry):
        if entry.name in self.entries:
            return 1
        entry.level = self.level
        if entry.kind == KIND.VARIABLE:
            entry.adr = self.dx
            self.dx += 1
        self.entries[entry.name] = entry

    def getSize(self):
        return self.dx

    def find(self, name):  # 当标识符是变量时返回层差和地址Flag=1，当标识符是常量时返回层差和值Flag=0
        if name in self.entries:
            if self.entries[name].kind==KIND['CONSTANT']:  # 是常量
                return (0, self.entries[name].val, isConst)
            elif self.entries[name].kind==KIND['PROCEDURE']:  # 是常量
                return (0, self.entries[name].adr, isProc)
            else:
                return (0, self.entries[name].adr, isVar)
        elif self.parent == None:
            return (0, 0, 0)
        else:
            (l, a, flag) = self.parent.find(name)
            return (1 + l, a, flag)

    def find_val(self, name):  # 找到变量后，判断变量是否被赋值
        if name in self.entries and self.entries[name].kind == KIND['VARIABLE']:
            return self.entries[name].val_flag
        elif self.parent == None:  # 未找到
            return 0
        else:  # 向上寻找
            return (self.parent.find_val(name))

    def find_par(self, name):  # 查询过程的形参个数
        if name in self.entries and self.entries[name].kind == KIND['PROCEDURE']:
            return self.entries[name].para
        elif self.parent == None:  # 未找到
            return -1
        else:  # 向上寻找
            return (self.parent.find_par(name))

    def set_val(self, name):  # 记录被赋值的变量
        if name in self.entries and self.entries[name].kind == KIND['VARIABLE']:
            self.entries[name].val_flag = 1
            return 1
        elif self.parent == None:  # 未找到
            return 0
        else:  # 向上寻找
            self.parent.set_val(name)

    def __str__(self):
        msg = '___________________________________________________________\n'
        for i in self.entries.keys():
            msg += self.entries[i].__str__() + '\n'
        msg += '___________________________________________________________'
        return msg


class Entry:
    def __init__(self, name, kind, val=None):
        self.name = name
        self.kind = kind
        if kind != KIND.CONSTANT and val != None:
            print('非常量无法初始化值')
            return 1
        else:
            self.val = val
        self.level = None
        self.adr = None
        self.para = 0  # 过程形参个数，调用时匹配传参
        self.val_flag = 0  # 变量是否被赋值

    def __str__(self):
        msg = 'NAME:' + self.name + '\t\t' + self.kind.name + '\t\t'
        if self.val != None:
            msg += 'VAL:' + str(self.val) + '\t\t'
        else:
            msg += 'LEVEL:' + str(self.level) + '\t\t'
        msg += 'ADR:' + str(self.adr)
        return msg
