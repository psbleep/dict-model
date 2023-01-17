import pytest

from dict_model import DictModel


class Example(DictModel):
    object_data = {1: {"hello": "world", "func": lambda self: self.hello}}


def test_dict_model_constructor_accepts_pointer_to_related_model():
    class Parent:
        pass

    related = Parent()
    obj = Example(id=1, related=related)

    # Generic attribute for related model.
    assert obj.related == related

    # Named attribute based on class name of related model.
    assert obj.parent == related


def test_dict_model_attribute_lookup():
    obj = Example(1)
    assert obj.hello == "world"


def test_dict_model_attribute_lookup_binds_callables():
    obj = Example(1)
    assert obj.func() == "world"


def test_dict_model_attribute_lookup_fails_if_not_set():
    obj = Example(1)
    with pytest.raises(AttributeError):
        obj.zoo


def test_dict_model_choices_returns_tuple_of_ids_and_names():
    class Decisions(DictModel):
        object_data = {1: {"yes": True, "name": "Yes"}, 2: {"yes": False, "name": "No"}}

    assert Decisions.choices() == [(1, "Yes"), (2, "No")]


def test_dict_model_choices_prioritizes_choice_attribute_over_name_attribute():
    class Decisions(DictModel):
        object_data = {
            1: {"yes": True, "choice": "Y", "name": "YES"},
            2: {"yes": False, "choice": "N", "name": "NO"},
        }

    assert Decisions.choices() == [(1, "Y"), (2, "N")]


def test_dict_model_choices_raises_validation_error_for_inconsistent_fields():
    class Invalid(DictModel):
        object_data = {1: {"hello": "world"}, 2: {"foo": "bar"}}

    with pytest.raises(Invalid.ValidationError):
        Invalid.choices()


def test_dict_model_choices_raises_validation_error_for_optional_and_required_fields():
    class OptionallyValid(DictModel):
        optional_fields = ["extra"]
        object_data = {1: {"hello": "world"}, 2: {"foo": "bar", "extra": True}}

    with pytest.raises(OptionallyValid.ValidationError):
        OptionallyValid.choices()


def test_dict_model_choices_does_not_raise_validation_error_for_optional_fields():
    class OptionallyValid(DictModel):
        optional_fields = ["extra"]
        object_data = {1: {"hello": "world"}, 2: {"hello": "foo", "extra": True}}

    assert OptionallyValid.choices()


def test_dict_model_choices_does_not_raise_error_if_validations_are_skipped():
    class SurprisinglyValid(DictModel):
        validate_fields = False
        object_data = {1: {"hello": "world"}, 2: {"foo": "bar"}}

    assert SurprisinglyValid.choices()


def test_dict_model_repr():
    class Represent(DictModel):
        object_data = {1: {"stringy": "abc", "numby": 136.23, "booly": False}}

    assert repr(Represent(id=1)) == (
        "Represent(id=1, related=None, stringy='abc', numby=136.23, booly=False)"
    )


def test_dict_model_repr_with_related():
    class Child(DictModel):
        object_data = {3: {"name": "hello"}}

    class ParentModel:
        def __init__(self, id):
            self.id = id

    assert repr(Child(id=3, related=ParentModel(id=7))) == (
        "Child(id=3, parent_model=ParentModel(7), name='hello')"
    )
