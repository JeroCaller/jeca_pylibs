"""파일 및 디렉토리 검색 모듈.

이 모듈에서 사용하는 용어들.
1. entity: 파일과 디렉토리를 아우르는 말. 주로 파일과 디렉토리 
둘 중 하나이지만 정확히 둘 중 무엇일지 모를 때 사용. 또는 둘 다 
언급할 때에도 사용됨.

"""
import os
import heapq
from typing import TypeAlias

from submodules.tree import PathTree

# type aliases
Path: TypeAlias = str  # entity의 경로.
DirPath: TypeAlias = str

def sort_length_order(
        liststr: list[str],
        ascending: bool = True
    ) -> (list[str]):
    """문자열들의 리스트를 입력값으로 받으면, 문자열들의 길이 순으로 
    정렬한 결과를 반환하는 함수.

    파일 및 디렉토리들의 경로 문자열들을 리스트로 받았을 때 이를 
    경로 문자열 길이 순으로 정렬하고자 할 때 쓰는 함수.

    Parameters
    ----------
    liststr : list[str]
        정렬시키고자 하는 문자열들의 리스트
    ascending : bool, default True
        정렬 시 문자열들의 길이가 짧은 것부터 오름차순으로 정렬할지를 
        결정하는 매개변수. 
        True 시 오름차순, False 시 내림차순으로 정렬.

    Returns
    -------
    list[str]

    Examples
    --------

    >>> some_liststr = [
    ...     'hi',
    ...     'nice to meet you',
    ...     'how are you?',
    ...     'merci beaucoup'    
    ... ]
    >>> result = sort_length_order(some_liststr)
    >>> print(result)
    ['hi', 'how are you?', 'merci beaucoup', 'nice to meet you']

    """
    heap_list = []
    for string in liststr:
        if ascending:
            str_len = len(string)
        else:
            str_len = - len(string)
        heap_list.append((str_len, string))
    heapq.heapify(heap_list)
    result = []
    while heap_list:
        result.append(heapq.heappop(heap_list)[1])
    return result

def get_all_in_rootdir(
        root_dir: DirPath, 
        to_abspath: bool = True
    ) -> (list[str]):
    """루트 디렉토리 경로가 주어지면 해당 디렉토리 내 
    모든 파일들과 leaf 디렉토리의 경로들을 리스트로 묶어 반환.

    Parameters
    ----------
    root_dir : str
        루트 디렉토리 경로
    to_abspath : bool, default True
        루트 디렉토리 내 하위 파일 및 디렉토리들의 경로를 절대경로 또는 
        상대경로로 반환할 지 결정하는 매개변수. 
        True 시 절대경로로 반환한다.
        False 시 상대경로로 반환한다. 여기서 상대경로는 해당 절대경로에서 
        root_dir로 지정된 루트 디렉토리의 절대경로를 뺀 경로이다.

    Returns
    -------
    list[str]
        루트 디렉토리 내 모든 최하위 파일 및 디렉토리들의 절대경로의 
        리스트.
    
    """
    results: list[str] = []
    root_dir = os.path.abspath(root_dir)
    
    def search(dirpath: DirPath):
        entities = os.listdir(dirpath)
        if not entities:
            # leaf 디렉토리인 경우, 해당 디렉토리 경로를
            # 결과에 추가한다.
            if dirpath != root_dir:
                results.append(dirpath)
            return
        for entity in entities:
            if os.path.splitext(entity)[1]:
                # 해당 entity가 파일일 경우.
                results.append(os.path.join(dirpath, entity))
            else:
                # 해당 entity가 디렉토리일 경우.
                subdir_path = os.path.join(dirpath, entity)
                search(subdir_path)

    search(root_dir)

    if not to_abspath:
        for i, res in enumerate(results):
            results[i] = os.path.relpath(res, root_dir)
    
    return results

def get_ptree_from_rootdir(
        root_dir: DirPath, 
        to_abspath: bool = True
    ) -> (PathTree):
    """루트 디렉토리의 경로가 주어지면 해당 디렉토리 내 모든 
    최하위 디렉토리 및 파일들의 절대경로를 탐색한 후 이를 저장하는 
    PathTree 객체를 반환하는 함수.

    Parameters
    ----------
    root_dir : str
        루트 디렉토리의 경로
    to_abspath : bool, default True
        루트 디렉토리 내 최하위 디렉토리 및 파일들의 경로를 절대경로 
        또는 상대경로로 저장할지 결정하는 매개변수.
        True 시 절대경로로, False 시 루트 디렉토리명으로 시작하는 상대경로로 저장.

    Returns
    -------
    PathTree
        PathTree 객체

    Notes
    -----
    이 함수는 내부적으로 get_all_in_rootdir() 함수를 사용함.

    """
    leaf_path = get_all_in_rootdir(root_dir, to_abspath)
    ptree = PathTree(delimiter='\\')
    ptree.appendAll(leaf_path)
    return ptree

def visualize_rootdir(
        root_dir: DirPath,
        to_abspath: bool = True
    ) -> (str):
    """루트 디렉토리의 경로가 주어지면 해당 루트 디렉토리 내 모든 
    최하위 디렉토리 및 파일들을 탐색하여 이를 트리 구조 형태의 문자열로 
    재구성하여 반환하는 함수.

    Parameters
    ----------
    root_dir : str
        루트 디렉토리 경로
    to_abspath : bool, default True
        루트 디렉토리 내 최하위 디렉토리 및 파일들의 경로를 절대경로 
        또는 상대경로로 저장할지 결정하는 매개변수.
        True 시 절대경로로, False 시 루트 디렉토리명으로 시작하는 상대경로로 저장.

    Returns
    -------
    str

    Notes
    -----
    이 함수는 내부적으로 get_all_in_rootdir() 함수를 사용함.

    """
    leaf_path = get_all_in_rootdir(root_dir, to_abspath)
    ptree = PathTree(delimiter='\\')
    ptree.appendAll(leaf_path)
    return ptree.getTreeStructure()

def validate_if_your_dir_with_ext(
        root_dir: str, 
        include: list[str],
        not_include_ok: bool = True,
        dir_include_ok: bool = False
    ) -> (tuple[bool, list[str]]):
    """특정 디렉토리가 사용자가 원하는 조건을 만족시키는 디렉토리인지 
    검사하는 함수. 사용자가 지정한 확장자의 파일들만을 가진 디렉토리인지 그 외 
    원치 않은 확장자를 가지는 파일들도 있는지를 검사한다. 

    특정 디렉토리의 하위 파일들만을 검색하며, 하위 디렉토리가 있는 경우, 
    더 하위에 있는 디렉토리들 및 파일들은 검색하지 않는다. 

    Parameters
    ----------
    root_dir : str
        검사할 루트 디렉토리의 경로
    include : list[str]
        디렉토리에 꼭 포함되어야 할 파일 확장자 문자열들의 리스트. 해당 
        매개변수 내에 지정되지 않은 확장자를 가진 파일이 해당 디렉토리 내 
        검색될 경우, 해당 디렉토리는 사용자가 원하는 조건의 디렉토리가 아닌 
        것으로 판명됨. 
    not_include_ok : bool, defalut True
        include 매개변수로 지정한 확장자들 중 하나라도 해당 디렉토리에 
        존재하지 않더라도 지정되지 않은 확장자 파일만 없으면 되는지를 묻는 
        매개변수. 
        True 시, include 매개변수로 지정한 확장자들 중 한 개 이상 
        해당 디렉토리에 없거나 지정된 확장자 모두 존재하지 않는 빈 디렉토리라도 
        해당 조건은 통과한 것으로 간주.
        False 시, include 매개변수에 지정된 확장자들 중 단 하나의 확장자 파일이 
        디렉토리에 없으면 해당 디렉토리는 검사에 통과하지 못한 것으로 간주하고 
        False를 반환시키게 함.
    dir_include_ok : bool, default False
        루트 디렉토리 내에 하위 디렉토리를 포함해도 될지 여부를 묻는 매개변수. 
        True 시 하위 디렉토리가 있어도 되는 조건으로 설정됨. 
        False 시 하위 디렉토리가 있으면 다른 조건들과는 상관없이 사용자가 
        원하는 조건의 디렉토리가 아닌 것으로 판명함.

    Returns
    -------
    tuple[bool, list[str] | []]
        사용자가 원하는 조건을 만족시키는 디렉토리일 경우 True, 
        그렇지 않고 지정되지 않은 확장자 파일을 가진 디렉토리라면 False를 반환.
        조건을 만족하지 않은 디렉토리일 경우, 조건을 만족하지 않는 
        파일(또는 디렉토리)명들의 문자열이 리스트로 포함되어 두 번째 값으로 반환되고, 
        조건을 만족한 경우 빈 리스트가 두 번째 값으로 반환된다.
        not_include_ok = False인 상황에서 검사할 디렉토리 내에 include 매개변수로 
        지정된 확장자들 중 하나라도 없는 경우, 두 번째 값으로 'no .log'와 같이 
        'no'와 그 뒤에 해당 확장자명이 붙은 문자열이 포함되어 반환된다. 
    
    Examples
    --------
    
    예1) mydir라는 디렉토리 안에 .txt, .log 확장자 파일들 중 
    하나라도 갖고 있거나 아니면 다른 확장자 파일이 없는지 확인하고자 
    하는 케이스. 빈 디렉토리도 괜찮으니 .txt, .log 이외의 다른 
    확장자를 가진 파일(하위 디렉토리 포함)만 없으면 되는 경우. 
    이 때, 빈 디렉토리이거나 .txt, .log 둘 중 적어도 하나의 확장자를 
    가지는 파일이 단 한 개라도 있고, 그 외 확장자 파일이 없는 경우 
    해당 함수 실행 시 True를 반환받는다. 

    >>> path = 'C:\\mydir\\'
    >>> cond = validate_if_your_dir_with_ext(
    ... root_dir=path,
    ... include=['.txt', '.log'],
    ... not_include_ok=True)
    >>> cond
    (True, [])

    예2) mydir라는 디렉토리 안에 .txt, .log 확장자 파일 모두 
    각각 단 한개 라도 해당 디렉토리에 있는지 확인하는 케이스. 
    이 경우, 두 확장자 중 하나라도 빠지면 안되며, 빈 디렉토리도 안되고, 
    그 외 확장자를 가진 파일이 단 한개라도 있으면 안된다. 
    다음은 해당 디렉토리에 README.txt, Debug.log, how_to_use_sample.jpg가 
    있는 경우 False를 반환받는 예이다. 

    >>> path = 'C:\\mydir\\'
    >>> cond = validate_if_your_dir_with_ext(
    ... root_dir=path,
    ... include=['.txt', '.log'],
    ... not_include_ok=False)
    >>> cond
    (False, ['how_to_use_sample.jpg'])

    만약 위 예제2에서 'Debug.log' 파일이 없다면 반환값은 
    (False, ['how_to_use_sample.jpg', 'no .log'])가 된다. 

    예3) mydir라는 디렉토리 안에 .txt 확장자가 아닌 다른 확장자를 가진 
    파일들은 없는지 확인하는 케이스. 이 때, 해당 디렉토리 내에 하위 디렉토리를 
    가져도 상관없는 케이스. 
    다음은 해당 디렉토리에 README.txt 파일과 'log'라는 
    이름의 하위 디렉토리가 있을 경우 True를 반환받는 예이다. 

    >>> path = 'C:\\mydir\\'
    >>> cond = validate_if_your_dir_with_ext(
    ... root_dir=path,
    ... include=['.txt'],
    ... dir_include_ok=True)
    >>> cond
    (True, [])

    만약 위 예3에서 dir_include_ok=False시 반환값은 
    (False, ['log'])가 될 것이다.

    """
    sub_entities = os.listdir(root_dir)
    proce_exts = []
    # sub_entities 데이터 전처리.
    for entity in sub_entities:
        ext = os.path.splitext(entity)[1]
        if not ext:
            ext = 'dir'
        proce_exts.append(ext)
    sub_en_ex = zip(sub_entities, proce_exts)

    # include 매개변수 데이터 전처리.
    processed_include = []
    for ext in include:
        if not ext.startswith('.'):
            ext = '.' + ext
        processed_include.append(ext)

    is_passed: bool = True
    failed_because = []
    for entity, ext in sub_en_ex:
        if ((not dir_include_ok and ext == 'dir') or
            (ext != 'dir' and ext not in processed_include)):
            is_passed = False
            failed_because.append(entity)
    
    # include로 지정된 확장자들 중 대상 디렉토리에는 없는 
    # 확장자가 있는지 확인.
    if not not_include_ok:
        for inc in processed_include:
            if inc not in proce_exts:
                is_passed = False
                failed_because.append(f'no {inc}')

    return is_passed, failed_because

if __name__ == '__main__':
    # 테스트 용 코드.
    root_dir_path \
        = r'C:\my_coding_works\python\my_python_libs\fdlib\tests\testdata\testpkg'
    result = get_all_in_rootdir(root_dir_path, False)
    from pprint import pprint
    pprint(result)

    treestr = visualize_rootdir(root_dir_path, False)
    print(treestr)
    