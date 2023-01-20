import pytest

from dict_model import DictModel, DictModelQueryset


class Example(DictModel):
    object_data = {
        1: {"name": "a", "foo": True, "valid": True},
        2: {"name": "b", "foo": False, "valid": True},
        3: {"name": "c", "foo": True, "valid": True},
    }


def test_dict_model_queryset_all_returns_collection_of_every_object():
    assert Example.objects.all() == [Example(1), Example(2), Example(3)]


def test_dict_model_queryset_count_returns_number_of_objects_in_collection():
    assert Example.objects.count() == 3


def test_dict_model_queryset_count_returns_zero_for_an_empty_set():
    assert Example.objects.filter(name="Z").count() == 0


def test_dict_model_queryset_count_returns_count_when_passed_an_object():
    assert Example.objects.count(Example(1)) == 1


def test_dict_model_queryset_count_returns_zero_if_passed_an_object_that_is_not_found():
    assert Example.objects.count("invalid") == 0


def test_dict_model_queryset_exclude():
    assert Example.objects.exclude(foo=True) == [Example(2)]


def test_dict_model_queryset_exclude_returns_empty_results_if_none_found():
    assert Example.objects.exclude(valid=True) == []


def test_dict_model_queryset_filter():
    assert Example.objects.filter(foo=True) == [Example(1), Example(3)]


def test_dict_model_queryset_filter_returns_empty_results_if_none_found():
    assert Example.objects.filter(foo="invalid") == []


def test_dict_model_queryset_first():
    assert Example.objects.first() == Example(1)


def test_dict_model_queryset_first_returns_none_when_collection_is_empty():
    assert Example.objects.filter(foo="invalid").first() is None


def test_dict_model_queryset_get():
    assert Example.objects.get(name="b") == Example(2)


def test_dict_model_queryset_raises_exception_if_no_results_are_found():
    with pytest.raises(DictModelQueryset.NoResultFound):
        Example.objects.get(foo="invalid")


def test_dict_model_queryset_get_raises_exception_if_multiple_results_are_found():
    with pytest.raises(DictModelQueryset.MultipleResultsFound):
        Example.objects.get(foo=True)


def test_dict_model_queryset_last():
    assert Example.objects.last() == Example(3)


def test_dict_model_queryset_last_returns_none_when_collection_is_empty():
    assert Example.objects.filter(foo="invalid").last() is None


def test_dict_model_queryset_can_chain_multiple_calls():
    assert Example.objects.filter(foo=True).exclude(name="a") == [Example(3)]
