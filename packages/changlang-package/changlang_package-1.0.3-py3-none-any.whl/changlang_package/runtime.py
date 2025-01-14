import sys
from unittest.mock import patch
from io import StringIO

class ChangLang:
    def __init__(self):
        self.data = [0]*256

    def toNumber(self, code):
        tokens = code.split(' ')
        result = 1
        for token in tokens:
            num = (self.data[token.count('아')] if '숭이' in code else 0) + token.count('.') - token.count(',')
            result *= num
        return result

    @staticmethod
    def type(code):
        if '그냥' in code:
            return 'IF'
        if '메' in code:
            return 'MOVE'
        if '신창섭!' in code:
            return 'END'
        if '?' in code:
            return 'INPUT'
        if '정상화' in code and '해야겠지' not in code:
            return 'PRINT'
        if '정상화' in code and '해야겠지' in code:
            return 'PRINTASCII'
        if '싸' in code: 
            return 'DEF'

    def compileLine(self, code):
        if code == '':
            return None
        TYPE = self.type(code)

        # print(f"넘어온 커맨드: {code}, 타입: {TYPE}")

        if TYPE == 'DEF':
            var, cmd = code.split('알', 1)
            self.data[var.count('아')] = self.toNumber(cmd)
        elif TYPE == 'END':
            print(self.toNumber(code.split('신창섭!')[1]), end='')
            sys.exit()
        elif TYPE == 'INPUT':
            self.data[code.replace('?', '').count('아')] = int(input())
        elif TYPE == 'PRINT':
            print(self.toNumber(code[3:]), end='')
        elif TYPE == 'PRINTASCII':
            # print(code[3:-4])
            value = self.toNumber(code[3:-4])
            print(chr(value) if value else '\n', end='')
        elif TYPE == 'IF':
            cond, cmd = code.replace('그냥', '').replace('해줬잖아', '').split('다')
            if self.toNumber(cond) == 0:
                return cmd
        elif TYPE == 'MOVE':
            return self.toNumber(code.replace('메', ''))
        else:
            raise SyntaxError('정상화 실패! 정상화의 신에 걸맞은 언어를 쓰십시오.')

    def compile(self, code, check=True, errors=100000):
        jun = False
        recode = ''
        spliter = '\n' if '\n' in code else '~'
        code = code.rstrip().split(spliter)
        # print(code)
        if check and (code[0].replace(" ","") != '아니지나는정상화의신' or code[-1] != '아직남아있는최후의수단이있지' or not code[0].startswith('아니지나는정상화의신')):
            raise SyntaxError('정상화 실패! 정상화의 신에 걸맞은 언어를 쓰십시오.')
        code = code[1:len(code) - 1]
        index = 0
        error = 0
        # print(code, len(code))
        while index < len(code):
            errorline = index
            # print(index, code[index])
            c = code[index].strip()
            # print(c)
            res = self.compileLine(c)
            # print(f"res:{res} and c: {c}")
            if jun:
                jun = False
                code[index] = recode                
            if isinstance(res, int):
                index = res-2
            if isinstance(res, str):
                recode = code[index]
                code[index] = res
                index -= 1
                jun = True

            index += 1
            error += 1
            if error == errors:
                raise RecursionError(str(errorline+1) + '번째 줄에서 무한 루프가 감지되었습니다.')

    def compilePath(self, path):
        with open(path) as file:
            code = ''.join(file.readlines())
            self.compile(code)
    
    def run(self, code, inputs=None):
        """
        주어진 코드를 실행하며, 입력값을 자동으로 처리.
        :param code: 실행할 코드 문자열
        :param inputs: 자동으로 입력할 값들의 리스트
        """
        if inputs is None:
            inputs = []
        
        # Mock input()을 사용하여 입력값 자동 처리
        with patch('builtins.input', side_effect=inputs):
            self.compile(code)
        
    def test(self, code, inputs=None, expected_output=""):
        """
        주어진 코드와 입력값으로 실행한 결과가 예상 출력과 일치하는지 확인.
        :param code: 실행할 코드 문자열
        :param inputs: 자동으로 입력할 값들의 리스트
        :param expected_output: 예상되는 출력값
        :return: (성공 여부, 실행 결과 출력값)
        """
        if inputs is None:
            inputs = []

        # 출력값 캡처를 위해 sys.stdout 리다이렉트
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            with patch('builtins.input', side_effect=inputs):
                self.compile(code)
        finally:
            sys.stdout = old_stdout

        # 캡처된 출력값 가져오기
        actual_output = captured_output.getvalue().strip()

        # 결과 비교
        return actual_output == expected_output.strip(), actual_output    