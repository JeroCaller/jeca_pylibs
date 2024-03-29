직접 만든 파이썬에서 쓸 모듈, 라이브러리 모음.
===

# 구현한 라이브러리 목록
> - proglog
>   - 프로젝트 패키지 내에서 여러 모듈에 패키지 수준으로 
로깅 코드를 좀 더 간편하게 추가하여 로깅을 하는 라이브러리. 기존의 
logging 내장 라이브러리 사용 시 가능한 여러 설정 코드들을 캡슐화하여 로깅 관련 코드들을 최소화하도록 고안함. 
>   - 프로젝트 코드에 로깅 코드가 최소한으로 삽입되도록 하여 프로젝트 코드와 로깅 코드 간 결합도를 최소한으로 낮추도록 고안함.
>   - logging 내장 라이브러리의 Logger 객체들을 사용할 때 패키지 내에서 사용된 모든 Logger 객체들을 트리 구조로 나타내고 이를 로그 파일로 기록할 수 있는 기능.
>   - 기존의 logging 내장 라이브러리만을 사용하여 로깅 코드 작성 시 프로젝트의 코드에 로깅 코드가 너무 간섭하는 것 같았고, 로깅 관련 설정 코드들을 일일이 하나로 모아 캡슐화하기 귀찮았음. 또한, 부모-자식 로거 객체들의 계층 관계를 한 눈에 볼 수 있는 방법도 없었음. 이러한 기존 logging 라이브러리에서 느낀 단점들을 보완하고자 해당 라이브러리를 제작함. 

> - fdlib
>   - 루트 디렉토리 경로를 입력하면 해당 디렉토리 내 모든 최하위 디렉토리 및 파일들의 경로를 반환하거나 구조를 시각화해주는 기능.
>   - 텍스트 파일 생성 및 텍스트 쓰기, 읽기 코드를 캡슐화하여 더 간단하게 사용할 수 있는 기능.
---

# 구현한 모듈 목록
> - dirimporttool.py
>   - 상위 디렉토리 내 특정 모듈을 import하고자 할 때 사용할 수 있는 도구.

> - codenote.py
>   - 특정 코드에 메모를 달아놓고, 나중에 코드 실행 시 특정 코드에 달린 메모를 출력해주는 기능.
>   - 특정 함수 또는 메서드 내에 콘솔에 메시지를 출력하는 기능이 있을 때 위 아래로 경계선을 그어주는 기능.
