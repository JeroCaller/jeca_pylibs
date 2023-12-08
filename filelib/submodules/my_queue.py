from typing import Any


class StaticQueue():
    def __init__(
            self, 
            limit_size: int = 10, 
            msg_on_off: bool = True
        ):
        """
        큐의 왼쪽에서 데이터 삽입, 오른쪽에서 데이터 추출 가능한 구조.

        매개변수
        ------
        limit_size: queue가 담을 수 있는 총 아이템 수 지정.
        msg_on_off: enqueue, dequeue에서 발생할 수 있는 메시지를 출력할 것인지에 대한 변수. 
        True -> 메시지가 출력된다. False -> 메시지가 출력되지 않는다. 
        """
        self._en_stack = []
        self._de_stack = []
        self.limit_size = limit_size
        self.msg_mode: bool = msg_on_off

    def getMsgMode(self) -> (bool): return self.msg_mode
    def setMsgMode(self, on_off: bool) -> (None): self.msg_mode = on_off

    def _transfer(self):
        while self._en_stack:
            self._de_stack.append(self._en_stack.pop())

    def isEmpty(self) -> (bool):
        return self._en_stack == [] and self._de_stack == []
    
    def getCurrentSize(self) -> (int):
        return len(self._en_stack) + len(self._de_stack)
    
    def enqueue(self, item):
        cur_size = self.getCurrentSize()
        if cur_size != self.limit_size:
            self._en_stack.append(item)
        else:
            if self.msg_mode:
                print("큐에 데이터가 꽉 차서 더 이상 삽입할 수 없습니다.")
            else:
                return

    def dequeue(self) -> (Any | None):
        if not self._de_stack:
            self._transfer()
        try:
            return self._de_stack.pop()
        except IndexError:
            if self.msg_mode:
                print("큐가 비어서 출력할 데이터가 없습니다.")
            else:
                return
        
    def seek_peek(self) -> (Any | None):
        if not self._de_stack:
            if self._en_stack:
                return self._en_stack[0]
            else:
                return
        return self._de_stack[-1]
    
    def clear(self) -> (None):
        """
        큐를 비운다.
        """
        self._en_stack.clear()
        self._de_stack.clear()
    
    def __repr__(self):
        if self._en_stack == [] and self._de_stack == []:
            return repr([])
        
        self.total_queue = []  # self.en_queue + self.de_queue
        temp_stack = []
        if self._en_stack:
            temp_stack = self._en_stack.copy()
            while temp_stack:
                self.total_queue.append(temp_stack.pop())
        if self._de_stack:
            self.total_queue.extend(self._de_stack)
        return repr(self.total_queue)
    

class DynamicQueue(StaticQueue):
    def __init__(self, msg_on_off: bool = True) -> (None):
        """
        크기 제한없이 동적으로 데이터를 enqueue및 dequeue할 수 있는 동적 큐.

        매개변수
        ------
        msg_on_off: enqueue, dequeue에서 발생할 수 있는 메시지를 출력할 것인지에 대한 변수. 
        True -> 메시지가 출력된다. False -> 메시지가 출력되지 않는다. 
        """
        self._en_stack = []
        self._de_stack = []
        self.msg_mode: bool = msg_on_off

    def enqueue(self, item: any) -> (None):
        self._en_stack.append(item)


def test_static_queue():
    q = StaticQueue()
    data = ['a', 'b', 'c', 'd']
    print("현재 큐는 비어있나요? ", q.isEmpty())
    print("큐에 데이터 삽입.")
    for item in data:
        q.enqueue(item)
    print("현재 큐는 비어있나요? ", q.isEmpty())
    print("최신 데이터: ", q.dequeue())
    print("현재 큐에서 제일 먼저 출력될 아이템: ", q.seek_peek())
    print("현재 큐에 존재하는 총 아이템 개수: ", q.getCurrentSize())
    print(q)
        

if __name__ == '__main__':
    test_static_queue()
