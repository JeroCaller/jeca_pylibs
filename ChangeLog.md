changelog
---
- - -
> 2023-11-28
> - loglib
>   - 코드 리팩토링
>       - logpackage.py 모듈 내 몇몇 클래스 독스트링 추가 및 수정.
>       - logpackage.py 모듈의 LogFileEnvironment 클래스에서, 로그 수준별 로그 파일 분류 옵션과 로그 수준별 최상위 로거 객체 이름 설정 기능을 분리하여 사용자가 로그 파일을 수준별 분류로 하지 않아도 로그 수준별 최상위 로거 객체 생성에 영향이 가지 않도록 수정함. 
>       - logexc.py 모듈 내 예외 클래스 이름을 짧게 줄임.
>       - tools.py의 DateTools.getDateStr() 키워드 인자 및 독스트링 수정.
>   - CustomizablePackageLogger, EasySetLogFileEnv, LogFileEnvironment 클래스 테스트를 위한 패키지 fixture 생성 및 테스트를 위한 코드 설정(loglib\tests\fixtures\testpkg2). -> 해당 패키지 fixture 자체 실행 결과 에러, 버그는 아직 발견하지 못함. -> 추후 여러 상황에 대한 테스트 코드 구현 예정.

> 2023-11-27
> - loglib
>   - 독스트링 내 설명 추가(EasySetLogFileEnv 클래스)
>   - 코드 리팩토링
>       - EasySetLogFileEnv 클래스 내에서 LogFileEnvironment 클래스를 인스턴스화하여 사용하는 composition 방법에서 상속으로 변경함. -> 사용자가 초기 설정을 한 이후, 중간에 초기 설정을 변경할 수 있도록 하기 위함.
>       - 독스트링 내 오타 수정.
>   - 로그 환경 설정 클래스 EasySetLogFileEnv 또는 LogFileEnvironment와 같이 
사용할 수 있는 패키지 수준 로그 클래스 CustomizablePackageLogger 코드 구현(테스트 코드 필요).

> 2023-11-24
> - loglib
>   - 코드 리팩토링
>       - tools.py 모듈 이동(sub_modules 디렉토리에서 현 패키지 디렉토리로 옮김) 및 그에 따른 모듈 임포트 관련 리팩토링 -> tools.py 일부 기능이 사용자도 사용해야하기 때문에 옮김.
>       - logpackage.py 내 에러 메시지를 logexc 모듈로 이동시킴.
>   - 로그 파일 환경 설정 기능의 LogFileEnvironment 클래스 코드 완성(테스트 필요).
>   - 로그 파일 환경 설정 클래스 LogFileEnvironment의 실행 과정을 더 명확하게 
해주는 클래스 EasySetLogFileEnv 코드 구현(테스트 코드 구현 필요).

> 2023-11-23
> - loglib
>   - 코드 부연 설명 추가 및 오타 수정. 코드 잘못 작성한 부분 수정.
>   - 현재 구현 중인 클래스 코드 일부 작성(구현 완료 및 테스트 통과 시 추후 상세히 설명).

> 2023-11-21
> - loglib
>   - 로그 파일 저장 디렉토리명에 쓰일 날짜 문자열 관련 기능 추가(tools.py) 및 관련 유닛 테스트 코드 추가.
>   - 로그 관련 예외 클래스 추가. - NotInitializedConfigError() -> 무언가를 초기 설정하지 않고 다른 기능 이용 시 발생시키는 예외.
>   - logpackage.py -> PackageLogger 클래스 추후 변경될 예정. 로그 관련 설정을 더 자유롭게 할 수 있도록 변경 중. 변경 내용은 일단 CustomizablePackageLogger 클래스에 반영할 예정. 이후 
변경 사항 완성 시 해당 클래스를 다시 PackageLogger 클래스로 변경할 수도 있음.

> 2023-11-16
> - README.md 내용 수정 -> 각 모듈, 라이브러리들에 대한 설명 추가.
> - loglib
>   - 로깅 코드를 일일이 삭제하지 않고도 로깅 기능을 키고 끌 수 있는 기능 추가.
(PackageLogger.setLoggingOnOff() 메서드로 구현함)
>   - 로그 파일 기록 및 관리 설정을 위한 코드 구현 중.
>   - 유닛 테스트 코드 리팩토링.

> 2023-11-03
> - loglib 코드 리팩토링. 

> 2023-11-02
> - 모든 모듈 코드 리팩토링.

> 2023-10-29
> - loglib에 패키지 내 모듈 내에서 자유롭게 함수 또는 메서드 내 특정 변수 
디버그 로깅 가능하게 하고 이에 대한 로거 객체들을 한 곳에서 관리하는 클래스 PackageLogger 추가. 
>   - PackageLogger 클래스 기능들
>       - 현재까지 생성한 로거 객체들을 계층 트리로 보여주는 기능. (따로 로그로 기록 가능)
>       - 특정 함수 또는 메서드 내에서 특정 변수만을 추적하여 디버그 로깅하고자 할 때 일일이 해당 함수 또는 메서드 이름 및 클래스, 모듈 이름까지 
logging.getLogger() 함수 인자에 대입하지 않아도 자동으로 해당 모듈, 클래스, 메서드 (함수라면 함수) 이름을 읽어들여 이를 토대로 로거 객체명을 자동 결정 및 자동 생성. 
>       - 변수 디버그 로그, 에러 로그 등을 기록하는 로그 파일들을 하나의 폴더에 자동으로 저장. -> 로그 파일 폴더 위치는 현재 실행시키는 파이썬 파일이 든 디렉토리 안에 생성됨. 
> - loglib에 대한 기초적인 사용 예시는 loglib/tests/fixtures/testpkg1 폴더 내 모듈들 참고. 
> - loglib에서 LoggerWHT 클래스 삭제 -> 잘못된 코드라서 삭제. 
> - loglib에서 logexp.py 이름을 logexc.py 이름으로 변경. 

> 2023-10-21
> - loglib 라이브러리 추가.
>   - 기존 logging.Logger 객체에는 로거 이름을 계층 구분하여 입력하면 나중에 부모-자식 로거 객체 계층이 어떤 구조를 띠고 있는지를 
한꺼번에 확인할 방법이 없다. 따라서 새로운 로거 객체를 생성하고 거기에 이름을 부여할 때마다 이를 기록하여 나중에 트리 구조로 보여주는 기능 추가. 
> - 특정 함수나 메서드의 실행 시작과 끝을 로깅해주는 데코레이터, 특정 함수, 메서드 실행 시 발생하는 예외를 로깅해주는 데코레이터 추가. 
- - -