from LexicalAnalysis import lexical_analyse
from SyntaxAnalysis import syntax_analyse
from Interpreter import interpret

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
