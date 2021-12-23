from LexicalAnalysis import lexical_analysis
import SyntaxAnalysis
import Interpreter

if __name__ == '__main__':
    filename = input('请输入测试用例文件名（留空则默认测试）：')
    print('开始词法分析')
    lexical_analysis(filename)
    print('词法分析完成')
