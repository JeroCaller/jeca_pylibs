changelog
---
- - -
> 2024-01-24
> - proglog.logpackage
>   - DetectErrorAndLog() 클래스 데코레이터에 새 기능 추가. 원래는 해당 데코레이터를 사용하면 에러 로깅 대상에서 에러가 나면 에러 로깅은 되나 에러 사실이 사용자에게 명시적으로 나타나지 않아 자칫 사용자가 에러를 무시하고 갈 수도 있다. 이를 방지하기 위해 on_error 변수에 True를 주면, 에러 로깅과 동시에 사용자에게 그대로 traceback 내역을 보여주도록 고안.
>   - 해당 새 기능 추가로 인한 테스트 코드 및 예제 코드 수정.
> - fdlib.fdhandler
>   - 특정 함수 실행 시 현재 작업 디렉토리 경로를 적절히 변경시킨 후 함수를 실행시켜주고, 함수 실행 후 다시 원래 경로로 되돌려주는 WorkCWD 클래스 데코레이터 추가. -> prolog의 테스트 모듈들의 버그를 고치기 위해 사용했던 기능을 그대로 가져와 업데이트함.

> 2024-01-23
> - loglib
>   - 테스트 코드 버그 수정.
>   - 독스트링 일부 수정.
>   - 코드 일부 추가 및 수정.
>   - loglib -> proglog로 해당 라이브러리 명칭 변경.

> 2024-01-22
> - loglib
>   - 테스트 코드 리팩토링. 라이브러리 패키지 구조 리팩토링.

> 2024-01-21
> - loglib.logpackage, test_lfm
>   - LogFileManager() 클래스 내 zip 압축 기능 관련 테스트 코드 구현 및 테스트 과정에서 발견한 버그 수정. (테스트 결과 성공.)

> 2024-01-19
> - fdlib.dirsearch
>   - 코드 수정 및 관련 테스트 코드 수정.
> - fdlib.fdhandler
>   - shutil.rmtree()에서 루트 디렉토리만 삭제하지 않는 기능으로 만든 함수 rmtree_except_root() 구현 및 관련 테스트 코드 추가. 
> - loglib.sub_modules
>   - 모듈 업데이트.
> - loglib.logpackage
>   - zip 압축 기능 초기 설계 완료.

> 2024-01-18
> - fdlib
>   - fdhandler.py
>   - make_zip_structure() 함수에 대한 테스트 코드 구현 및 테스트 실행으로 발견한 버그 수정.
>   - zip 파일을 압축 해제하고 특정 경로에 저장하는 과정을 조금 더 쉽게 한 decompress_zip() 함수 추가 및 관련 테스트 코드 구현 및 테스트 진행(테스트 성공).

> 2024-01-17
> - loglib
>   - logpackage.py -> LogFileManager()
>   - 테스트 코드 추가 및 테스트 진행 -> 테스트 성공.
>   - 테스트를 통해 발견한 버그 수정.
>   - 로그 파일에 대한 zip 파일 압축 기능 코드 설계(미완성).
> - fdlib
>   - fdhandler.py
>   - 루트 디렉토리의 구조를 그대로 유지한 채로 zip 파일로 압축하는 make_zip_structure() 함수 구현 - 추후 테스트 코드 작성 필요.

> 2024-01-12
> - fdlib
>   - fdhandler.py에 make_package() 함수 추가 및 관련 테스트 코드 추가 및 실행. 테스트 실행 결과, 통과.
> - loglib
>   - 코드 수정 및 추가.
>   - test_lfm.py에 테스트 코드 추가 (추후 추가 테스트 코드 구현 필요.)

> 2024-01-07
> - loglib
>   - 테스트 코드 수정.

> 2024-01-03
> - loglib
>   - 같은 날짜 디렉토리 내 로그 파일들에 대해 기준 용량을 넘어가면 기존 로그 내역은 새로운 파일에 이동시키고 기존 파일을 비운 후, 다시 새로운 로그 기록을 저장하는 rotating 기능 추가. -> logging.handlers.RotatingFileHandler() 클래스를 응용함.
>   - 해당 기능에 대한 testdata 패키지 및 테스트 코드 추가. -> 테스트 성공.
>   - test_logpackage.py
>       - 코드 수정.
>       - 제대로 된 테스트 환경이 아님을 확인함. 추후 문제 해결 필요.
>   - 용어 변경.

> 2024-01-01
> - loglib
>   - 테스트 코드 버그 수정.
>   - 코드 수정.
>   - 에러가 발생하지 않으면 이를 알리는 메시지를 로깅해주는 기능 추가.

> 2023-12-28
> - fdlib
>   - TextFileHandler 클래스에서 주어진 텍스트 경로의 중간 디렉토리가 없을 시 이를 자동으로 생성해주는 기능 추가. 관련 테스트 코드 추가 및 테스트 성공.
>   - json 파일 입출력 클래스 JsonFileHandler 클래스 추가. 관련 테스트 코드 추가 및 테스트 성공.
> - loglib
>   - 테스트 코드 추가 및 신규 테스트 코드를 위한 기존 testdata 코드 변경.
>   - 리팩토링

> 2023-12-27
> - fdlib
>   - dirsearch.py에서 사용자가 원하는 조건의 디렉토리인지를 검사하는 함수 추가.
>   - 새로 추가된 해당 함수에 대한 테스트 코드 작성 및 테스트 전원 통과.
> - loglib
>   - tools.py -> 오타 수정.
>   - logpackage.py
>       - 로그 파일들을 보관하는 베이스 디렉토리 내 날짜 디렉토리의 총 개수를 제한하고, 이를 초과하면 가장 오래된 날짜 디렉토리와 그 아래의 로그 파일들을 삭제해주는 LogFileManager 클래스의 rotateDateDirs() 메서드 구현 완료. 
>       - 특정 디렉토리와 내부 모든 요소들을 삭제할 때, 실수로 엉뚱한 디렉토리를 삭제하지 않도록 특정 조건의 디렉토리인지를 검사하는 코드 추가. 
>   - test.lfm.py -> rotateDateDirs() 테스트 코드 작성 및 해당 테스트 통과. (추후 다른 테스트가 필요할 것으로 여겨짐)

> 2023-12-24
> - loglib
> - 테스트 코드 추가. 해당 테스트 통과.

> 2023-12-23
> - loglib
> - 코드 오류 수정.
> - logpackage.py
>   - 로그 파일을 보관하는 날짜 디렉토리 개수 제한 메서드 설계 변경. 
(LogFileManager.rotateDateDirs() 메서드)
> - tools.py, test_tools.py
>   - LogFileManager.rotateDateDirs() 메서드에 사용될 부분 기능 개발.
>       - searchDateDir()의 내부 코드 수정. searchDateDirBirth()로 정해진 날짜 포맷 형식을 만족하는 이름을 가지는 날짜 디렉토리들의 생성 시각도 검색하는 기능 개발. 기존에 날짜 디렉토리명에서 날짜를 추출하여 날짜순으로 정렬하는 코드인 searchDateDir()는 '2100-01-01'과 같은 이름을 가지는 날짜 디렉토리들이 삽입되는 경우 의도와 다른 결과가 나올 수 있어 이를 디렉토리의 생성 시각을 직접 가져오는 방식인 searchDateDirBirth() 메서드 코드로 수정함. 
>       - 위 메서드들에 사용될 convertStrToDatetime() 메서드 구현. 
>   - 위에 언급된 메서드들을 테스트할 코드 추가 및 테스트 실행 -> 테스트 성공. 추후 테스트 코드 추가 예정.

> 2023-12-22
> - loglib
> - test_tools.py 
>   - 일부 테스트 코드 리팩토링.
>   - 테스트 코드 추가 및 테스트 실행 (테스트 성공)
> - tools.py
>   - 독스트링 수정.

> 2023-12-21
> - loglib
> - tools.py, test_tools.py
>   - tools.DateTools.isDateStr() 메서드 코드 수정. 특정 연, 월의 마지막 일수를 고려한 코드 추가. 해당 코드에 대한 테스트 코드 수정 및 추가. 테스트 성공.
>   - 날짜 문자열을 입력받으면 이를 datetime.date 객체로 변환하여 반환하는 메서드인 
DateTools.convertStrToDate() 메서드 및 관련 테스트 코드 추가. 테스트 성공.
>   - 루트 폴더 안에 날짜 문자열을 이름으로 갖는 모든 하위 디렉토리들의 경로와 그 문자열을 얻어 날짜순으로 정렬한 결과물을 반환하는 메서드인 Datetools.searchDateDir()
메서드 및 관련 테스트 코드 일부 추가. 현재까지 작성한 테스트 코드는 통과함. 추후 테스트 코드 추가 필요.

> 2023-12-20
> - loglib
> - tools.py
>   - 'YYYY-MM-N주' 형태의 날짜를 'YYYY-MM-DD'로 바꾸는 기능 구현 및 관련 테스트 코드 작성. 테스트 통과.

> 2023-12-18
> - loglib
> - 로그 파일명 뒤에 로깅하는 날짜를 YYYY-MM-DD 형태로 삽입하는 기능 추가 및 해당 기능을 디폴트로 설정.
> - 테스트 대상 모듈의 코드 변경으로 테스트 코드도 변경.
> - 변경한 테스트 코드로 테스트 수행 -> 테스트 통과.
> - 코드 리팩토링 및 오타 수정.

> 2023-12-13
> - loglib
> - 코드 리팩토링
>   - 기존 PackageLogger 클래스 삭제 및 관련 테스트 testdata 삭제.
>   - 기존 CustomizablePackageLogger 클래스 이름을 PackageLogger 이름으로 변경.
>   - 기존 testdata 패키지들의 이름 변경
>   - 기존 클래스 삭제 및 클래스명 변경으로 인한 모듈 import 관련 코드 리팩토링.

> 2023-12-12
> - loglib
>   - tools.py의 DateTools.isDateStr() 메서드 추가. 주어진 문자열이 DateTools.getDateStr()의 반환 형태 중 하나와 똑같은 날짜 형식인지 확인하는 메서드.
>   - logpackage.py의 LogFileManager() 클래스에 날짜 디렉토리명의 날짜 유효성 검사 코드 추가.

> 2023-12-11
> - fdlib
>   - fdhandler.py 생성 및 텍스트 파일 조작 클래스 TextFileHandler 추가
>       - 텍스트 파일 생성 및 텍스트 쓰기, 읽기 기능 추가.
>   - fdhandler.TextFileHandler 클래스에 대한 단위 테스트 코드 추가 및 테스트 진행(테스트 통과).
> - loglib
>   - LogFileManager 클래스 코드 일부 구현.

> 2023-12-09
> - fdlib
>   - dirsearch.py 생성 및 여러 기능 추가.
>       - 루트 디렉토리 경로가 주어지면 해당 디렉토리 내 모든 파일 및 디렉토리들의 경로를 반환하거나 그 구조를 시각화하는 기능.
>       - 여러 파일 및 디렉토리들의 경로 문자열들의 리스트를 문자열 길이 순으로 정렬하는 기능.
>   - dirsearch.py 내 기능들에 대한 단위 테스트를 위한 testdata 추가 및 단위 테스트 코드 추가. 테스트 수행 완료. (테스트 성공)

> 2023-12-05
> - loglib
>   - 패키지 testdata에 테스트를 위한 코드 추가.
>   - 패키지 testdata에 코드 추가로 발견한 에러 고침.

> 2023-12-04
> - loglib
>   - 단위 테스트 내 테스트 추가(일, 주, 월, 연별 및 로그 수준별 로깅 테스트)
>   - 단위 테스트를 위한 testdata에 코드 추가.
>   - 추가한 단위 테스트 모두 테스트 통과.
>   - logpackage.py의 LogFileEnvironment 클래스의 common formatter 형식 수정.

> 2023-12-01
> - loglib
>   - 단위 테스트 내 테스트 추가(향후 다른 테스트들도 추가 예정).
>   - 단위 테스트 실행으로 발견한 버그 수정. (tools.Datetools.combineDateToGetDateStr)
>   - 로그 파일들을 저장하는 베이스 디렉토리 내 로그 파일 및 날짜 
디렉토리들을 조작, 관리하는 LogFileManager 클래스 생성 및 구조 설정.

> 2023-11-30
> - loglib
>   - 독스트링 수정.
>   - 예외, 버그 수정을 위한 코드 수정.
>   - 단위 테스트를 위한 패키지 testdata 'testpkg3' 생성 및 단위 테스트 모듈 
'test_logpackage.py'와 연결하여 테스트 하기 위한 환경 설정 완료. (testpkg1, 2는 
해당 패키지 안의 main.py를 직접 실행시켜서 로그 파일이 생성되고 로깅이 되는지를 
확인하기 위한 용도였음. 추후 단위 테스트 모듈에 'testpkg3'에 대한 여러 테스트 코드 
추가 예정)

> 2023-11-28
> - loglib
>   - 코드 리팩토링
>       - logpackage.py 모듈 내 몇몇 클래스 독스트링 추가 및 수정.
>       - logpackage.py 모듈의 LogFileEnvironment 클래스에서, 로그 수준별 로그 파일 분류 옵션과 로그 수준별 최상위 로거 객체 이름 설정 기능을 분리하여 사용자가 로그 파일을 수준별 분류로 하지 않아도 로그 수준별 최상위 로거 객체 생성에 영향이 가지 않도록 수정함. 
>       - logexc.py 모듈 내 예외 클래스 이름을 짧게 줄임.
>       - tools.py의 DateTools.getDateStr() 키워드 인자 및 독스트링 수정.
>   - CustomizablePackageLogger, EasySetLogFileEnv, LogFileEnvironment 클래스 테스트를 위한 패키지 testdata 생성 및 테스트를 위한 코드 설정(loglib\tests\testdata\testpkg2). -> 해당 패키지 testdata 자체 실행 결과 에러, 버그는 아직 발견하지 못함. -> 추후 여러 상황에 대한 테스트 코드 구현 예정.

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
> - loglib에 대한 기초적인 사용 예시는 loglib/tests/testdata/testpkg1 폴더 내 모듈들 참고. 
> - loglib에서 LoggerWHT 클래스 삭제 -> 잘못된 코드라서 삭제. 
> - loglib에서 logexp.py 이름을 logexc.py 이름으로 변경. 

> 2023-10-21
> - loglib 라이브러리 추가.
>   - 기존 logging.Logger 객체에는 로거 이름을 계층 구분하여 입력하면 나중에 부모-자식 로거 객체 계층이 어떤 구조를 띠고 있는지를 
한꺼번에 확인할 방법이 없다. 따라서 새로운 로거 객체를 생성하고 거기에 이름을 부여할 때마다 이를 기록하여 나중에 트리 구조로 보여주는 기능 추가. 
> - 특정 함수나 메서드의 실행 시작과 끝을 로깅해주는 데코레이터, 특정 함수, 메서드 실행 시 발생하는 예외를 로깅해주는 데코레이터 추가. 
- - -