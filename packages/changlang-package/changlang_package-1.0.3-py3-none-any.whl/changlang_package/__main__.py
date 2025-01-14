import sys
from changlang_package.runtime import ChangLang

def main():
    if len(sys.argv) != 2:
        print("Usage: ChangLang <filename.cl>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "r", encoding="UTF-8") as file:
        code = file.read()

    interpreter = ChangLang()
    interpreter.compile(code)
    # interpreter.run(code, inputs=[2, 5])
    # inputs = []
    # expected_output = "Hello, Worl2d!"
    # success, actual_output = interpreter.test(code, inputs, expected_output)

    # if success:
    #     print("테스트 성공!")
    # else:
    #     print(f"테스트 실패: 예상 출력='{expected_output}', 실제 출력='{actual_output}'")
if __name__ == "__main__":
    main()