from dict_model import DictModel, dict_model_object


class Example(DictModel):
    optional_fields = ["func"]


@dict_model_object(Example)
class FooBar:
    bar = "baz"


def test_dict_model_object_decorator_adds_entry_to_dict_model_data():
    assert Example.object_data == {1: {"bar": "baz"}}


def test_dict_model_object_decorator_assigns_id_constant_for_type():
    assert Example.FOO_BAR == 1


def test_dict_model_object_decorator_properly_increments_id_for_new_entries():
    @dict_model_object(Example)
    class Bar:
        bar = "foo"

    assert list(Example.object_data.keys()) == [1, 2]


def test_dict_model_object_decorator_accepts_type_id_option():
    @dict_model_object(Example, type_id=6)
    class Boo:
        bar = "boo"

    assert 6 in Example.object_data.keys()


def test_dict_model_object_decorator_accepts_type_id_constant_name_option():
    @dict_model_object(Example, type_id=111, constant_name="CUSTOM")
    class Bam:
        bar = "bam"

    assert Example.CUSTOM == 111


def test_dict_model_object_decorator_binds_functions_properly():
    @dict_model_object(Example, type_id=222)
    class Bom:
        bar = "bom"

        def func(self):
            return f"called: {self.bar}"

    assert Example(222).func() == "called: bom"
