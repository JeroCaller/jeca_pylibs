"""
패키지 내에서 하위 디렉토리에 있는 어떤 모듈을 A라 하고, 
상위 디렉토리에 있는 어떤 모듈을 B라 할 때, 모듈 A에서 모듈 B를 임포트하고자 할 때 
사용해야하는 sys.path.append() 함수 내 인자로 대입하는 모듈 B의 경로를 추출해주는 모듈. 

사용 예시1)
패키지 예)
/package
    B.py
    /sub_dir
        dirimporttool.py
        A.py

# A.py
import sys
from dirimporttool import get_super_dir_directly

super_dir = get_super_dir_directly(__file__, 2)
sys.path.append(super_dir)

import B
(생략...)

========
사용 예시2)
패키지 예)
/package
    main_module.py
    /sub_a
        a.py
    /sub_b
        dirimporttool.py
        b.py

# main_module.py
from sub_a.a import ...

# b.py
import sys
from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

import main_module
========
"""

import os

def get_current_absdir(filepath: str):
    """
    filepath로 대입받은 현재 파일의 현재 디렉토리의 절대주소 반환. \n
    ex)
    >>> get_current_absdir('C:\\python\\ilovepython\\yes.py')
    'C:\\\\python\\\\ilovepython'
    """
    return os.path.dirname(os.path.abspath(filepath))

def get_super_dir(current_dir, relative_height: int = 1) -> (str):
    """
    current_dir로 받은 현재 디렉토리보다 relative_height으로 받은 수만큼 
    상위에 존재하는 디렉토리를 절대경로로 반환. \n
    ex) 
    >>> get_super_dir('a/b/c', 2)
    'a'
    """
    super_dir = current_dir
    for _ in range(relative_height):
        super_dir = os.path.dirname(super_dir)
    return super_dir

def get_super_dir_directly(filepath: str, relative_height: int = 1) -> (str):
    """
    filepath로 대입받은 현재 파일의 절대경로에 대해, 
    relative_height 인자의 수만큼 상위에 존재하는 디렉토리를 
    절대경로로 반환.

    ex)
    >>> get_super_dir_directly('C:\\python\\ilovepython\\yes.py', 2)
    'C:\\\\'
    """
    c_dir = os.path.dirname(os.path.abspath(filepath))
    super_dir = c_dir
    for _ in range(relative_height):
        super_dir = os.path.dirname(super_dir)
    return super_dir

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    