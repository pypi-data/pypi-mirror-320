"""
The module provides the `Future` class which facilitates dynamic attribute
creation and access within nested object structures. It includes the ability to
analyze the call stack and current execution frame, enabling context-aware
handling for setting or getting operations. The class raises descriptive errors
for invalid accesses and manages nested attribute chains accordingly.
"""

import sys
from inspect import isframe, stack
from textwrap import indent
from types import FrameType
from typing import Any, Optional, Union

from tree_interval.core.interval_core import Position

from .frame_analyzer import FrameAnalyzer


class Future:
    """
    Handles dynamic attribute creation and access in nested object structures.
    This class provides context-aware attribute handling by analyzing
    the call stack and current execution frame to determine whether an
    attribute access is part of a setting operation
    (creating new attributes) or a getting operation (which may
    raise appropriate errors).
    Example:
        class Nested:
            def __getattr__(self, name):
                return Future(name, frame=1, instance=self)
        obj = Nested()
        obj.a.b.c = 42  # Creates nested structure
        print(obj.a.b.c)  # Prints 42
        print(obj.x.y)  # Raises AttributeError with context
    """

    @classmethod
    def is_set(cls, frame: Optional[Union[int, FrameType]] = None) -> bool:
        """Determine if the current operation is a setting operation.

        Analyzes the execution frame to check if the current attribute
        access is part of an assignment operation.

        Args:
            frame: Optional frame object for context analysis. If None,
                   uses current.

        Returns:
            bool: True if current operation is a setting operation,
                  False otherwise.
        """
        frame = cls.get_frame(frame)
        if isframe(frame):
            current_node = cls.current_node(frame)
            if current_node:
                top_statement = current_node.top_statement
                return (getattr(top_statement, "is_set", False) and Position(
                    getattr(getattr(top_statement, "ast_node", None),
                            "targets", [None])[0]).start
                        == current_node.position.start)
        return False

    @staticmethod
    def current_node(
            frame: Optional[Union[int, FrameType]] = None) -> Optional[Any]:
        """Get the current AST node from the execution frame.

        Uses FrameAnalyzer to locate the current node in the execution context.

        Args:
            frame: Optional frame object to analyze. If None, uses
                   current frame.

        Returns:
            Optional[Any]: Current AST node if found, None otherwise.
        """
        return FrameAnalyzer(frame).find_current_node()

    @staticmethod
    def get_frame(
            frame: Optional[Union[int,
                                  FrameType]] = None) -> Optional[FrameType]:
        """Get the execution frame for context analysis.

        Resolves the appropriate frame object based on the input type.
        If an integer is provided, it's used as a stack offset.

        Args:
            frame: Frame object, stack level (int), or None for current frame.

        Returns:
            Optional[FrameType]: Resolved frame object or None if not found.
        """
        return frame if isframe(frame) else stack()[(
            frame + 2) if isinstance(frame, int) else 3].frame

    def __new__(
        cls,
        name: str,
        instance: Optional[object] = None,
        frame: Optional[Union[int, FrameType]] = None,
        new_return: Optional[Any] = None,
    ) -> Any:
        """Dynamic attribute creation and access handler.
        This method implements the core logic for dynamic attribute
        handling by:
        1. Analyzing call stack context to determine operation type
        2. Creating new attributes in assignment context
        3. Raising descriptive errors in access context
        4. Managing nested attribute chains
        The context analysis includes:
        - Frame inspection for operation type
        - AST analysis for statement structure
        - Position tracking for error reporting
        Args:
            name: Name of the attribute being accessed
            instance: Object instance where attribute belongs
            frame: Call frame or stack level for context
            new_return: Value to use for new attributes
        Returns:
            Any: Created attribute value in setting context
        Raises:
            AttributeError: When attribute doesn't exist in get context
        Example:
            >>> obj.nonexistent = 42  # Creates new attribute
            >>> print(obj.nonexistent)  # Prints 42
            >>> print(obj.missing)  # Raises AttributeError
        """
        """Create or handle attribute access in a dynamic object structure.
        This method provides the core functionality for dynamic attribute
        handling, determining whether to create new attributes or raise
        appropriate errors.
        Args:
            name: The attribute name being accessed or created
            instance: The object instance where the attribute belongs
            frame: Optional frame object or stack level for context analysis
            new_return: Optional value to use when creating new attributes
        Returns:
            Any: Created attribute value if in a setting context
        Raises:
            AttributeError: When attribute doesn't exist in a get context
        """
        # Get caller's frame if not provided for context analysis
        frame = cls.get_frame(frame)
        if not isframe(frame):
            raise AttributeError("No frame object found")
        # Suppress traceback for cleaner error messages
        original_tracebacklimit = getattr(sys, "tracebacklimit", -1)
        sys.tracebacklimit = 0
        # Prepare error message components with formatting
        header = "Attribute \033[1m" + name + "\033[0m not found "
        footer = indent(
            (f'File "{frame.f_code.co_filename}"' +
             f'line {frame.f_lineno}, in {frame.f_code.co_name}'),
            "   ",
        )
        cls.is_set(frame)
        new = AttributeError(f"{header}\n{footer}")
        # Check if we're in an attribute setting operation
        if cls.is_set(frame):
            sys.tracebacklimit = original_tracebacklimit
            # Create and set new attribute if in setting context
            new = None
            if new_return is not None:
                new = new_return
            elif instance is not None:
                new = type(instance)
            if callable(new):
                new = new()
            if instance is not None:
                setattr(instance, name, new)
            return new
        else:
            # Build detailed error for attribute access in get context
            current_node = cls.current_node(frame)
            if current_node:
                statement = current_node.statement
                new = AttributeError(header + "in \033[1m" +
                                     statement.before.replace(" ", "").replace(
                                         "\n", "").removesuffix(".") +
                                     "\033[0m\n" + footer + "\n" +
                                     indent(statement.text, "   "))
        # Raise error for invalid attribute access
        raise new
