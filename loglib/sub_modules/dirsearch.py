"""파일 및 디렉토리 검색 모듈.

이 모듈에서 사용하는 용어들.
1. entity: 파일과 디렉토리를 아우르는 말. 주로 파일과 디렉토리 
둘 중 하나이지만 정확히 둘 중 무엇일지 모를 때 사용. 또는 둘 다 
언급할 때에도 사용됨.

"""
import os
import heapq
from typing import TypeAlias

try:
    from tree import PathTree
except ModuleNotFoundError:
    from sub_modules.tree import PathTree

# type aliases
Path: TypeAlias = str  # entity의 경로.
DirPath: TypeAlias = str

def sort_length_order(
        liststr: list[str],
        ascending: bool = True
    ):
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
        False 시 상대경로로 반환한다. 상대경로는 root_dir 매개변수로 지정한 
        루트 디렉토리명으로 시작한다.

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
        temp_list = results.copy()
        super_dir_abspath = os.path.dirname(root_dir)
        for i, abspath in enumerate(temp_list):
            temp_list[i] = abspath.replace(super_dir_abspath, '')
            temp_list[i] = temp_list[i].lstrip('\\')
        results = temp_list.copy()
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

if __name__ == '__main__':
    root_dir_path \
        = r'C:\my_coding_works\python\my_python_libs\fdlib\tests\fixtures\testpkg'
    result = get_all_in_rootdir(root_dir_path, False)
    from pprint import pprint
    pprint(result)

    treestr = visualize_rootdir(root_dir_path, False)
    print(treestr)
    