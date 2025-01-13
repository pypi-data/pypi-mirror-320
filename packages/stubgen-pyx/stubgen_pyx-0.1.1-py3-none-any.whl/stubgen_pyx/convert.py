from abc import ABC, abstractmethod
import ast
from dataclasses import dataclass, field
import inspect
import logging
from textwrap import dedent, indent
from typing import Optional

from stubgen_pyx._version import __version__


_INDENT = "    "

# Generally not useful names to include in the stub.
#
# Either it is a Cython internal name, it's a name included in most class definitions,
# or it provides little information to the user. This list is entirely subjective.
_DISALLOWED_NAMES: set[str] = {
    "__doc__",
    "__file__",
    "__loader__",
    "__name__",
    "__package__",
    "__pyx_capi__",
    "__spec__",
    "__test__",
    "__class__",
    "__dir__",
    "__format__",
    "__getstate__",
    "__hash__",
    "__init_subclass__",
    "__new__",
    "__reduce__",
    "__reduce_ex__",
    "__setstate__",
    "__sizeof__",
    "__subclasshook__",
    "__weakref__",
    "__delattr__",
    "__eq__",
    "__getattribute__",
    "__ge__",
    "__gt__",
    "__le__",
    "__lt__",
    "__ne__",
    "__repr__",
    "__setattr__",
    "__reduce_cython__",
    "__setstate_cython__",
    "__str__",
    "__annotations__",
    "__dataclass_fields__",
    "__dataclass_params__",
    "__dict__",
    "__match_args__",
    "__module__",
    # Specific to this project
    "__cimport_types__",
}


def _docstring_to_string(docstring: str, indentation: int) -> str:
    return f'{_INDENT * indentation}"""{indent(dedent(docstring), _INDENT * indentation)}{_INDENT * indentation}"""'


def _is_valid_signature(signature: str) -> bool:
    # Hack: Use the ast module to parse the signature to see if it is valid
    try:
        ast.parse(f"def {signature}: pass")
        return True
    except SyntaxError:
        return False


@dataclass
class Convertable(ABC):
    """
    An element that can be converted to lines of a `.pyi` file.
    """

    @abstractmethod
    def key(self) -> tuple:
        raise NotImplementedError

    @abstractmethod
    def to_pyi(self, indentation: int) -> str:
        raise NotImplementedError


@dataclass
class Import(Convertable):
    """
    A bare import statement (i.e. `foo` in `import foo`).
    """

    module: str
    name: str = ""
    alias: str = ""

    def key(self) -> tuple:
        return 0, self.module, self.name, self.alias

    def to_pyi(self, indentation: int) -> str:
        if self.name:
            result = f"from {self.module} import {self.name}"
        else:
            result = f"import {self.module}"
        if self.alias:
            result = f"{result} as {self.alias}"
        return f"{_INDENT * indentation}{result}"

    def out_name(self) -> str:
        if self.alias:
            return self.alias
        elif self.name:
            return self.name
        return self.module


@dataclass
class Annotation(Convertable):
    """
    Simple type annotation.
    """

    name: str
    annotation: str = "object"

    def key(self) -> tuple:
        return 1, self.name, self.annotation

    def to_pyi(self, indentation: int) -> str:
        return f"{_INDENT * indentation}{self.name}: {self.annotation}"


@dataclass
class ClassDefinition(Convertable):
    name: str
    cls: object

    def key(self) -> tuple:
        return 3, self.name, self.cls

    def to_pyi(self, indentation: int) -> str:
        result = f"{_INDENT * indentation}class {self.name}:\n"
        if self.cls.__doc__:
            result = (
                f"{result}{_docstring_to_string(self.cls.__doc__, indentation + 1)}\n"
            )
        return f"{result}{Body(self.cls).to_pyi(indentation + 1)}"


@dataclass
class FunctionDefinition(Convertable):
    name: str
    func: object

    def key(self) -> tuple:
        return 4, self.name, self.func

    def default_definition(self) -> str:
        return f"{self.name}(*args, **kwargs)"

    def to_pyi(self, indentation: int) -> str:
        definition: str = ""
        docstring: str = ""

        if self.func.__doc__ and _is_valid_signature(
            (split_docs := self.func.__doc__.split("\n", 1))[0]
        ):
            # Embedded signature docstring
            definition = split_docs[0]
            docstring = split_docs[1] if len(split_docs) > 1 else ""
        elif self.func.__doc__:
            # Regular docstring
            try:
                definition = f"{self.name}{inspect.signature(self.func)}"
            except ValueError:
                definition = self.default_definition()
            docstring = self.func.__doc__
        else:
            # No docstring
            try:
                definition = f"{self.name}{inspect.signature(self.func)}"
            except ValueError:
                definition = self.default_definition()
        if docstring:
            return f"{_INDENT * indentation}def {definition}: \n{_docstring_to_string(docstring, indentation + 1)}"
        return f"{_INDENT * indentation}def {definition}: ..."


@dataclass
class Body(Convertable):
    """
    The body of a class definition or a module.
    """

    obj: object

    def key(self) -> tuple:
        # Bodies are single children of pyi elements, they don't need a sorting key.
        return (-1,)

    def _is_function(self, value) -> bool:
        return inspect.isfunction(value) or value.__class__.__name__ in (
            "cython_function_or_method",
            "wrapper_descriptor",
            "method_descriptor",
        )

    def _is_class(self, value) -> bool:
        return inspect.isclass(value)

    def _is_datadescriptor(self, value) -> bool:
        return inspect.isdatadescriptor(value)

    def _to_convertable(self, name: str, obj: object) -> Optional[Convertable]:
        if (
            name in _DISALLOWED_NAMES
            or name.startswith("__pyx_")
            or not name.isidentifier()
        ):
            return

        if self._is_class(obj):
            return ClassDefinition(name, obj)
        elif self._is_function(obj):
            return FunctionDefinition(name, obj)
        elif self._is_datadescriptor(obj):
            doc = obj.__doc__ if obj.__doc__ else ""
            if doc.startswith(f"{name}: "):
                return Annotation(name, annotation=doc[len(name) + 2 :])
            return Annotation(name)
        elif not isinstance(obj, type):
            # value is an object, probably a module-level constant
            return Annotation(name, obj.__class__.__name__)

    def members(self) -> list[Convertable]:
        annotations = [
            Annotation(name, annotation=type_)
            for name, type_ in inspect.get_annotations(self.obj).items()
        ]
        result = (
            self._to_convertable(name, value)
            for name, value in inspect.getmembers(self.obj)
        )
        members = [member for member in result if member is not None]
        members.extend(annotations)
        members.sort(key=lambda member: member.key())
        return members

    def to_pyi(self, indentation: int) -> str:
        members = self.members()
        members.sort(key=lambda member: member.key())
        return "\n".join([member.to_pyi(indentation) for member in members])


class BodyWithImports(Body):
    def _is_imported(self, value) -> bool:
        if inspect.ismodule(value):
            return True
        if not hasattr(value, "__module__") or not hasattr(value, "__name__"):
            return False
        return value.__module__ != self.obj.__name__

    def to_import(self, name: str, value: object) -> Import:
        has_module = hasattr(value, "__module__")
        alias = "" if value.__name__ == name else name
        name_ = value.__name__ if has_module else ""
        module = value.__module__ if has_module else value.__name__
        return Import(module=module, name=name_, alias=alias)

    def _to_convertable(self, name, obj):
        if self._is_imported(obj):
            return
        return super()._to_convertable(name, obj)

    def imports(self) -> list[Import]:
        return [
            self.to_import(name, value)
            for name, value in inspect.getmembers(self.obj)
            if self._is_imported(value)
        ]


class AstNameTransformer(ast.NodeTransformer):
    _cython_ints: tuple[str] = (
        "char",
        "short",
        "Py_UNICODE",
        "Py_UCS4",
        "long",
        "longlong",
        "Py_hash_t",
        "Py_ssize_t",
        "size_t",
        "ssize_t",
        "ptrdiff_t",
    )

    _cython_floats: tuple[str] = (
        "longdouble",
        "double",
    )

    _cython_complex: tuple[str] = (
        "longdoublecomplex",
        "doublecomplex",
        "floatcomplex",
    )

    _cython_translation: dict[str, str] = None

    collected_names: set[str]

    def __init__(self) -> None:
        super().__init__()

        self.collected_names = set()

        self._cython_translation = {
            "bint": "bool",
            "unicode": "str",
        }

        self._cython_translation.update({k: "int" for k in self._cython_ints})

        self._cython_translation.update({k: "float" for k in self._cython_floats})

        self._cython_translation.update({k: "complex" for k in self._cython_complex})

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id in self._cython_translation:
            node.id = self._cython_translation[node.id]
        self.collected_names.add(node.id)
        return node


@dataclass
class ImportList(Convertable):
    module: str
    names: list[tuple[str, str]] = field(default_factory=list)

    def key(self) -> tuple:
        return 0, self.module, self.names

    def to_pyi(self, indentation: int) -> str:
        result = f"{_INDENT * indentation}from {self.module} import "

        for name, alias in self.names:
            result += f"{name}"
            if alias and alias != name:
                result += f" as {alias}"
            result += ", "

        return result.rstrip(", ")


def convert_module(module: object) -> str:
    """
    Converts a Cython module to a `.pyi` file.
    """
    header = f"# This file was generated by stubgen-pyx v{__version__}\n"

    if doc := module.__doc__:
        header = f"{header}{_docstring_to_string(doc, 0)}\n\n"

    module_body = BodyWithImports(module)

    imports = module_body.imports()

    if hasattr(module, "__cimport_types__"):
        cimport_types = module.__cimport_types__
        if isinstance(cimport_types, type):
            cimport_types = (cimport_types,)
        for cimport_type in cimport_types:
            imports.append(module_body.to_import(cimport_type.__name__, cimport_type))

    body_content = module_body.to_pyi(0)

    try:
        ast_body = ast.parse(body_content)
        transformer = AstNameTransformer()
        transformer.visit(ast_body)
        body_content = ast.unparse(ast_body)
        imports = [
            import_
            for import_ in imports
            if import_.out_name() in transformer.collected_names
        ]
    except SyntaxError as e:
        logging.warning(f"SyntaxError in {module.__name__}: {e}")

    if not imports:
        return f"{header}{body_content}"

    bare_imports: list[Import] = []
    joined_imports: dict[str, ImportList] = {}

    for import_ in imports:
        if not import_.name:
            bare_imports.append(import_)
            continue

        if import_.module in joined_imports:
            joined_imports[import_.module].names.append((import_.name, import_.alias))
        else:
            joined_imports[import_.module] = ImportList(
                import_.module, [(import_.name, import_.alias)]
            )

    bare_imports.extend(joined_imports.values())
    imports = bare_imports
    imports.sort(key=lambda import_: import_.key())

    return f"{header}{'\n'.join(import_.to_pyi(0) for import_ in imports)}\n\n{body_content}"
