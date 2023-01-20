import pytest

from dict_model import DictModel, DictModelQueryset


class Example(DictModel):
    object_data = {
        1: {"name": "a", "foo": True, "valid": True},
        2: {"name": "b", "foo": False, "valid": True},
        3: {"name": "c", "foo": True, "valid": True},
    }


@pytest.fixture
def queryset():
    examples = [Example(1), Example(2), Example(3)]
    return DictModelQueryset(examples)


def test_dict_model_queryset_all_returns_collection_of_every_object(queryset):
    assert queryset.all() == [Example(1), Example(2), Example(3)]


def test_dict_model_queryset_count_returns_number_of_objects_in_collection(queryset):
    assert queryset.count() == 3


def test_dict_model_queryset_count_returns_zero_for_an_empty_set():
    assert DictModelQueryset([]).count() == 0


def test_dict_model_queryset_count_returns_count_of_object(queryset):
    assert queryset.count(Example(1)) == 1


def test_dict_model_queryset_count_returns_zero_if_passed_an_object_that_is_not_found(
    queryset,
):
    assert queryset.count("not-found") == 0


def test_dict_model_queryset_exclude(queryset):
    assert queryset.exclude(foo=True) == [Example(2)]


def test_dict_model_queryset_exclude_returns_empty_results_if_none_found(queryset):
    assert queryset.exclude(valid=True) == []


def test_dict_model_queryset_filter(queryset):
    assert queryset.filter(foo=True) == [Example(1), Example(3)]


def test_dict_model_queryset_filter_returns_empty_results_if_none_found(queryset):
    assert queryset.filter(foo="invalid") == []


def test_dict_model_queryset_first(queryset):
    assert queryset.first() == Example(1)


def test_dict_model_queryset_first_returns_none_when_collection_is_empty():
    assert DictModelQueryset([]).first() is None


def test_dict_model_queryset_get(queryset):
    assert queryset.get(name="b") == Example(2)


def test_dict_model_queryset_raises_exception_if_no_results_are_found(queryset):
    with pytest.raises(DictModelQueryset.NoResultFound):
        queryset.get(foo="invalid")


def test_dict_model_queryset_get_raises_exception_if_multiple_results_are_found(
    queryset,
):
    with pytest.raises(DictModelQueryset.MultipleResultsFound):
        queryset.get(foo=True)


def test_dict_model_queryset_last(queryset):
    assert queryset.last() == Example(3)


def test_dict_model_queryset_last_returns_none_when_collection_is_empty():
    assert DictModelQueryset([]).last() is None


def test_dict_model_queryset_can_chain_multiple_calls(queryset):
    assert queryset.filter(foo=True).exclude(name="a") == [Example(3)]
