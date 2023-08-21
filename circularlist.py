class Node:
    def __init__(self, value):
        self.value: tuple[int, int] = value
        self.next: Node

    def __repr__(self) -> str:
        return f"({self.value[0]},{self.value[1]})"

class CircularList:
    """
    Reverse circular linked list. Self.tail = snake's tail (but actually list's head).
    Self.head = snake head (but list's tail). self.tail → node → ... → node → self.head.
    Finally self.head → self.tail making it circular.
    """
    def __init__(self, value) -> None:
        self.tail = self.head = Node(value)
        self.tail.next = self.tail

    def __repr__(self) -> str:
        node = self.tail
        return_string = str(node)
        while node is not self.head:
            node = node.next
            return_string += " → " + str(node)
        return return_string

    def shift(self, value) -> None:
        self.head = self.tail
        self.tail.value = value
        self.tail = self.tail.next

    def insert(self, value) -> None:
        tail_copy = Node(self.tail.value)
        tail_copy.next = self.tail.next
        self.tail.next = tail_copy
        self.shift(value)

    def get_tail(self):
        return self.tail.value

    def get_head(self):
        return self.head.value
