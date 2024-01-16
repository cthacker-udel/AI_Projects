from __future__ import annotations
from typing import Optional, List, Any, TypeVar

from enum import Enum


class GraphNodeType(Enum):
    MIN = 0,
    MAX = 1,
    EXPECTIMAX = 2,
    TERMINAL = 4


class GraphNode:
    def __init__(self: GraphNode, value: int = -1) -> None:
        self.value = value
        self.spec: GraphNodeType = GraphNodeType.TERMINAL
        self.children: List[GraphNode] = []
        self.parent: Optional[GraphNode] = None

    def add_child(self: GraphNode, child: GraphNode) -> GraphNode:
        self.children.append(child)
        return self

    def add_children(self: GraphNode, children: List[GraphNode]) -> GraphNode:
        for each_child in children:
            self.children.append(each_child)
        return self

    def get_value(self: GraphNode) -> int:
        if self.spec == GraphNodeType.TERMINAL:
            return self.value
        if self.spec == GraphNodeType.MIN:
            return min(x.get_value() for x in self.children)
        if self.spec == GraphNodeType.MAX:
            return max(x.get_value() for x in self.children)
        if self.spec == GraphNodeType.EXPECTIMAX:
            return sum(x.get_value() for x in self.children) // len(self.children)
        return 0

    def clone(self: GraphNode) -> GraphNode:
        cloned = GraphNode(self.value)
        cloned.spec = self.spec
        cloned.children = [x.clone() for x in self.children]
        cloned.parent = self.parent.clone() if self.parent is not None else None
        return cloned
