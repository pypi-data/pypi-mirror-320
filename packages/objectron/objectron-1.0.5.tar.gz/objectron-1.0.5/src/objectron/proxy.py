"""
Proxy implementation for the Objectron framework.
Provides specialized proxy classes for different Python types, enabling:
- Transparent attribute access and modification
- Method call interception and monitoring
- Path-based object traversal
- Reference tracking across object graphs
"""
from ast import AST, unparse
from contextlib import suppress
from functools import wraps
from gc import get_referrers
from inspect import isframe, stack
from types import FrameType, FunctionType
from typing import (
    Any,
    Callable,
    Generic,
    List,
    Mapping,
    Optional,
    TypeVar,
)

from tree_interval import Future, LeafStyle
from tree_interval.core.future import FrameAnalyzer
from tree_interval.core.interval_core import Statement

T = TypeVar("T")
DEBUG = False


def _print(*args):
    if DEBUG:
        print(*args)


class ReferenceObjectron:
    """Forward declaration for type hinting."""

    def transform(self, value: Any) -> Any:
        pass  # Placeholder for actual implementation


class DynamicProxy(Generic[T], ReferenceObjectron):
    """Base proxy class providing dynamic object access and monitoring.
    Implements a transparent wrapper around Python objects that enables:
    - Dynamic attribute creation and tracking
    - Method call interception
    - Path-based access patterns
    - Reference management
    Example:
        proxy = DynamicProxy({"a": 1}, objectron)
        proxy.b.c = 2           # Dynamic attribute creation
        proxy["a.b.c"] = 3      # Path-based access
    """
    _registry = {}  # Global registry of proxied objects

    @staticmethod
    def _get_func_from_frame(frame=None):
        _frame = stack()[2].frame if frame is None else frame
        if isframe(_frame):
            for v in get_referrers(_frame.f_code):
                if isinstance(v, FunctionType):
                    return v

    @staticmethod
    def _get_class_from_func(func):
        if not callable(func):
            return
        _cls_qual_name, _func_name = (func.__qualname__.rsplit(
            ".", 1) if "." in func.__qualname__ else (None, func.__name__))
        assert _func_name == func.__name__
        if not isinstance(func, FunctionType):
            _self = getattr(func, "__self__", None)
            for v in (_self, type(_self)):
                if isinstance(v, type) and v.__qualname__ == _cls_qual_name:
                    return v
        _visited_ids = set()
        _items_to_check: list = [func]
        while len(_items_to_check) > 0:
            _obj = _items_to_check.pop(0)
            _obj_id = id(_obj)
            if _obj_id in _visited_ids:
                continue
            _visited_ids.add(_obj_id)
            for v in get_referrers(_obj):
                if isinstance(v, type) and v.__qualname__ == _cls_qual_name:
                    return v
                if hasattr(v, "__get__") or isinstance(v, Mapping):
                    _items_to_check.append(v)

    def __new__(cls, obj: T,
                objectron: ReferenceObjectron) -> "DynamicProxy[T]":
        """Create or retrieve existing proxy for an object.
        Ensures each object has only one proxy instance to
        maintain consistency.
        """
        obj_id = id(obj)
        if obj_id in cls._registry:
            proxy = cls._registry[obj_id]
            object.__setattr__(proxy, "_objectron", objectron)
            return proxy
        instance = super(DynamicProxy, cls).__new__(cls)
        cls._registry[obj_id] = instance
        return instance

    def __init__(self, obj: T, objectron: ReferenceObjectron) -> None:
        # Use __dict__ directly to avoid recursion
        if "_initialized" in self.__dict__:
            return
        object.__setattr__(self, "_obj", obj)
        object.__setattr__(self, "_objectron", objectron)
        object.__setattr__(self, "_attributes", {})  # For dynamic attributes
        object.__setattr__(self, "_initialized", True)

    def __getattr__(self, name: str) -> Any:
        # Handle dynamic attributes first
        if name in self._attributes:
            return self._attributes[name]
        _cls = self._get_class_from_func(
            self._get_func_from_frame(stack()[1].frame))
        if _cls and type(self) in _cls.mro():
            return object.__getattribute__(self._obj, name)

        def new_return():
            if isinstance(self._obj, dict) and name in self._obj:
                return self._objectron.transform(self._obj[name])
            new_dict = self._objectron.transform({})
            if isinstance(self._obj, dict):
                self._obj[name] = new_dict
            else:
                self._attributes[name] = new_dict
            return new_dict

        try:
            return object.__getattribute__(self._obj, name)
        except Exception:
            with suppress(Exception):
                return self[name]
            return Future(
                name,
                frame=1,
                instance=None,
                new_return=new_return,
            )

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            # Internal attributes
            object.__setattr__(self, name, value)
        elif isinstance(self._obj, dict):
            self._obj[name] = self._objectron.transform(value)
        else:
            # For immutable types, store in _attributes
            self._attributes[name] = self._objectron.transform(value)

    def __delattr__(self, name: str, /) -> None:
        if name in self._obj:
            del self._obj[name]
            return
        return super().__delattr__(name)

    def __getitem__(self, key: Any) -> Any:
        _stack = stack()
        caller = _stack[1].frame
        current_node = Future.current_node(caller)
        create_frame = caller
        for v in _stack[1:]:
            frame = v.frame
            _cls = self._get_class_from_func(self._get_func_from_frame(frame))
            if not _cls or type(self) not in _cls.mro():
                create_frame = frame
                break

        if isinstance(key, str) and self._is_path_string(key):
            parent, key_immutable = self._resolve_path(
                self._parse_path(key),
                create=Future.is_set(create_frame),
                frame=caller,
                statement=current_node.statement if current_node else None)
            return parent[key_immutable] if key_immutable else parent
        # Regular item access
        return self._objectron.transform(self._obj[key])

    def __setitem__(self, key: Any, value: Any) -> None:
        if isinstance(key, str) and self._is_path_string(key):
            path_steps = self._parse_path(key)
            try:
                parent, key_immutable = self._resolve_path(path_steps[:-1])
                if key_immutable:
                    parent.update({
                        key_immutable:
                        object.__getattribute__(
                            parent, key_immutable)[:path_steps[-1]] + value +
                        object.__getattribute__(
                            parent, key_immutable)[path_steps[-1] + 1:]
                    })
                    return
                last_step = path_steps.pop(-1)
                for v in path_steps:
                    if isinstance(v, str) and not hasattr(self, v):
                        parent_new = self._objectron.transform({})
                        parent[v] = parent_new
                        parent = parent_new

                if isinstance(parent, DictProxy):
                    parent[last_step] = self._objectron.transform(value)
                elif isinstance(parent, DynamicProxy) and isinstance(
                        parent._obj, (
                            list,
                            str,
                        )):
                    if isinstance(last_step, int):
                        parent = parent[:last_step] + (
                            value if isinstance(value, DynamicProxy) else
                            self._objectron.transform(value)
                        ) + parent[last_step + 1:]
                    else:
                        raise KeyError(f"Invalid list index: {last_step}")
                else:
                    raise TypeError(
                        "Unsupported parent type for setting value.")
            except Exception as e:
                # Optionally handle or log the exception
                raise e
            return
        # Regular item access
        if isinstance(self._obj, dict):
            print(value, isinstance(value, IntProxy))
            self._obj[key] = value if isinstance(
                value, DynamicProxy) else self._objectron.transform(value)
        elif isinstance(key, int):
            if isinstance(self._obj, list):
                self._obj = self._obj[:key] + [
                    value if isinstance(value, DynamicProxy) else
                    self._objectron.transform(value)
                ] + self._obj[key + 1:]
            elif isinstance(self._obj, (str, )):
                self._obj = self._obj[:key] + (
                    value if isinstance(value, DynamicProxy) else
                    self._objectron.transform(value)) + self._obj[key + 1:]

    def _is_path_string(self, path: str) -> bool:
        # Simple heuristic: contains dots or brackets
        return "." in path or "[" in path

    def _parse_path(self, path: str) -> List[Any]:
        """
        Parses a complex path string into a list of steps.
        Example: "users[0].details.age" or "users.0.details.age"
                 -> ['users', 0, 'details', 'age']
        """
        tokens = []
        current = ''
        i = 0
        while i < len(path):
            if path[i] == '[':
                if current:
                    tokens.append(current)
                    current = ''
                i += 1
                num = ''
                while i < len(path) and path[i].isdigit():
                    num += path[i]
                    i += 1
                if num:
                    tokens.append(int(num))
                while i < len(path) and path[i] != ']':
                    i += 1
                i += 1
            elif path[i] == '.':
                if current:
                    if current.isdigit():
                        tokens.append(int(current))
                    else:
                        tokens.append(current)
                    current = ''
                i += 1
            else:
                current += path[i]
                i += 1
        if current:
            if current.isdigit():
                tokens.append(int(current))
            else:
                tokens.append(current)
        return tokens

    def _resolve_path(self,
                      steps: List[Any],
                      create: bool = False,
                      statement: Optional[Statement] = None,
                      frame: Optional[FrameType] = None,
                      _depth: int = 0) -> Any:
        """
        Traverses the proxy based on the list of steps with
        recursion protection.
        If 'create' is True, it will create proxies along the path if needed.
        """
        if _depth > 100:  # Protect against infinite recursion
            raise RecursionError("Maximum path resolution depth exceeded")
        current = self
        """
        Traverses the proxy based on the list of steps.
        If 'create' is True, it will create proxies along the path if needed.
        """
        current = self
        cumulative = ""
        key_immutable = None
        for k, step in enumerate(steps):
            if isinstance(step, str):
                if isinstance(current, DictProxy):
                    if step not in current._obj:
                        if create:
                            current._obj[step] = {}
                        elif statement:
                            with suppress(Exception):
                                statement_self = statement.self
                                self_before = statement_self[:statement_self.
                                                             index(step, k)]
                                statement.before += self_before
                                statement.self = step
                                statement.after = statement_self.removeprefix(
                                    self_before + step) + statement.after
                            Future.raise_error(
                                Future.get_error(step, frame, statement))
                    if getattr(current, step, None) and not isinstance(
                            getattr(current, step), str):
                        current = current[step]
                    elif create:
                        key_immutable = step
                else:
                    current = getattr(current, step)
            elif isinstance(step, int):
                if isinstance(current, DynamicProxy) and isinstance(
                        current._obj, list):
                    if step >= len(current._obj):
                        if create:
                            # Extend the list with None to
                            # accommodate the index
                            while len(current._obj) <= step:
                                current._obj.append(None)
                        else:
                            raise IndexError(
                                f"List index out of range: {step}")
                    current = current[step]
                else:
                    raise TypeError(
                        "Cannot index into object of type",
                        f"{type(current._obj).__name__}",
                    )
            else:
                raise TypeError(f"Invalid step type: {type(step).__name__}")
            cumulative += str(step)
        return current, key_immutable

    def _wrap_method(self, method: Callable, name: str) -> Callable:

        @wraps(method)
        def wrapped(*args, **kwargs):
            _print(f"[ReferenceTracker] Calling method: {name}")
            result = method(*args, **kwargs)
            _print(f"[ReferenceTracker] Method {name} called successfully.")
            return self._objectron.transform(result)

        return wrapped

    def get_original(self) -> object:
        """Retrieve the original object."""
        return self._obj

    def __repr__(self) -> str:
        return object.__repr__(self._obj)

    def __str__(self) -> str:
        return object.__str__(self._obj)

    def __len__(self) -> int:
        return len(self._obj)


class DictProxy(DynamicProxy[dict]):
    """
    A specialized proxy class for dictionaries that allows
    attribute-style access.
    For example, {"a": {"b": {"c": 1}}} can be accessed as a.b.c
    """

    def __getattr__(self, name: str) -> Any:
        if name in (
                "get",
                "keys",
                "values",
                "items",
                "update",
                "clear",
                "pop",
                "popitem",
                "setdefault",
        ):
            return getattr(self._obj, name)
        elif name in self._obj:
            return self._objectron.transform(self._obj[name])
        if DEBUG:
            print(f'\n{"#" * 50}')
            print(f"attribute name: {name}")
            analyzer = FrameAnalyzer(1)
            current_node = analyzer.find_current_node()
            tree = analyzer.build_tree()
            if current_node and tree:
                current_node_ast_node = getattr(current_node, "ast_node", None)
                print("Current attribute node: " +
                      (unparse(current_node_ast_node) if isinstance(
                          current_node_ast_node, AST) else "None"))
                top_statement = current_node.top_statement
                top_statement_ast_node = getattr(top_statement, "ast_node",
                                                 None)
                print("Top attribute node: " +
                      (unparse(top_statement_ast_node) if isinstance(
                          top_statement_ast_node, AST) else "None"))
                is_set = top_statement.is_set if top_statement else False
                print(f"Is set: {is_set}")
                next_attribute = current_node.next_attribute
                next_attribute_ast_node = getattr(next_attribute, "ast_node",
                                                  None)
                print("Next attribute node: " +
                      (unparse(next_attribute_ast_node) if isinstance(
                          next_attribute_ast_node, AST) else "None"))
                previous_attribute_ast_node = getattr(
                    current_node.previous_attribute, "ast_node", None)
                print("Previous attribute node: " +
                      (unparse(previous_attribute_ast_node) if isinstance(
                          previous_attribute_ast_node, AST) else "None"))
                # Show statement with different marker styles
                print("\nDefault markers:", current_node.statement)
                flat_nodes = tree.flatten()
                for node in flat_nodes:
                    if node.match(current_node):
                        node.style = LeafStyle(color="#ff0000", bold=True)
                    elif node.match(top_statement):
                        node.style = LeafStyle(color="#00ff00", bold=False)
                    elif node.match(next_attribute):
                        node.style = LeafStyle(color="#0000ff", bold=False)
                    else:
                        node.style = LeafStyle(color="#cccccc", bold=False)
                tree.visualize()

        def new_return():
            if name not in self._obj:
                self._obj[name] = {}
            return self._objectron.transform(self._obj[name])

        return Future(
            name,
            frame=1,
            instance=None,
            new_return=new_return,
        )

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            # Internal attributes
            object.__setattr__(self, name, value)
        else:
            self._obj[name] = self._objectron.transform(value)

    def __delattr__(self, name: str, /) -> None:
        if name in self._obj:
            del self._obj[name]
            return
        return super().__delattr__(name)

    def __init__(self, obj: object, objectron: ReferenceObjectron) -> None:
        # Use __dict__ directly to avoid recursion
        if "_initialized" in self.__dict__:
            return
        object.__setattr__(self, "_obj", obj)
        object.__setattr__(self, "_objectron", objectron)
        object.__setattr__(self, "_attributes", {})  # For dynamic attributes
        object.__setattr__(self, "_initialized", True)


class IntProxy(int, DynamicProxy[int]):

    def __new__(cls, value: int, objectron: ReferenceObjectron):
        obj = int.__new__(cls, value)
        DynamicProxy.__init__(obj, obj, objectron)
        return obj

    def __add__(self, other):
        result = super().__add__(other)
        _print(f"[ReferenceTracker] Adding {self} + {other}")
        return self._objectron.transform(result)

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        result = super().__sub__(other)
        _print(f"[ReferenceTracker] Subtracting {self} - {other}")
        return self._objectron.transform(result)

    def __isub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        result = super().__mul__(other)
        _print(f"[ReferenceTracker] Multiplying {self} * {other}")
        return self._objectron.transform(result)

    def __imul__(self, other):
        return self.__mul__(other)

    def get_original(self) -> int:
        return int(self)


class FloatProxy(float, DynamicProxy[float]):

    def __new__(cls, value: float, objectron: ReferenceObjectron):
        obj = float.__new__(cls, value)
        DynamicProxy.__init__(obj, obj, objectron)
        return obj

    def __add__(self, other):
        result = super().__add__(other)
        _print(f"[ReferenceTracker] Adding {self} + {other}")
        return self._objectron.transform(result)

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        result = super().__sub__(other)
        _print(f"[ReferenceTracker] Subtracting {self} - {other}")
        return self._objectron.transform(result)

    def __isub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        result = super().__mul__(other)
        _print(f"[ReferenceTracker] Multiplying {self} * {other}")
        return self._objectron.transform(result)

    def __imul__(self, other):
        return self.__mul__(other)

    def get_original(self) -> float:
        return float(self)


class StrProxy(str, DynamicProxy[str]):

    def __new__(cls, value: str, objectron: ReferenceObjectron):
        obj = str.__new__(cls, value)
        DynamicProxy.__init__(obj, obj, objectron)
        return obj

    def __add__(self, other):
        result = super().__add__(other)
        _print(f"[ReferenceTracker] Adding '{self}' + '{other}'")
        return self._objectron.transform(result)

    def __iadd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        result = super().__mul__(other)
        _print(f"[ReferenceTracker] Multiplying '{self}' * {other}")
        return self._objectron.transform(result)

    def __imul__(self, other):
        return self.__mul__(other)

    def get_original(self) -> str:
        return str(self)


class TupleProxy(tuple, DynamicProxy[tuple]):

    def __new__(cls, value: tuple, objectron: ReferenceObjectron):
        obj = tuple.__new__(cls, value)
        DynamicProxy.__init__(obj, obj, objectron)
        return obj

    def __add__(self, other):
        result = super().__add__(other)
        _print(f"[ReferenceTracker] Adding {self} + {other}")
        return self._objectron.transform(result)

    def __iadd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        result = super().__mul__(other)
        _print(f"[ReferenceTracker] Multiplying {self} * {other}")
        return self._objectron.transform(result)

    def __imul__(self, other):
        return self.__mul__(other)

    def get_original(self) -> tuple:
        return tuple(self)


class FrozensetProxy(frozenset, DynamicProxy[frozenset]):

    def __new__(cls, value: frozenset, objectron: ReferenceObjectron):
        obj = frozenset.__new__(cls, value)
        DynamicProxy.__init__(obj, obj, objectron)
        return obj

    def __or__(self, other):
        result = super().__or__(other)
        _print(f"[ReferenceTracker] Union {self} | {other}")
        return self._objectron.transform(result)

    def __ior__(self, other):
        return self.__or__(other)

    def __and__(self, other):
        result = super().__and__(other)
        _print(f"[ReferenceTracker] Intersection {self} & {other}")
        return self._objectron.transform(result)

    def __iand__(self, other):
        return self.__and__(other)

    def get_original(self) -> frozenset:
        return frozenset(self)


class ComplexProxy(complex, DynamicProxy[complex]):

    def __new__(cls, value: complex, objectron: ReferenceObjectron):
        obj = complex.__new__(cls, value)
        DynamicProxy.__init__(obj, obj, objectron)
        return obj

    def __add__(self, other):
        result = super().__add__(other)
        _print(f"[ReferenceTracker] Adding {self} + {other}")
        return self._objectron.transform(result)

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        result = super().__sub__(other)
        _print(f"[ReferenceTracker] Subtracting {self} - {other}")
        return self._objectron.transform(result)

    def __isub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        result = super().__mul__(other)
        _print(f"[ReferenceTracker] Multiplying {self} * {other}")
        return self._objectron.transform(result)

    def __imul__(self, other):
        return self.__mul__(other)

    def get_original(self) -> complex:
        return complex(self)


class ListProxy(DynamicProxy[list]):

    def __init__(self, value: list, objectron: ReferenceObjectron):
        super().__init__(list(value), objectron)

    def __getitem__(self, key: int) -> Any:
        if isinstance(key, slice):
            return self._obj[key]
        return self._objectron.transform(self._obj[key])

    def __eq__(self, other):
        if isinstance(other, list):
            return self._obj == other
        return super().__eq__(other)

    def __setitem__(self, key: int, value: Any) -> None:
        self._obj[key] = value

    def __delitem__(self, key: int) -> None:
        del self._obj[key]

    def __contains__(self, item: Any) -> bool:
        return item in self._obj

    def __len__(self) -> int:
        return len(self._obj)

    def append(self, item: Any) -> None:
        self._obj.append(item)

    def extend(self, items: list) -> None:
        self._obj.extend(items)

    def pop(self, index: int = -1) -> Any:
        return self._objectron.transform(self._obj.pop(index))
