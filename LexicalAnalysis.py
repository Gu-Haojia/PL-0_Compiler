from Cache import *
from Symbol import *


def lexical_analysis(filename):
    Error = 0
    IDindex = 0
    if filename == '':
        filename = 'test.txt'
        print('使用默认测试文件生成')
    sourcefile = open(filename, 'r')
    outlog = open('log/lexical_log.txt', 'w')

    lines = sourcefile.readlines()
    line_num = 0
    for line in lines:
        line_num += 1
        index = 0
        while index < len(line):
            # 处理空格
            while line[index] == ' ':
                index += 1
            if line[index] == '\n':
                break
            if line[index].isalpha():  # 处理字母开头情况
                word = line[index]
                index += 1
                while index < len(line) and (line[index].isalpha() or line[index].isdigit()):
                    word += line[index]
                    index += 1

                # 处理关键字
                if word in KEYWORDS:
                    SYMBOL.append(KEYWORDS[word])
                    Position.append((line_num, index - len(word) + 1))
                    print(line_num, '<', word, ',KEYWORD >')
                    outlog.writelines('< ' + word + ',KEYWORD >' + '\n')

                # 处理单词型操作符
                elif word in OPERATORS:
                    SYMBOL.append(OPERATORS[word])
                    Position.append((line_num, index - len(word) + 1))
                    print(line_num, '<', word, ',OPERATOR >')
                    outlog.writelines('< ' + word + ',OPERATOR >' + '\n')

                # 处理标识符
                else:
                    SYMBOL.append(identifier)
                    Position.append((line_num, index - len(word) + 1))
                    if word not in IDENTIFIER:  # 加入标识符列表
                        IDENTIFIER[word] = IDindex  # 字典新增
                        IDindex = IDindex + 1
                    IDlist.append(word)
                    print(line_num, '<', word, ',IDENTIFIER >')
                    outlog.writelines('< ' + word + ',IDENTIFIER >' + '\n')
                del word
            elif line[index].isdigit():  # 处理数字开头
                word = line[index]
                index += 1
                while index < len(line) and line[index].isdigit():
                    word += line[index]
                    index += 1

                # 非法数字字母组合
                if line[index].isalpha():
                    while line[index].isalpha() or line[index].isdigit():
                        word += line[index]
                        index += 1
                    print('### ({},{}),error: character after number'.format(line_num, index - len(word) + 1))
                    Error = 1
                    outlog.writelines(
                        '### ({},{}),error: character after number\n'.format(line_num, index - len(word) + 1))

                # 处理数字
                else:
                    SYMBOL.append(number)
                    NUMlist.append(int(word))
                    Position.append((line_num, index - len(word) + 1))
                    print(line_num, '<', word, ',NUMBER >')
                    outlog.writelines('< ' + word + ',NUMBER >' + '\n')
                del word

            # 处理赋值
            elif line[index] == ':' and index + 1 < len(line):
                if line[index + 1] == '=':
                    SYMBOL.append(OPERATORS[':='])
                    Position.append((line_num, index + 1))
                    print(line_num, '<', ':=', ',ASSIGNMENT >')
                    outlog.writelines('< ' + ':=' + ',ASSIGNMENT >' + '\n')
                    index = index + 2
                else:
                    print('### ({},{}),error: expect \'=\' after \':\''.format(line_num, index))
                    Error = 1
                    outlog.writelines('### ({},{}),expect \'=\' after \':\''.format(line_num, index) + '\n')
                    index += 1

            # 处理<
            elif line[index] == '<' and index + 1 < len(line):
                if line[index + 1] == '=':
                    SYMBOL.append(OPERATORS['<='])
                    Position.append((line_num, index + 1))
                    print(line_num, '<', '>=', ',OPERATOR >')
                    outlog.writelines('< ' + '>=' + ',OPERATOR >' + '\n')
                    index = index + 2
                elif line[index + 1] == '>':
                    SYMBOL.append(OPERATORS['<>'])
                    Position.append((line_num, index + 1))
                    print(line_num, '<', '<>', ',OPERATOR >')
                    outlog.writelines('< ' + '<>' + ',OPERATOR >' + '\n')
                    index = index + 2
                else:
                    SYMBOL.append(OPERATORS['<'])
                    Position.append((line_num, index + 1))
                    print(line_num, '<', '<', ',OPERATOR >')
                    outlog.writelines('< ' + '<' + ',OPERATOR >' + '\n')
                    index += 1

            # 处理>
            elif line[index] == '>' and index + 1 < len(line):
                if line[index + 1] == '=':
                    SYMBOL.append(OPERATORS['>='])
                    Position.append((line_num, index + 1))
                    print(line_num, '<', '>=', ',OPERATOR >')
                    outlog.writelines('< ' + '>=' + ',OPERATOR >' + '\n')
                    index = index + 2
                else:
                    SYMBOL.append(OPERATORS['>'])
                    Position.append((line_num, index + 1))
                    print(line_num, '<', '>', ',OPERATOR >')
                    outlog.writelines('< ' + '>' + ',OPERATOR >' + '\n')
                    index += 1

            # 处理其它操作符
            elif line[index] in OPERATORS:
                SYMBOL.append(OPERATORS[line[index]])
                Position.append((line_num, index + 1))
                print(line_num, '<', line[index], ',OPERATOR >')
                outlog.writelines('< ' + line[index] + ',OPERATOR >' + '\n')
                index += 1

            # 处理界符
            elif line[index] in DELIMITERS:
                SYMBOL.append(DELIMITERS[line[index]])
                Position.append((line_num, index + 1))
                print(line_num, '<', line[index], ',DELIMITER >')
                outlog.writelines('< ' + line[index] + ',DELIMITER >' + '\n')
                index += 1

            # 出错处理
            else:
                print('### ({},{}),error: illegal character'.format(line_num, index + 1), line[index])
                Error = 1
                outlog.writelines(
                    '### ({},{}),error: illegal character'.format(line_num, index + 1) + line[index] + '\n')
                index += 1
    sourcefile.close()
    outlog.close()

    if Error == 1:
        print("词法分析出错")
        exit(-1)

    # for index in range(0, len(SYMBOL)):
    #    print(index, SYMBOL[index], Position[index])
