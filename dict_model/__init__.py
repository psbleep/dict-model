import functools
import re
from collections import UserDict, UserList
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type

from django.utils.functional import classproperty


def snake_case(pascal_case: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", pascal_case).lower()


class DictModelObjects(UserList):
    class NoResultFound(Exception):
        pass

    class MultipleResultsFound(Exception):
        pass

    def __init__(self, collection: Iterable["DictModel"]) -> None:
        self.data = list(collection)

    def __repr__(self) -> str:
        obj_repr = ", ".join(
            [f"{obj.__class__.__name__}({obj.id})" for obj in self.data]
        )
        return f"DictModelObjects([{obj_repr}])"

    def all(self) -> "DictModelObjects":
        return DictModelObjects(self.data)

    def count(self, item: Optional[Any] = None) -> int:
        return len(self.data)

    def exclude(self, **kwargs) -> "DictModelObjects":
        return DictModelObjects(
            [obj for obj in self.data if not self._check_filter(obj, **kwargs)]
        )

    def filter(self, **kwargs) -> "DictModelObjects":
        return DictModelObjects(
            [obj for obj in self.data if self._check_filter(obj, **kwargs)]
        )

    @staticmethod
    def _check_filter(obj, **kwargs) -> bool:
        for key, value in kwargs.items():
            if getattr(obj, key) != value:
                return False
        return True

    def first(self) -> Optional["DictModel"]:
        try:
            return self.data[0]
        except IndexError:
            return None

    def get(self, **kwargs) -> Optional["DictModel"]:
        results = self.filter(**kwargs)
        if not results:
            raise self.NoResultFound()
        elif len(results) > 1:
            raise self.MultipleResultsFound()

        return results.first()

    def last(self) -> Optional["DictModel"]:
        try:
            return self.data[-1]
        except IndexError:
            return None


class DictModel(UserDict):
    class ValidationError(Exception):
        pass

    validate_fields: bool = True
    optional_fields: List[str] = []

    object_data: Dict = {}

    @classmethod
    def choices(cls) -> List[Tuple[int, str]]:
        cls._validate_fields()
        _choices = []
        for type_id, type_data in cls.object_data.items():
            type_choice = type_data.get("choice") or type_data.get("name")
            _choices.append((type_id, type_choice))
        return _choices

    @classmethod
    def _validate_fields(cls) -> None:
        if not cls.validate_fields:
            return

        _fields = None
        _optional_fields = set(cls.optional_fields)
        for type_attrs in cls.object_data.values():
            type_fields = sorted(list(set(type_attrs.keys()) - _optional_fields))
            _fields = _fields or type_fields
            if _fields != type_fields:
                raise cls.ValidationError(f"{cls.__name__}: Fields do not match!")

    def __init__(self, id: int, related: Optional[Any] = None) -> None:
        self.id = id
        self.related = related
        self.related_name = snake_case(related.__class__.__name__)
        setattr(self, self.related_name, related)

        self.data = self.object_data[id]

    def __eq__(self, other: Any) -> bool:
        try:
            return self.id == other.id
        except AttributeError:
            return False

    def __getattr__(self, attr: Any) -> Optional[Any]:
        try:
            value = self.data[attr]
        except KeyError as err:
            raise AttributeError(str(err))

        # Callables attached to a dict model object in the `object_data` dict will not
        # already be bound to their objects. Bind them here.
        if callable(value) and not hasattr(value, "__self__"):
            value = functools.partial(value, self)
        return value

    def __repr__(self) -> str:
        unformatted_data = [f"id={self.id}", self._get_related_repr()]
        formatted_data = [f"{k}={v!r}" for k, v in self.data.items()]
        data = ", ".join(unformatted_data + formatted_data)
        return f"{self.__class__.__name__}({data})"

    def _get_related_repr(self) -> str:
        if not self.related:
            return "related=None"

        return (
            f"{self.related_name}={self.related.__class__.__name__}({self.related.id})"
        )

    @classproperty
    def objects(cls):
        return DictModelObjects([cls(id) for id in cls.object_data.keys()])


def dict_model(dict_model_cls: Type[DictModel], field_name: Optional[str] = None):
    def dict_model_wrapper(func):
        @functools.wraps(func)
        def dict_model_inner(obj: Any):
            _field_name = field_name or f"{func.__name__}_id"
            type_id = getattr(obj, _field_name)
            dict_model = dict_model_cls(id=type_id, related=obj)
            return dict_model

        return dict_model_inner

    return dict_model_wrapper


def dict_model_object(
    dict_model_cls: Type[DictModel],
    type_id: Optional[int] = None,
    constant_name: Optional[str] = None,
) -> Callable:
    # TODO: cleaner id assignment
    if not type_id:
        if dict_model_cls.object_data:
            type_id = max(list(dict_model_cls.object_data.keys())) + 1
        else:
            type_id = 1

    def dict_model_object_wrapper(type_cls: Any) -> Any:
        _constant_name = constant_name or snake_case(type_cls.__name__).upper()
        setattr(dict_model_cls, _constant_name, type_id)
        # TODO: cleaner way to get only custom attributes
        attributes = {
            field: getattr(type_cls, field)
            for field in set(dir(type_cls)) - set(dir(DictModel))
        }
        dict_model_cls.object_data[type_id] = attributes
        return type_cls

    return dict_model_object_wrapper
