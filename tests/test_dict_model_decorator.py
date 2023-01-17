from dict_model import DictModel, dict_model


class Example(DictModel):
    object_data = {1: {"hello": "world"}, 2: {"hello": False}}


class Model:
    def __init__(self, example_id):
        self.example_id = example_id

    @property
    @dict_model(Example)
    def example(self):
        pass


def test_dict_model_decorator_looks_up_dict_model_by_id_field():
    model = Model(example_id=1)
    assert model.example == Example(id=1)


def test_dict_model_decorator_passes_in_pointer_to_related_model():
    model = Model(example_id=1)
    assert model.example.related == model


def test_dict_model_decorator_accepts_custom_id_field_name():
    class CustomModel:
        def __init__(self, custom_id):
            self.custom_id = custom_id

        @property
        @dict_model(Example, field_name="custom_id")
        def example(self):
            pass

    model = CustomModel(custom_id=2)
    assert model.example == Example(id=2)
