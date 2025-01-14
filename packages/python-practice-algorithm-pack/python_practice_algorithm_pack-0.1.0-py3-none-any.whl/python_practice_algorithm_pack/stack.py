from typing import Generic, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self, initial_elements: list[T] | None = None) -> None:
        if initial_elements is None:
            initial_elements = []
        self.elements: list[T] = initial_elements.copy()

    def pop(self) -> T:
        if len(self.elements) == 0:
            raise ValueError("The stack is empty and there's not an element to pop.")
        return self.elements.pop(-1)

    def push(self, item: T) -> None:
        self.elements.append(item)

    def peek(self) -> T:
        if len(self.elements) == 0:
            raise ValueError("The stack is empty and there's not an element to peek.")
        return self.elements[-1]

    def size(self) -> int:
        return len(self.elements)
