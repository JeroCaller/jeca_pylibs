"""
개체들과 그 개체들의 트리 구조의 연결관계를 트리 구조로 표현. 
"""
from typing import Literal
import heapq
try:
    from submodules.my_queue import DynamicQueue
except ModuleNotFoundError:
    from my_queue import DynamicQueue


# type aliases
Parent = str
Child = str
Node = object
Depth = int
AbsPath = str
EmptyList = list
EmptyDict = dict
EmptyStr = str

# 상수 정의
# Tree().remove() 인자에 들어갈 수 있는 상수들.
REMOVEALL = 1
REMOVEONE = 2
DONTREMOVE = 3
RemoveMode = Literal[1, 2, 3] # type alias
# PathTree().getAllLeafAbs()의 how_to_sort 인자에 들어갈 수 있는 상수들.
ALPHABET = 4
LENGTH = 5
SortMode = Literal[4, 5] # type alias


# 사용자 정의 예외 클래스 모음
class ParentNoneError(Exception):
    def __init__(self):
        error_msg = """
        트리 내에서 새 개체가 직접 연결될 부모 개체를 지정하지 않았습니다. 
        만약 트리 내에 이미 root 노드가 있는 상태에서 새로 삽입할 노드의 부모 노드를 
        지정하지 않은 상태로 삽입하려하면, 새로 삽입할 노드를 root 노드로 인식하는데, 
        이때 트리 내 root 노드는 단 하나만 존재하도록 설정했으므로 이 경우에도 
        해당 에러가 발생할 수 있습니다. 
        """
        super().__init__(error_msg)


class NodeNotFoundError(Exception):
    def __init__(self, msg: str | None = None):
        error_msg = "트리 내에 찾고자 하는 노드가 존재하지 않습니다."
        if msg: error_msg = msg
        super().__init__(error_msg)


class NodeAlreadyExistsError(Exception):
    def __init__(self):
        error_msg = "트리 내에 중복되는 노드가 있습니다."
        super().__init__(error_msg)
        

class PathAlreadyExistsError(Exception):
    def __init__(self):
        error_msg = "이미 트리 내에 같은 경로를 가지는 노드가 있습니다."
        super().__init__(error_msg)


class RootNotUniqueError(Exception):
    def __init__(self):
        error_msg = "트리 내 root 노드는 단 하나여야 합니다. "
        super().__init__(error_msg)
# 사용자 정의 예외 클래스 모음 끝.


class Tree():
    def __init__(
            self,
            default_root: bool = False, 
            delimiter: str = '.',
            always_raise_error: bool = False
        ):
        """
        자식 노드를 여러 개 가지거나 아예 없을 수도 있는 구조의 트리. 
        루트 트리는 단 하나만 존재. 
        트리 전체 내부에 중복되는 노드는 허용하지 않음. 
        깊이가 서로 같은 특정 노드의 자식 노드들은 알파벳(한글) 오름차순으로 정렬됨. 

        매개변수
        -------
        default_root: 루트 노드가 별로 쓰이지 않을 것 같고 아무 값이나\
        할당해도 될 때 'root'라는 문자열을 가지는 노드를 생성하여 root 노드로 지정함.
        
        delimiter: 트리 계층 구조를 구분지어주는 기호. 기본은 '.'으로 설정됨. 
        예) a.b.c -> b는 a의 자식 노드, c는 b의 자식 노드.

        always_raise_error: append(), replace() 등 몇몇 메서드에는 특정 예외 발생 시 
        예외를 발생시킬 것인지 여부를 묻는 raise_error 키워드 인자가 있다. 일일이 해당 
        메서드들을 호출할때마다 정하기 귀찮을 때 해당 매개변수를 사용. 
        True시 해당 메서드들을 호출할 때마다 예외 발생 시 항상 그 예외를 일으킨다. 
        False시 메서드 호출 시 raise_error 인자값을 따른다. 
        각 메서드의 raise_error 인자보다 always_raise_error의 우선순위가 더 높다. 
        즉, always_raise_error가 True일 경우, raise_error가 False로 지정되어도 
        예외 상황 발생 시 예외를 일으킨다. always_raise_error를 False로 지정해야 
        raise_error 인자값을 따른다. 
        """
        self._node_number = 0
        self._delimiter = delimiter
        self._adj_list: dict[Parent, list[Child]] = {}
        self._r_adj_list: dict[Child, Parent] = {}
        if default_root: 
            self._root = 'root'
            self._adj_list[self._root] = []
            self._node_number += 1
        else: 
            self._root = None
        self.always_raise_error = always_raise_error

    def getRoot(self) -> (Node | None): return self._root

    @property
    def delimiter(self) -> (str): return self._delimiter

    @delimiter.setter
    def delimiter(self, new_delimiter: str) -> (None): 
        temp_adjl = {}
        for k, v in self._adj_list.items():
            new_k = k.replace(self._delimiter, new_delimiter)
            temp_adjl[new_k] = v
        self._adj_list = temp_adjl.copy()
        self._delimiter = new_delimiter

    def getRaiseErrorMode(self) -> (bool): 
        """
        트리 내 특정 메서드 호출 시 예외 상황이 발생했을 때 예외를 항상 
        일으킬 것인지에 대한 현재 상태를 반환.
        """
        return self.always_raise_error
    
    def setRaiseErrorMode(self, raise_error_mode: bool) -> (None): 
        """
        트리 내 특정 메서드 호출 시 예외 상황이 발생했을 때 예외를 항상 
        일으키도록 설정할 것인지에 대한 메서드. 
        True: 메서드 호출 때마다 예외 발생 시 예외를 일으킨다. 
        False: 예외가 발생해도 무시하고 메서드 실행을 중단한다. 
        """
        self.always_raise_error = raise_error_mode

    def lenTree(self) -> (int):
        """
        현재 트리 내에 존재하는 모든 노드들의 개수를 반환. 
        """
        return self._node_number
    
    def getAdjList(self) -> (dict[Parent, list[Child]]):
        """
        현재 트리를 구성하는 인접리스트를 반환.
        """
        return self._adj_list

    def _bfs(self) -> (list[tuple[Depth, Node]] | EmptyList):
        """
        트리 내 모든 노드들을 depth 순으로 하여 리스트로 반환. 
        depth는 루트 노드에서 0부터 시작함. 
        """
        if self._root is None: return []
        all_nodes = []
        queue = DynamicQueue()
        # (depth, node)
        queue.enqueue((0, self._root))
        while not queue.isEmpty():
            depth, node = queue.dequeue()
            all_nodes.append((depth, node))
            children = self.getChildren(node)
            if children is not None:
                for c in children: queue.enqueue((depth+1, c))
        return all_nodes
    
    def __repr__(self):
        """
        트리 내 모든 노드들을 depth 순으로 출력.
        """
        all_nodes = self._bfs()
        all_info = []
        for d, n in all_nodes:
            msg = f"depth: {d}, node: {n}."
            all_info.append(msg)
        if all_info == []: return "<빈 트리>"
        return '\n'.join(all_info)
    
    def getTreeStructure(self) -> (str):
        """
        트리 구조를 문자열로 구성하여 이를 반환. 
        같은 깊이의 노드들은 알파벳 오름차순으로 정렬하여 나타남. 

        구성 예1)\n
        root\n
        └ main
            ├ interface.py\n
            ├ log\n
            │   ├ debug.log\n
            │   └ error.log\n
            ├ main.dy\n
            ├ sound.py\n
            └ system.py
        
        구성 예2) \n
        root\n
        ├ 살 것들\n
        │   └ 마트\n
        │       └ 당근\n
        └ 할 일
            ├ 공부\n
            │    └ 과목\n
            │        ├ 자료구조\n
            │        └ 프로그래밍 언어\n
            │             └ 파이썬\n
            └ 집안일
                └ 설거지
                    └ 접시
        """
        if self._root is None: return "<빈 트리>"

        extension = "│"
        sub_dir_line = "└"
        sub_and_extension = "├"
        whitespace = " "
        one_tab_length = 2

        struct_str = []
        stack = [(0, self._root)]
        
        # depth가 같은 두 노드 a, b 노드가 있다고 가정하고, 두 노드에
        # 하위 트리가 존재할 경우, a 노드의 하위 트리가 구성될 동안 각 라인 
        # 앞에는 b 노드가 a 노드와 이어지는 것을 표현하기 위한 문자 "│"을 
        # 계속 하위 노드들의 맨 앞에 출력해야한다. 이를 위해선 a 노드의 하위 
        # 트리들이 한 줄씩 구성될 떄동안 b 노드가 아직 남아있음을 기록해야 한다.
        # 연결선 "│"으로 같은 깊이의 노드들을 연결하기 위해 시작 노드와 끝 노드
        # 를 기록하는 변수. 
        branch_stack = []

        while stack:
            depth, node = stack.pop()
            line = ""
            for iter_depth in range(depth+1):
                if iter_depth == depth:
                    line += f"{node}"
                elif iter_depth == (depth-1):
                    try:
                        branch_stack.remove((depth, node))
                    except ValueError:
                        if not branch_stack: line += sub_dir_line
                        elif iter_depth in dict(branch_stack): line += sub_and_extension
                    else:
                        if (iter_depth+1) in dict(branch_stack): line += sub_and_extension
                        else: line += sub_dir_line
                    line += whitespace
                else:
                    if (iter_depth+1) in dict(branch_stack): line += extension + (whitespace*(one_tab_length-1))
                    else: line += whitespace * one_tab_length

            struct_str.append(line)
            # 현재 노드의 자식 노드들을 스택에 삽입.
            children = self.getChildren(node)
            if children == [] or children is None: continue
            children.sort(reverse=True)
            for c in children: 
                stack.append((depth+1, c))
                branch_stack.append((depth+1, c))
        return "\n".join(struct_str)

    def _reverseAdjList(self) -> (dict[Child, Parent] | EmptyDict):
        """
        dict[Parent, list[Child]] 구조의 인접리스트를 
        dict[Child, Parent]으로 변환하고, 그 결과물의 복사본을 반환. 
        """
        new_dict = {}
        for k, v_list in self._adj_list.items():
            for v in v_list: new_dict[v] = k
        return new_dict
    
    def search(self, target_node: Node) -> (Node | None):
        """
        인자로 대입한 노드를 트리 내에서 찾아 이를 반환한다. 
        찾고자 하는 노드가 트리 내에 없다면 None을 반환.
        """
        if len(self._adj_list) == 0: return
        if len(self._adj_list) == 1:
            if self._adj_list[self._root] == []:
                if self._root == target_node: return self._root
                else: return
        
        self._r_adj_list = self._reverseAdjList()
        for node in self._r_adj_list.keys():
            while True:
                if node == target_node: return node
                try: node = self._r_adj_list[node]
                except KeyError: break
    
    def getChildren(self, parent: Node) -> (list[Child] | EmptyList | None):
        """
        인자로 주어진 노드를 트리 내에서 검색한 후, 해당 노드에 연결된 모든 자식 노드들을 
        리스트 형태로 반환. 주어진 노드가 트리에 없으면 None을 반환. 주어진 노드가 
        트리에 존재하지만 자식 노드가 아예 없는 경우 빈 리스트를 반환. 
        """
        try: return self._adj_list[parent]
        except KeyError: return

    def getParent(self, child: Node) -> (Parent | None):
        """
        인자로 주어진 노드를 트리 내에서 검색한 후, 해당 노드에 연결된 부모 노드를 반환. 
        주어진 노드가 트리 내에 존재하지 않거나 
        주어진 노드의 부모 노드가 존재하지 않을 경우, None을 반환. 
        """
        self._r_adj_list = self._reverseAdjList()
        try: return self._r_adj_list[child]
        except KeyError: return

    def append(
            self, 
            new_node: Node,
            parent: Node | None = None, 
            raise_error: bool = False
        ) -> (None):
        """
        트리 내에 특정 부모 노드에 새로운 노드를 연결하여 추가한다. 
        해당 부모 노드에 연결된 자식 노드들 중에 새로 삽입하고자 하는 노드가 이미 존재한다면 
        이 둘은 서로 연결되지 않음. 
        만약 현재 트리에 아무 노드가 없으면 인자로 입력된 부모 노드를 root 노드로 하고, 
        new_node를 root 노드의 자식 노드로 설정한다. 

        매개변수
        -------
        parent: new_node 변수에 root 노드로 지정할 인자를 대입했다면 
        부모 노드는 필요없으므로 해당 변수를 None으로 하면 된다. 
        만약 root 노드가 트리에 이미 있음에도 None으로 지정 시, 
        raise_error 여부에 따라 예외가 발생하거나 메서드 실행이 중단됨. 
        raise_error: 발생할 수 있는 각종 에러에 대해, raise_error 인자를 True로 설정 시,
        에러의 종류에 따라 예외를 발생시킨다. 예외 종류는 아래에 자세히 설명됨. 
        False로 설정 시 에러가 발생해도 이를 무시하고 메서드 실행을 중단한다. 

        발생할 수 있는 예외 종류
        -----
        ParentNoneError: 트리에 이미 root 노드가 있는 상태에서 
        parent 인자에 None을 입력한 경우.
        NodeNotFoundError: 지정한 부모 노드가 트리 내에 없을 경우. \n
        NodeAlreadyExistsError: 새로 삽입할 새 노드가 트리 내 기존 노드들 중 하나와 
        그 이름이 겹칠 경우. 
        """
        if self._root is None:
            if parent is None:
                self._root = new_node
                self._adj_list[new_node] = []
                self._node_number += 1
                return
            else:
                self._root = parent
                self._adj_list[parent] = [new_node]
                self._adj_list[new_node] = []
                self._node_number += 2
                return
        elif parent is None:
            if self.always_raise_error or raise_error: raise ParentNoneError()
            else: return
        
        if self.search(new_node): 
            if self.always_raise_error or raise_error: raise NodeAlreadyExistsError()
            else: return
        if self.search(parent) is None: 
            if self.always_raise_error or raise_error: raise NodeNotFoundError() 
            else: return

        try: 
            self._adj_list[parent].append(new_node)
        except KeyError: 
            self._adj_list[parent] = [new_node] 
        else: 
            self._adj_list[parent].sort()
        finally:
            # leaf 노드는 그 부모 노드의 자식 노드로 등록됨과 동시에, 
            # 인접리스트 딕셔너리에 {'leaf': []}와 같은 형태로 
            # value가 빈 리스트 형태로 삽입된다.
            self._adj_list[new_node] = []
        self._node_number += 1
    
    def appendAll(self, structure: list[str], raise_error: bool = False):
        """
        트리 구조를 나타낸 리스트를 입력하면 해당 구조 내 모든 노드들을 
        트리 구조에 맞게 트리에 추가함. 
        예)
        structure = [
            'root.살 것들.마트', '마트.당근', 'root.할 일.공부', 
            'root.할 일.집안일', '공부.과목.자료구조', '과목.프로그래밍 언어.파이썬',
            '집안일.설거지.접시',
        ]
        ->
        [
           'root.살 것들.마트.당근', 'root.할 일.공부.과목.자료구조',
           'root.할 일.공부.과목.프로그래밍 언어.파이썬', 
           'root.할 일.집안일.설거지.접시',
        ]
        -> 
        root\n
        ├ 살 것들\n
        │   └ 마트\n
        │       └ 당근\n
        └ 할 일
            ├ 공부\n
            │    └ 과목\n
            │        ├ 자료구조\n
            │        └ 프로그래밍 언어\n
            │             └ 파이썬\n
            └ 집안일
                └ 설거지
                    └ 접시

        매개변수
        -------
        raise_error: 발생할 수 있는 각종 에러에 대해, raise_error 인자를 True로 설정 시,
        에러의 종류에 따라 예외를 발생시킨다. 예외 종류에 대한 정보는 
        append() 메서드의 독스트링 참조. 
        """
        # 리스트 내 요소들의 순서에 상관없이 
        # 어떤 노드가 어떤 부모 노드에 연결되는 지 등을 자동으로 
        # 파악할 수 있게끔 함. 
        adj_list: dict[Parent, list[Child]] = {}
        
        def insert_adj_list(adjl: dict[Parent, list[Child]]):
            """
            반환 값
            ------
            dict[Parent, list[Child]]: 트리 구성에 성공. 
            """
            for data in structure:
                data = data.split(self._delimiter)
                for i in range(len(data)-1):
                    try:
                        if data[i+1] not in adjl[data[i]]: 
                            adjl[data[i]].append(data[i+1])
                    except KeyError:
                        adjl[data[i]] = [data[i+1]]
                        if data[i+1] not in adjl: adjl[data[i+1]] = []
            return adjl
        
        def reverse_adj_list(adjl: dict[Parent, list[Child]]):
            """
            dict[Parent, list[Child]] -> dict[Child, Parent]으로 변경한 결과를 반환.
            """
            r_adjl: dict[Child, Parent] = {}
            for k, v_list in adjl.items():
                for v in v_list: r_adjl[v] = k
            return r_adjl
        
        def find_root(radjl: dict[Child, Parent]) -> (Node | None):
            import random

            if radjl == {}: return None
            node = random.choice(list(radjl.keys()))
            while True:
                try: node = radjl[node]
                except KeyError: return node

        def find_top_nodes(radjl: dict[Child, Parent]) -> (list[Node] | EmptyList):
            top_nodes = []
            for node in radjl.keys():
                while True:
                    try:
                        node = radjl[node]
                    except KeyError:
                        if node not in top_nodes: top_nodes.append(node)
                        break
            return top_nodes
                
        def insert_into_tree(
                adjl: dict[Parent, list[Child]], 
                root: Node | list[Node]
            ):
            if self._root is None:
                self.append(root, raise_error=raise_error)
                stack = [root]
            else:
                # 이미 트리에 루트 노드나 그 이상의 노드가 존재할 경우에도 
                # 추가로 삽입하고자 하는 새 노드들을 삽입할 수 있어야 함. 
                stack = root
            while stack:
                node = stack.pop()
                try:
                    children = adjl[node]
                except KeyError:
                    continue
                else:
                    for c in children:
                        self.append(c, node, raise_error)
                        stack.append(c)

        adj_list = insert_adj_list(adj_list)
        r_adj_list = reverse_adj_list(adj_list)
        if self._root is None:
            r = find_root(r_adj_list)
            if r is None:
                if self.always_raise_error or raise_error: 
                    raise NodeNotFoundError("루트 노드 발견 못함.")
                else: 
                    return
            result = insert_into_tree(adj_list, r)
        else:
            top_nodes = find_top_nodes(r_adj_list)
            result = insert_into_tree(adj_list, top_nodes)
        return result

    def remove(
            self, 
            target_node, 
            mode: RemoveMode = REMOVEONE
        ) -> (bool):
        """
        주어진 노드를 트리 내에서 삭제한다. 
        만약 삭제하고자 하는 노드에 자식 노드가 1개 이상 연결되어 있는 경우, 
        mode 매개변수에 REMOVEALL, REMOVEONE, DONTREMOVE 상수들 중 하나를 
        대입하여 처리한다.

        REMOVEALL: 삭제하고자 하는 노드와 함께 그 자식 노드들도 모두 삭제한다. 

        REMOVEONE: 삭제하고자 하는 노드만 삭제하고, 그 하위 트리들은 모두 
        삭제한 노드의 부모 노드에 종속시킨다. 

        DONTREMOVE: 만약 삭제하고자 하는 노드가 자식 노드를 가지면 해당 노드와 
        그 자식 노드 모두 삭제하지 않는다. 오로지 자식 노드가 없는 leaf 노드일 
        경우에만 삭제한다. 
        
        반환값
        -----
        True: 트리 내 해당 노드를 삭제한 경우. 
        False: 트리 내 해당 노드를 삭제하지 않은 경우.
        """
        if self.search(target_node) is None: return False
        if mode == REMOVEALL:
            parent_node = self.getParent(target_node)
            queue = DynamicQueue()
            queue.enqueue(target_node)
            while not queue.isEmpty():
                node = queue.dequeue()
                children = self.getChildren(node)
                if children is not None:
                    for n in children: queue.enqueue(n)
                p = self.getParent(node)
                try: self._adj_list[p].remove(node)
                except KeyError: pass
                del self._adj_list[node]
                self._node_number -= 1
            if parent_node is not None: self._adj_list[parent_node].sort()
            return True
        elif mode == REMOVEONE:
            parent_node = self.getParent(target_node)
            children = self.getChildren(target_node)
            if children != [] and children is not None:
                self._adj_list[parent_node].extend(children)
            self._adj_list[parent_node].remove(target_node)
            self._adj_list[parent_node].sort()
            del self._adj_list[target_node]
            self._node_number -= 1
            return True
        else:
            # DONTREMOVE
            children = self.getChildren(target_node)
            if children is None or children == []:
                if target_node == self._root:
                    del self._adj_list[target_node]
                    self._root = None
                else:
                    parent = self.getParent(target_node)
                    if parent is not None:
                        self._adj_list[parent].remove(target_node)
                        del self._adj_list[target_node]
                self._node_number -= 1
                return True
            return False
        
    def replace(self, old_node, new_node, raise_error: bool = False) -> (bool):
        """
        기존 트리 내 특정 노드를 다른 노드로 바꾼다. 

        매개변수
        -------
        old_node: 바꾸고자 하는 트리 내 기존 노드. 
        new_node: old_node를 새로 바꿀 노드. 
        raise_error: 해당 메서드 실행 중 발생할 수 있는 에러들에 대해 
        예외를 일으킬지 무시할지에 대한 변수. True 시 각 에러 종류에 따른 예외를 발생. 
        False 시 예외를 일으키지 않고 중단한다. 
        예외 종류)
        NodeNotFoundError(): old_node가 트리 내에 존재하지 않을 경우. 
        NodeAlreadyExistsError(): 새로 바꾸고자 하는 new_node가 이미 
        트리 내에 존재할 경우. 
        
        반환값
        -----
        True: 성공적으로 노드를 바꿨을 경우. 
        False: 노드를 바꾸지 못한 경우. 
        """
        if self.search(old_node) is None: 
            if self.always_raise_error or raise_error: raise NodeNotFoundError()
            else: return False
        if self.search(new_node):
            if self.always_raise_error or raise_error: raise NodeAlreadyExistsError()
            else: return False
        # 새로 삽입할 노드의 자식 노드들을 기존 노드의 자식 노드들로 설정.
        self._adj_list[new_node] = self._adj_list[old_node]
        parent = self.getParent(old_node)
        if parent:
            self._adj_list[parent].remove(old_node)
            self._adj_list[parent].append(new_node)
            self._adj_list[parent].sort()
        del self._adj_list[old_node]
        return True
        
    def clear(self):
        """
        트리를 모두 비우고, 트리 설정도 모두 초기화된다. 
        always_raise_error 속성도 False로 초기화된다. 
        """
        self._adj_list.clear()
        self._r_adj_list.clear()
        self._node_number = 0
        self._root = None
        self.always_raise_error = False


class PathTree(Tree):
    def __init__(
            self, 
            default_root: bool = False, 
            delimiter: str = '.',
            always_raise_error: bool = False
        ):
        """
        파일, 디렉토리의 절대경로처럼 트리 내 노드들을 root 노드까지의 
        경로로 고유하게 식별하는 방식의 트리. 
        예) a 노드가 root 노드이고 자식노드가 b 노드일 경우, b 노드의 
        절대경로는 a.b이다. 
        절대경로가 다르면 이름이 같은 노드라도 트리 내 삽입을 허용한다. 
        반대로, 절대경로가 중복되는 노드를 트리에 삽입할 수는 없다. 
        이러한 특성에 의해, 부모 노드의 이름과 자식 이름의 노드가 겹쳐도 된다. 
        예) 'a.c.c'
        단, 같은 부모 노드에 같은 이름의 자식 노드들의 존재는 허용하지 않는다. 

        매개변수
        -------
        default_root: 루트 노드가 별로 쓰이지 않을 것 같고 아무 값이나\
        할당해도 될 때 'root'라는 문자열을 가지는 노드를 생성하여 root 노드로 지정함.
        
        delimiter: 트리 계층 구조를 구분지어주는 기호. 기본은 '.'으로 설정됨. 

        always_raise_error: append(), replace() 등 몇몇 메서드에는 특정 예외 발생 시 
        예외를 발생시킬 것인지 여부를 묻는 raise_error 키워드 인자가 있다. 일일이 해당 
        메서드들을 호출할때마다 정하기 귀찮을 때 해당 매개변수를 사용. 
        True시 해당 메서드들을 호출할 때마다 예외 발생 시 항상 그 예외를 일으킨다. 
        False시 메서드 호출 시 raise_error 인자값을 따른다. 
        각 메서드의 raise_error 인자보다 always_raise_error의 우선순위가 더 높다. 
        즉, always_raise_error가 True일 경우, raise_error가 False로 지정되어도 
        예외 상황 발생 시 예외를 일으킨다. always_raise_error를 False로 지정해야 
        raise_error 인자값을 따른다. 
        """
        super().__init__(default_root, delimiter, always_raise_error)
        self._adj_list: dict[AbsPath, list[Child]] = {}
        self._r_adj_list: dict[Child, list[AbsPath]] = {}
        if default_root:
            self._root = 'root'
            self._adj_list[self._root] = []
        else:
            self._root = None

    def _bfs(self):
        if self._root is None: return []
        all_nodes = []
        queue = DynamicQueue()
        # (depth, abspath)
        queue.enqueue((0, self._root))
        while not queue.isEmpty():
            depth, path = queue.dequeue()
            all_nodes.append((depth, path))
            if path == self._root: children = self._adj_list[self._root].copy()
            else: children = self.getChildren(path)
            if children != [] and children is not None:
                for c in children:
                    c = self.combineNodesToAbsPath(path, c)
                    queue.enqueue((depth+1, c))
        return all_nodes

    def __repr__(self):
        all_nodes = self._bfs()
        all_info = []
        for d, n in all_nodes:
            msg = f"depth: {d}, node: {n}."
            all_info.append(msg)
        if all_info == []: return "<빈 트리>"
        return '\n'.join(all_info)

    def isAbsPath(self, node: Node | AbsPath) -> (bool):
        """
        node 매개변수로 주어진 개체가 노드 이름인지 절대경로인지를 판단해주는 메서드. 
        절대경로일 경우 True, 노드 이름일 경우 False를 반환. 
        (root 노드는 절대경로로 고려하지 않는다)
        해당 노드가 트리에 존재하는지 여부는 상관없이 항상 작동한다. 
        단, 계층 구분 기호는 PathTree() 생성자의 인자 delimiter와 
        동일해야함. 
        """
        if self._delimiter in node: return True
        else: return False

    def basename(self, node_abs: AbsPath) -> (Node):
        """
        주어진 노드의 절대경로에서 노드 이름을 추출. 
        해당 절대경로가 트리 내에 존재하는지 여부에 상관없이 작동됨. 
        단, 계층 구분 기호는 PathTree() 생성자의 인자 delimiter와 
        동일해야함. 

        예)
        >>> PathTree().basename('a.b.c')
        'c'
        """
        return node_abs.split(self._delimiter)[-1]
    
    def dirname(self, node_abs: AbsPath) -> (AbsPath):
        """
        주어진 노드의 절대경로에서 부모 노드의 절대경로를 추출. 
        해당 절대경로가 트리 내에 존재하는지 여부에 상관없이 작동됨. 
        단, 계층 구분 기호는 PathTree() 생성자의 인자 delimiter와 
        동일해야함. 

        예)
        >>> PathTree().dirname('a.b.c')
        'a.b'
        """
        return self._delimiter.join(node_abs.split(self._delimiter)[:-1])

    def splitAbsPath(self, node_abs: AbsPath) -> (tuple[AbsPath, Node]):
        """
        주어진 노드 절대경로에서 현재 노드 이름과 해당 노드의 부모 노드의 절대경로로 
        분리하여 반환. 해당 절대경로가 트리에 존재하는지의 여부에 상관없이 작동한다. 
        단, 계층 구분 기호는 PathTree() 생성자의 인자 delimiter와 
        동일해야함. 

        예)
        >>> PathTree().splitAbsPath('a.b.c.d')
        ('a.b.c', 'd')
        """
        data = node_abs.split(self._delimiter)
        return self._delimiter.join(data[:-1]), data[-1]
    
    def combineNodesToAbsPath(
            self,
            node1: Node | AbsPath, 
            node2: Node | AbsPath
        ) -> (AbsPath):
        """
        두 노드의 이름 또는 절대경로를 하나로 합친 절대경로를 반환. 

        예)
        >>> PathTree().combineNodesToAbsPath('a.b.c', 'd.e')
        'a.b.c.d.e'
        """
        return self._delimiter.join([node1, node2])

    def _reverseAdjList(self) -> (dict[Child, list[Parent]]):
        """
        dict[AbsPath, list[Child]] 형태의 인접리스트 딕셔너리를 
        dict[Child, list[AbsPath]] 형태로 바꾼 결과를 반환. 
        AbsPath는 부모 노드의 절대경로를 의미한다. 
        """
        new_dict: dict[Child, list[Parent]] = {}
        for p, c_list in self._adj_list.items():
            for c in c_list:
                try: new_dict[c].append(p)
                except KeyError: new_dict[c] = [p]
        return new_dict

    def getAbsPath(self, target_node: Node) -> (list[AbsPath] | None):
        """
        target_node에 원하는 노드 이름 입력 시 
        해당 노드의 절대경로를 반환. 
        만약 트리 내에 해당 노드가 2개 이상이면 
        그에 해당하는 모든 절대경로들을 리스트로 반환.  
        예1)
        >>> tree_obj = PathTree()
        >>> tree_obj.appendAll(['a.b.c'])
        >>> tree_obj.getAbsPath('c')
        ['a.b.c']

        예2)
        >>> tree_obj = PathTree()
        >>> data = ['a.b.c', 'a.d.c']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.getAbsPath('c')
        ['a.b.c', 'a.d.c']

        예3)
        >>> tree_obj = PathTree()
        >>> data = ['a.c.c']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.getAbsPath('c')
        ['a.c', 'a.c.c']

        만약 target_node가 트리 내에 존재하지 않으면 None을 반환.
        """
        results = []
        for ab in self._adj_list.keys():
            if target_node == self.splitAbsPath(ab)[1]:
                results.append(ab)
        if results == []: return None
        return results

    def getChildren(
            self, 
            parent: Node | AbsPath
        ) -> (dict[AbsPath, list[Child]] | list[Child] | None):
        """
        parent 매개변수로 입력된 노드 또는 절대경로의 자식 노드들을 반환. 
        parent 매개변수에 노드 이름으로 입력 시 트리 내에 해당 이름을 가지는 
        모든 노드들의 모든 자식 노드들을 묶어 반환한다. 
        예)
        >>> tree_obj = PathTree()
        >>> data = ['a.b.c.d', 'a.b.c.e', 'a.d.c.f', 'a.d.c.g']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.getChildren('c')
        {'a.b.c': ['d', 'e'], 'a.d.c': ['f', 'g']}

        parent 매개변수로 입력된 노드와 이름이 같은 트리 내 노드들 중
        leaf 노드가 있으면 그 노드에 대해서는 빈 리스트를 value로 가지게 된다. 
        예)
        >>> tree_obj = PathTree()
        >>> data = ['a.b.c.d', 'a.e.c']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.getChildren('c')
        {'a.b.c': ['d'], 'a.e.c': []}

        만약 입력된 노드가 트리 내에 존재하지 않으면 None을 반환.

        parent 매개변수로 노드의 절대경로를 입력 시 그 노드의 자식 노드만을 
        반환한다. 
        예) 
        >>> tree_obj = PathTree()
        >>> data = ['a.b.c.d', 'a.b.c.e']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.getChildren('a.b.c')
        ['d', 'e']

        parent 매개변수로 대입받은 노드 절대경로는 존재하나 그 자식 노드가 없으면 
        빈 리스트를 반환.
        만약 parent 매개변수로 입력된 절대경로가 트리 내에 존재하지 않으면 
        None을 반환. 
        """
        if self.isAbsPath(parent):
            try: return self._adj_list[parent].copy()
            except KeyError: return None
        else:
            results = {}
            t_node_abs = self.getAbsPath(parent)
            if t_node_abs is None: return None
            for ab, c_list in self._adj_list.items():
                if ab in t_node_abs: results[ab] = c_list
            return results

    def getParent(self, child: Node | AbsPath) -> (list[AbsPath] | AbsPath | None):
        """
        child 매개변수로 입력된 노드 또는 절대경로의 부모 노드를 반환. 
        child 매개변수에 노드 이름 입력 시 트리 내에 같은 이름을 가지는 
        모든 노드들의 부모 노드들을 반환한다. 

        예)
        >>> tree_obj = PathTree()
        >>> data = ['a.b.c', 'a.d.c']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.getParent('c')
        ['a.b', 'a.d']

        만약 child 매개변수에 해당하는 트리 내 노드들 중 하나가 root 노드라면 
        root 노드는 부모 노드가 없으므로 리스트 안에 ['']와 같이 빈 문자열이 포함된다. 
        반면, 해당 노드가 트리 내에 존재하지 않으면 None을 반환. 

        예1)
        >>> tree_obj = PathTree(default_root=True)
        >>> tree_obj.getParent('root')
        ['']

        예2)
        >>> tree_obj = PathTree(default_root=True)
        >>> tree_obj.append('a', 'root')
        >>> print(tree_obj.getParent('b'))
        None

        child 매개변수에 노드의 절대경로 입력 시 일단 해당 절대경로가 
        트리 내에 존재하는지 확인 후, 존재하면 해당 노드의 부모 노드만을 반환. 

        예) 
        >>> tree_obj = PathTree()
        >>> data = ['a.b.c']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.getParent('a.b.c')
        'a.b'

        해당 절대경로가 트리 내에 존재하지 않으면 None, 
        주의) root 노드를 인자로 입력 시, root 노드는 절대경로가 아닌 
        노드 이름으로 취급한다. 

        예)
        >>> tree_obj = PathTree(default_root=True)
        >>> print(tree_obj.getParent('a.b.c'))
        None
        """
        if self.isAbsPath(child):
            if self.search(child): return self.dirname(child)
            else: return None
        else:
            results = []
            for key in self._adj_list.keys():
                parent_abs, base_node = self.splitAbsPath(key)
                if base_node == child: results.append(parent_abs)
            if results == []: return None
            return results

    def search(self, target_node: Node | AbsPath) -> (AbsPath | list[AbsPath] | None):
        """
        특정 노드가 트리 내에 존재하는지 검색하는 메서드. 

        매개변수
        -------
        target_node: 노드 이름으로 입력 시 해당 노드 이름을 절대경로로 가지는 모든 
        노드들의 절대경로들을 리스트로 묶어 반환. 

        예1) 
        >>> tree_obj = PathTree()
        >>> data = ['a.b.c', 'a.d.c']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.search('c')
        ['a.b.c', 'a.d.c']

        예2)
        >>> tree_obj = PathTree()
        >>> data = ['a.a.b', 'a.b.c']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.search('a')
        ['a', 'a.a']
        
        트리 내에 존재하지 않는 노드라면 None을 반환. 

        만약 절대경로로 입력 시, 트리 내에 존재하는 절대경로라면 그 절대경로를 그대로 반환. 
        예) 
        >>> tree_obj = PathTree()
        >>> tree_obj.appendAll(['a.b.c'])
        >>> print(tree_obj.search('a.b.c'))
        a.b.c

        트리 내에 존재하지 않는 노드라면 None을 반환. 
        """
        if self.isAbsPath(target_node):
            if target_node in self._adj_list: return target_node
            else: return None
        else:
            results = []
            for key in self._adj_list.keys():
                if self.splitAbsPath(key)[1] == target_node: results.append(key)
            if results == []: return None
            return sorted(results)
        
    def append(
            self,
            new_node: Node,
            parent: Node | AbsPath | None = None,
            raise_error: bool = False
        ) -> (None):
        """
        트리 내에 특정 부모 노드에 새로운 노드를 연결하여 추가한다. 
        새로 삽입할 노드 이름과 트리 내에 존재하는 노드들 중 몇몇의 이름과 
        중복되어도 그들의 절대경로가 겹치지만 않는다면 추가할 수 있다. 
        단, 같은 부모 노드를 가지는 같은 이름을 가지는 자식 노드들은 허용하지 않는다. 
        절대경로가 중복되는 노드는 삽입할 수 없다. 
        만약 현재 트리에 아무 노드가 없으면 parent 인자에 None이 아닌 노드가 
        입력된 경우, 해당 노드를 root 노드로 설정한 뒤, new_node는 그 root 노드의 
        자식 노드로 정한다. 단, 이 때 parent 인자는 반드시 절대경로가 아닌 노드 이름
        이어야 한다. 만약 절대경로인 경우, parent 인자는 무시하고 new_node를 
        root 노드로 지정한다. 
        만약 parent 인자가 None인 경우, new_node를 root 노드로 지정한다. 

        매개변수
        -------
        new_node: 삽입하고자 하는 새 노드 이름을 대입한다. 
        parent: new_node를 연결시킬 부모 노드 이름 또는 부모 노드의 
        절대경로. 노드 이름으로 대입 시 트리 내 같은 이름을 가지는 
        모든 노드에 새 노드들을 삽입한다. 반면, 절대경로로 입력 시, 
        그 절대경로에만 새 노드를 삽입한다. 

        예1)
        >>> tree_obj = PathTree()
        >>> data = ['a.b.c', 'a.d.c']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.append('d', 'c')
        >>> print(tree_obj.getTreeStructure())
        a
        ├ b
        │ └ c
        │   └ d
        └ d
          └ c
            └ d
        
        예2) 
        >>> tree_obj = PathTree()
        >>> data = ['a.b.c', 'a.d.c']
        >>> tree_obj.appendAll(data)
        >>> tree_obj.append('d', 'a.b.c')
        >>> print(tree_obj.getTreeStructure())
        a
        ├ b
        │ └ c
        │   └ d
        └ d
          └ c
        
        raise_error 여부에 따라 예외가 발생하거나 메서드 실행이 중단됨. 
        raise_error: 발생할 수 있는 각종 에러에 대해, raise_error 인자를 True로 설정 시,
        에러의 종류에 따라 예외를 발생시킨다. 예외 종류는 아래에 자세히 설명됨. 
        False로 설정 시 에러가 발생해도 이를 무시하고 메서드 실행을 중단한다. 

        발생할 수 있는 예외 종류
        -----
        ParentNoneError(): 트리에 이미 root 노드가 있는 상태에서 
        parent 인자에 None을 입력한 경우. 
        NodeNotFoundError: 지정한 부모 노드가 트리 내에 없을 경우.
        PathAlreadyExistsError(): 새로 삽입하고자 하는 새 노드의 절대경로가 이미 
        트리 내에 있을 경우. 
        """
        if self._root is None:
            if parent is None or self.isAbsPath(parent):
                self._root = new_node
                self._adj_list[new_node] = []
                self._node_number += 1
                return
            else:
                self._root = parent
                self._adj_list[parent] = [new_node]
                new_node_abs = self.combineNodesToAbsPath(parent, new_node)
                self._adj_list[new_node_abs] = []
                self._node_number += 2
                return
        elif parent is None:
            if self.always_raise_error or raise_error: raise ParentNoneError()
            else: return
        
        parents = self.search(parent)
        if parents is None:
            if self.always_raise_error or raise_error: raise NodeNotFoundError()
            else: return
        if type(parents) == str: parents = [parents]
        for p in parents:
            new_node_abs = self.combineNodesToAbsPath(p, new_node)
            if self.search(new_node_abs):
                if self.always_raise_error or raise_error: raise PathAlreadyExistsError()
                else: return
            try: self._adj_list[p].append(new_node)
            except KeyError: self._adj_list[p] = [new_node]
            else: self._adj_list[p].sort()
            self._adj_list[new_node_abs] = []
            self._node_number += 1

    def appendAbs(self, new_path: AbsPath, raise_error: bool = False) -> (None):
        """
        새로 삽입하고자 하는 절대경로를 대입하면 트리에 삽입해주는 메서드. 
        절대경로에 명시된 모든 노드들이 삽입된다. 
        단, 루트 노드가 트리에 존재할 때 삽입하고자 하는 노드의 절대경로는 
        루트 노드 이름부터 시작해야 한다. 
        삽입 예)
        >>> tree_obj = PathTree()
        >>> tree_obj.appendAbs('a.b.c.d')

        매개변수
        ------
        raise_error: 발생할 수 있는 각종 에러에 대해, raise_error 인자를 True로 설정 시,
        에러의 종류에 따라 예외를 발생시킨다. 예외 종류는 아래에 자세히 설명됨. 
        False로 설정 시 에러가 발생해도 이를 무시하고 메서드 실행을 중단한다. 

        발생할 수 있는 예외 종류
        -----
        PathAlreadyExistsError(): 새로 삽입하고자 하는 새 노드의 절대경로가 이미 
        트리 내에 있을 경우.
        RootNotUniqueError(): 새 노드의 절대경로에 적힌 루트 노드의 이름과 트리에 이미 존재하는 
        루트 노드 이름과 다를 경우. 
        """
        if self.search(new_path):
            if self.always_raise_error or raise_error: raise PathAlreadyExistsError()
            else: return
        path_split = new_path.split(self._delimiter)
        for i in range(len(path_split)):
            if i == 0:
                if self._root is None:
                    self._root = path_split[i]
                    self._adj_list[path_split[i]] = []
                    self._node_number += 1
                elif self._root != path_split[i]:
                    if self.always_raise_error or raise_error: raise RootNotUniqueError()
                    else: return
                continue
            path = self._delimiter.join(path_split[:i+1])
            if self.search(path): continue
            p_path, cur_node = self.splitAbsPath(path)
            try: self._adj_list[p_path].append(cur_node)
            except KeyError: self._adj_list[p_path] = [cur_node]
            else: self._adj_list[p_path].sort()
            if path not in self._adj_list: self._adj_list[path] = []
            self._node_number += 1

    def appendAll(self, structure: list[str], raise_error: bool = False) -> (None):
        """
        트리 구조를 나타낸 리스트를 입력하면 해당 구조 내 모든 노드들을 
        트리 구조에 맞게 트리에 추가함. 
        단, 리스트 안에 입력되는 모든 정보들은 트리 내 모든 leaf 노드들의 
        절대경로들로 구성해야함. 

        예)
        >>> tree_obj = PathTree()
        >>> structure = [
        ... 'root.살 것들.마트.당근',
        ... 'root.할 일.공부.과목.자료구조',
        ... 'root.할 일.공부.과목.프로그래밍 언어.파이썬',
        ... 'root.할 일.집안일.설거지.접시']
        >>> tree_obj.appendAll(structure)
        >>> print(tree_obj.getTreeStructure())
        root
        ├ 살 것들
        │ └ 마트
        │   └ 당근
        └ 할 일
          ├ 공부
          │ └ 과목
          │   ├ 자료구조
          │   └ 프로그래밍 언어
          │     └ 파이썬
          └ 집안일
            └ 설거지
              └ 접시

        트리가 존재하고, 특정 leaf 노드들에 새 노드들을 삽입하는 경우에도 
        새 노드의 절대경로로 입력해야함. 
        
        매개변수
        ------
        raise_error: 발생할 수 있는 각종 에러에 대해, raise_error 인자를 True로 설정 시,
        에러의 종류에 따라 예외를 발생시킨다. 예외 종류에 대한 정보는 
        append() 메서드의 독스트링 참조. 

        appendAll() 메서드에만 존재하는 예외 종류
        -----
        RootNotUniqueError(): structure 인자 속 정보에 root 노드가 두 개 이상 존재할 경우. 
        """
        # 빈 트리에 노드들을 삽입하는 경우와 
        # 이미 구성되어있는 트리에 노드들을 추가하는 경우로 나눠서 코드 작성. 

        def check_root() -> (Node | None):
            """
            root 노드가 단 한 개만 있는지 테스트하는 함수. 
            둘 이상 존재하면 None, 하나만 존재하면 그 root 노드를 반환. 
            (root 노드가 둘 이상 존재하면, 만약 트리에 이미 노드들이 존재하는 경우, 
            root 노드가 아니라 그저 기존 트리에 추가할 노드들이다.)
            """
            root = structure[0].split(self._delimiter)[0]
            for i in range(1, len(structure)):
                r = structure[i].split(self._delimiter)[0]
                if root != r: return None
            return root
        
        def insert_nodes(root: Node | None):
            if root and self._root is None:
                self.append(root, raise_error=raise_error)
            for data in structure:
                nodes = data.split(self._delimiter)
                for i in range(1, len(nodes)):
                    parent_abs = self._delimiter.join(nodes[:i])
                    current_node = nodes[i]
                    current_node_abs = self.combineNodesToAbsPath(parent_abs, current_node)
                    if self.search(current_node_abs) is None:
                        self.append(current_node, parent_abs, raise_error)

        root = check_root()
        if root is None and self._root is None:
            if self.always_raise_error or raise_error: raise RootNotUniqueError()
            else: return
        insert_nodes(root)

    def remove(
            self,
            target_node: Node | AbsPath,
            mode: RemoveMode = REMOVEONE
        ) -> (bool):
        """
        주어진 노드를 트리 내에서 삭제한다. 
        만약 삭제하고자 하는 노드에 자식 노드가 1개 이상 연결되어 있는 경우, 
        mode 매개변수에 REMOVEALL, REMOVEONE, DONTREMOVE 상수들 중 하나를 
        대입하여 처리한다.

        REMOVEALL: 삭제하고자 하는 노드와 함께 그 자식 노드들도 모두 삭제한다. 
        root 노드를 삭제하려는 경우, 트리 내 모든 노드들이 삭제된다. 

        REMOVEONE: 삭제하고자 하는 노드만 삭제하고, 그 하위 트리들은 모두 
        삭제한 노드의 부모 노드에 종속시킨다. 이 때, 삭제된 노드의 하위 노드를 
        삭제된 노드의 부모 노드에 종속시킬 때, 해당 부모 노드의 자식 노드와 그 
        이름이 겹치면 하나로 합친다. 

        예)
        >>> tree_obj = PathTree()
        >>> data = ['a.b.c.d.h', 'a.b.c.e.d.f']
        >>> tree_obj.appendAll(data)
        >>> print(tree_obj.getTreeStructure())
        a
        └ b
          └ c
            ├ d
            │ └ h
            └ e
              └ d
                └ f
        >>> tree_obj.remove('e')
        True
        >>> print(tree_obj.getTreeStructure())
        a
        └ b
          └ c
            └ d
              ├ f
              └ h
        
        해당 모드에서는 root 노드를 삭제할 수 없다. 

        DONTREMOVE: 만약 삭제하고자 하는 노드가 자식 노드를 가지면 해당 노드와 
        그 자식 노드 모두 삭제하지 않는다. 오로지 자식 노드가 없는 leaf 노드일 
        경우에만 삭제한다. 

        매개변수
        -----
        target_node: 삭제하고자 하는 노드의 이름 또는 절대경로를 입력한다. 
        만약 노드 이름으로 입력 시, 트리 내 같은 이름을 가지는 모든 노드들에 
        대해 삭제 작업이 실행된다. 절대경로로 입력한 경우 그 절대경로에 해당하는 
        노드만 삭제된다. 
        
        반환값
        -----
        True: 트리 내 해당 노드를 삭제한 경우. 
        False: 트리 내 해당 노드를 삭제하지 않은 경우.
        """
        if self.search(target_node) is None: return False
        if mode == REMOVEALL:
            queue = DynamicQueue()  # 노드의 절대경로를 원소로 함. 
            if not self.isAbsPath(target_node):
                if target_node == self._root:
                    self.clear()
                    return True
                first_nodes = self.search(target_node)
                for node in first_nodes: queue.enqueue(node)
            else:
                queue.enqueue(target_node)
            while not queue.isEmpty():
                node = queue.dequeue()
                children = self.getChildren(node)
                if children is not None:
                    for n in children:
                        queue.enqueue(self.combineNodesToAbsPath(node, n))
                p = self.getParent(node)
                try: self._adj_list[p].remove(self.basename(node))
                except KeyError: pass
                try: del self._adj_list[node]
                except KeyError: pass
                else: self._node_number -= 1
            return True
        elif mode == REMOVEONE:
            if target_node == self._root: return False
            if self.isAbsPath(target_node):
                t_nodes_abs = [target_node]
            else:
                t_nodes_abs: list[AbsPath] = self.search(target_node)
                # 예를 들어 삭제하고자 하는 노드로 'g'가 입력되었고, 
                # search('g') 결과 ['a.g', 'a.g.g']로 나온 경우, 
                # 상대적으로 더 하위 계층에 존재하는 노드('a.g.g')부터 삭제하도록 
                # 하기 위해 search() 결과를 절대경로 문자열의 길이가 가장 긴 순서대로 정렬. 
                temp_list: list[tuple[int, AbsPath]] = []
                for v in t_nodes_abs: heapq.heappush(temp_list, (-len(v), v))
                t_nodes_abs.clear()
                while temp_list:
                    t_nodes_abs.append(heapq.heappop(temp_list)[1])
            for t_node in t_nodes_abs:
                t_parent_abs: AbsPath = self.getParent(t_node)
                if t_parent_abs == self._root:
                    t_parent_children = self._adj_list[self._root].copy()
                else:
                    t_parent_children: list[Child] = self.getChildren(t_parent_abs)
                t_parent_children.remove(self.basename(t_node))
                t_children = self.getChildren(t_node)
                self._adj_list[t_parent_abs].remove(self.basename(t_node))
                self._adj_list[t_parent_abs].extend(self._adj_list[t_node])
                before_len = len(self._adj_list[t_parent_abs])
                self._adj_list[t_parent_abs] = list(set(self._adj_list[t_parent_abs]))
                after_len = len(self._adj_list[t_parent_abs])
                self._node_number -= before_len - after_len
                self._adj_list[t_parent_abs].sort()
                del self._adj_list[t_node]
                self._node_number -= 1
                # 삭제당한 노드의 자식 노드들이 삭제된 노드의 부모 노드에 편입될 때, 
                # 기존에 부모 노드에 같은 이름의 노드가 있을 경우, 그 노드로 해당 자식 노드의 
                # 자식 노드들을 편입시킨다. 자세한 예시는 이 메서드의 독스트링의 예시 참조. 
                for tc in t_children:
                    if tc in t_parent_children:
                        tpc_abs = self.combineNodesToAbsPath(t_parent_abs, tc)
                        tc_abs = self.combineNodesToAbsPath(t_node, tc)
                        self._adj_list[tpc_abs].extend(self._adj_list[tc_abs])
                        # 자식 노드들의 합병 이후 이름이 중복되는 노드 삭제.
                        before_len = len(self._adj_list[tpc_abs])
                        self._adj_list[tpc_abs] = list(set(self._adj_list[tpc_abs]))
                        after_len = len(self._adj_list[tpc_abs])
                        self._node_number -= before_len - after_len
                        self._adj_list[tpc_abs].sort()
                        del self._adj_list[tc_abs]
                # adj_list 변수의 key에 삭제한 노드가 경로 내에 포함되어 있는 경우, 
                # 해당 경로에서 해당 노드만 삭제한다. 
                t_node_split = t_node.split(self._delimiter)
                t_node_split_len = len(t_node_split)
                adjl = self._adj_list.copy()
                for key in adjl.keys():
                    key_split = key.split(self._delimiter)
                    if key_split[:t_node_split_len] == t_node_split:
                        temp_children = self._adj_list[key].copy()
                        del key_split[t_node_split_len-1]
                        new_key = self._delimiter.join(key_split)
                        self._adj_list[new_key] = temp_children
                        del self._adj_list[key]
            return True
        else:
            # DONTREMOVE
            if self.isAbsPath(target_node):
                t_nodes_abs = [target_node]
            else:
                t_nodes_abs: list[AbsPath] = self.search(target_node)
            if self._root in t_nodes_abs and self._node_number == 1:
                self.clear()
                return True
            is_removed = False
            for t_node in t_nodes_abs:
                if self.getChildren(t_node) == []:
                    t_parent = self.getParent(t_node)
                    self._adj_list[t_parent].remove(self.basename(t_node))
                    self._adj_list[t_parent].sort()
                    del self._adj_list[t_node]
                    self._node_number -= 1
                    is_removed = True
            return is_removed

    def replace(
            self,
            old_node: Node | AbsPath,
            new_node: Node, 
            raise_error: bool = False
        ) -> (bool):
        """
        기존 트리 내 특정 노드를 다른 노드로 바꾼다. 

        매개변수
        -------
        old_node: 바꾸고자 하는 트리 내 기존 노드의 이름 또는 절대경로. 
        노드 이름으로 입력 시 트리 내 같은 이름을 가지는 모든 노드들이 
        new_node 인자에 대입된 노드 이름으로 바뀐다. 절대경로로 입력 시 
        해당 절대경로에 해당하는 노드에 대해서만 이름이 바뀐다. 
        new_node: old_node를 새로 바꿀 노드. 
        raise_error: 해당 메서드 실행 중 발생할 수 있는 에러들에 대해 
        예외를 일으킬지 무시할지에 대한 변수. True 시 각 에러 종류에 따른 예외를 발생. 
        False 시 예외를 일으키지 않고 중단한다. 

        예외 종류
        --------
        NodeNotFoundError: old_node가 트리 내에 존재하지 않을 경우. 
        PathAlreadyExistsError: 새로 바꿀 노드의 절대경로와 똑같은 경로를 가지는 노드가 
        이미 트리 내에 존재할 경우. 
        
        반환값
        -----
        True: 성공적으로 노드를 바꿨을 경우. 
        False: 노드를 바꾸지 못한 경우. 
        """
        old_nodes_abs = self.search(old_node)
        if old_nodes_abs is None:
            if self.always_raise_error or raise_error: raise NodeNotFoundError()
            else: return False
        if type(old_nodes_abs) == str: old_nodes_abs = [old_nodes_abs]
        for o_node in old_nodes_abs:
            o_node_dir = self.dirname(o_node)
            new_node_abs = self.combineNodesToAbsPath(o_node_dir, new_node)
            if self.search(new_node_abs):
                if self.always_raise_error or raise_error: raise PathAlreadyExistsError()
                else: return False
            self._adj_list[new_node_abs] = self._adj_list[o_node]
            o_parent = self.getParent(o_node)
            if o_parent == ['']: o_parent = self._root
            self._adj_list[o_parent].remove(self.basename(o_node))
            self._adj_list[o_parent].append(new_node)
            self._adj_list[o_parent].sort()
            del self._adj_list[o_node]
        return True

    def getTreeStructure(self) -> (str):
        if self._root is None: return "<빈 트리>"

        extension = "│"
        sub_dir_line = "└"
        sub_and_extension = "├"
        whitespace = " "
        one_tab_length = 2

        struct_str = []
        stack = [(0, self._root)]
        
        # depth가 같은 두 노드 a, b 노드가 있다고 가정하고, 두 노드에
        # 하위 트리가 존재할 경우, a 노드의 하위 트리가 구성될 동안 각 라인 
        # 앞에는 b 노드가 a 노드와 이어지는 것을 표현하기 위한 문자 "│"을 
        # 계속 하위 노드들의 맨 앞에 출력해야한다. 이를 위해선 a 노드의 하위 
        # 트리들이 한 줄씩 구성될 떄동안 b 노드가 아직 남아있음을 기록해야 한다.
        # 연결선 "│"으로 같은 깊이의 노드들을 연결하기 위해 시작 노드와 끝 노드
        # 를 기록하는 변수. 
        branch_stack = []

        while stack:
            depth, path = stack.pop()
            node = self.basename(path)
            line = ""
            for iter_depth in range(depth+1):
                if iter_depth == depth:
                    line += f"{node}"
                elif iter_depth == (depth-1):
                    try:
                        branch_stack.remove((depth, path))
                    except ValueError:
                        if not branch_stack: line += sub_dir_line
                        elif iter_depth in dict(branch_stack): line += sub_and_extension
                    else:
                        if (iter_depth+1) in dict(branch_stack): line += sub_and_extension
                        else: line += sub_dir_line
                    line += whitespace
                else:
                    if (iter_depth+1) in dict(branch_stack): line += extension + (whitespace*(one_tab_length-1))
                    else: line += whitespace * one_tab_length
            
            struct_str.append(line)
            if path == self._root: children = self._adj_list[self._root]
            else: children = self.getChildren(path)
            if children == [] or children is None: continue
            children.sort(reverse=True)
            for c in children:
                c = self.combineNodesToAbsPath(path, c)
                stack.append((depth+1, c))
                branch_stack.append((depth+1, c))
        return '\n'.join(struct_str)

    def getAllLeafAbs(
            self, 
            how_to_sort: SortMode = ALPHABET, 
            ascending: bool = True
        ) -> (list[AbsPath]):
        """
        트리 내 모든 leaf 노드들의 절대경로들을 리스트로 모아 반환한다. 
        how_to_sort 인자의 값에 따라 절대경로 리스트의 정렬 방식이 달라진다. 

        매개변수
        -------
        how_to_sort: leaf 노드들의 절대경로들을 리스트에 저장하고 반환할 때 
        리스트의 정렬방식. 
            1. ALPHABET: 알파벳, 가나다, 숫자 오름 또는 내림차순으로 정렬.
            2. LENGTH: 절대경로의 길이가 길거나 짧은 순대로 정렬.
        ascending: True 시 오름차순, False 시 내림차순으로 정렬.
        """
        if self._root is None: return []
        leaf_nodes = []
        for k, v_list in self._adj_list.items():
            if v_list == []: leaf_nodes.append(k)
        if how_to_sort == ALPHABET:
            if ascending: leaf_nodes.sort()
            else: leaf_nodes.sort(reverse=True)
        elif how_to_sort == LENGTH:
            temp_list = []
            if ascending:
                for element in leaf_nodes:
                    heapq.heappush(temp_list, (len(element), element))
            else:
                for element in leaf_nodes:
                    heapq.heappush(temp_list, (-len(element), element))
            leaf_nodes.clear()
            while temp_list:
                leaf_nodes.append(heapq.heappop(temp_list)[1])
        return leaf_nodes


if __name__ == '__main__':
    import doctest
    doctest.testmod()
