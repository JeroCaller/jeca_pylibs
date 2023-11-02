"""
기능들.
1. 특정 코드에 메모를 남기고자 할 때 사용할 수 있는 기능. 모듈 실행 시 
해당 메모가 출력창에 출력된다. 
2. 어떤 함수 내에서 print() 함수를 사용하여 무언가를 계속 출력해야 하는데 
경계선이 필요할 때 쓸 수 있는 데코레이터.
3. 테스트 실패 시 그 원인과 해결책을 잠시 적어놓고, 나중에 해당 테스트 실행 시 
해당 정보들을 출력창에서 볼 수 있게 해주는 기능.
"""

class PrintBorderlineDecor():
    def __init__(
            self,
            borderline_char: str = '=',
            repeat_num: int = 60,
            ):
        """
        출력 경계선 관련 데코레이터 클래스

        매개변수 설명
        -----
        borderline_char: 경계선으로 지정할 문자.
        repeat_num: borderline_char로 지정된 문자로 경계선을 그을 때 문자의 반복 횟수. 
        """
        self.border = borderline_char
        self.repeat = repeat_num

    def __call__(self, func: callable):
        def wrapper(*args, **kwargs):
            print(self.border * self.repeat)
            result = func(*args, **kwargs)
            print(self.border * self.repeat)
            return result
        return wrapper


class TestFailureDecor():
    def __init__(
            self,
            reason: str = None,
            rusure: bool = False,
            solution: str = None):
        """
        테스트 실패 관련 데코레이터. 
        테스트 메서드 중 원하는 결과와 전혀 다른 결과가 나온 메서드에 대해서 
        해당 테스트가 실패했다는 것을 표시하고, 그 원인과 해결책을 서술할 수 있도록 
        고안한 데코레이터. 

        매개변수
        -----
        reason: 테스트 실패 원인을 문자열로 적은 변수. 실패 원인을 파악하지 못했다면 None으로 둔다. \n
        rusure: 테스트 실패 원인이 확실한지에 대한 변수. True: 확실, False: 확실하지는 않은 추측. \n
        solution: 테스트 실패 원인에 대한 해결책 문자열. 해결책을 모르겠다면 None으로 둔다. \n
        """
        self.reason = reason
        self.rusure = rusure
        self.solution = solution

    def __call__(self, func: callable):
        def wrapper(*args, **kwargs):
            print(f"{func.__name__} 테스트 메서드(또는 함수)는 테스트에 실패했습니다.")
            self.printReason()
            self.printSolution()
            return_result = func(*args, **kwargs)
            return return_result
        return wrapper

    @PrintBorderlineDecor(borderline_char="-")
    def printReason(self):
        if self.reason:
            if self.rusure:
                print("실패 원인을 파악하였습니다. 다음의 내용은 확실합니다.")
            else:
                print("실패 원인에 대해 확실치는 않지만 추측한 내용이 있습니다.")
            print("다음은 테스트 실패 원인입니다.")
            print(self.reason)
        else:
            print("아직 실패 원인을 파악하지 못했습니다.")

    @PrintBorderlineDecor(borderline_char="-")
    def printSolution(self):
        if self.solution:
            print("테스트 실패 원인에 대해서는 다음과 같은 내용으로 " \
                  + "해결할 수 있을 것으로 추측됩니다.")
            print(self.solution)
        else:
            print("아직 테스트 실패 원인에 대한 해결책을 찾지 못했습니다.")


class NoteForLater():
    def __init__(self, memo: str = ""):
        """
        특정 함수 또는 메서드에 대해 추후 기억을 위한 기록용 메모 데코레이터. 
        """
        self.memo = memo

    def __call__(self, func: callable):
        @PrintBorderlineDecor()
        def wrapper(*args, **kwargs):
            print(f"{func.__module__}.py의 {func.__name__} 함수(또는 메서드)")
            print("해당 모듈의 해당 함수 (또는 메서드)에 대해 다음의 노트가 있습니다.")
            print(self.memo)
            result = func(*args, **kwargs)
            return result
        return wrapper


@NoteForLater(memo="""
    메모 테스트.""")
def test():
    pass


if __name__ == '__main__':
    test()
