# mypy: ignore-errors
from typing import Union, Any, Optional, TYPE_CHECKING, cast

# To find out what type mypy infers for an expression anywhere in
# your program, wrap it in reveal_type().  Mypy will print an error
# message with the type; remove it again before running the code.
reveal_type(1)  # Revealed type is "builtins.int"

# If you initialize a variable with an empty container or "None"
# you may have to help mypy a bit by providing an explicit type annotation
x: list[str] = []
x: Optional[str] = None # type: ignore

# Use Any if you don't know the type of something or it's too
# dynamic to write a type for
x: Any = mystery_function() # type: ignore
# Mypy will let you do anything with x!
x.whatever() * x["you"] + x("want") - any(x) and all(x) is super  # no errors # type: ignore

# Use a "type: ignore" comment to suppress errors on a given line,
# when your code confuses mypy or runs into an outright bug in mypy.
# Good practice is to add a comment explaining the issue.
x = confusing_function()  # type: ignore  # confusing_function won't return None here because ...

# "cast" is a helper function that lets you override the inferred
# type of an expression. It's only for mypy -- there's no runtime check.
a = [4]
b = cast(list[int], a)  # Passes fine
c = cast(list[str], a)  # Passes fine despite being a lie (no runtime check)
reveal_type(c)  # Revealed type is "builtins.list[builtins.str]"
print(c)  # Still prints [4] ... the object is not changed or casted at runtime

# Use "TYPE_CHECKING" if you want to have code that mypy can see but will not
# be executed at runtime (or to have code that mypy can't see)
if TYPE_CHECKING:
    import json
else:
    import orjson as json  # mypy is unaware of this

# mypy_test.py:6: note: Revealed type is "Literal[1]?"
# mypy_test.py:11: error: Name "x" already defined on line 10  [no-redef]
# mypy_test.py:15: error: Name "x" already defined on line 10  [no-redef]
# mypy_test.py:15: error: Name "mystery_function" is not defined  [name-defined]
# mypy_test.py:17: error: "List[str]" has no attribute "whatever"  [attr-defined]
# mypy_test.py:17: error: No overload variant of "__getitem__" of "list" matches argument type "str"  [call-overload]
# mypy_test.py:17: note: Possible overload variants:
# mypy_test.py:17: note:     def __getitem__(self, SupportsIndex, /) -> str
# mypy_test.py:17: note:     def __getitem__(self, slice, /) -> List[str]
# mypy_test.py:17: error: "List[str]" not callable  [operator]
# mypy_test.py:29: note: Revealed type is "builtins.list[builtins.str]"
# Found 6 errors in 1 file (checked 1 source file)