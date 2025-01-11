import json

from snapshot_field.utils import (
    serialize_object,
    deserialize_object,
    serialize_object_json,
    deserialize_object_json,
)
from tests.models import Example, ExampleReference


def test_simple_serialize_and_deserialization():
    obj = Example.objects.create(name="test_name")

    result = serialize_object(obj)
    obj_snapshot = deserialize_object(result)
    assert obj.id == obj_snapshot.id
    assert obj.name == obj_snapshot.name


def test_simple_serialize_and_deserialize_refs():
    obj = Example.objects.create(name="test_name")
    obj_ref = ExampleReference.objects.create(name="refname", ref=obj)

    result = serialize_object(obj_ref, refs=["ref"])
    obj_snapshot = deserialize_object(result)
    assert obj_ref.id == obj_snapshot.id
    assert obj_ref.name == obj_snapshot.name
    assert obj_ref.ref.name == obj.name


def test_json_serialize_deserialize():
    obj = Example.objects.create(name="test_name")
    obj_ref = ExampleReference.objects.create(name="refname", ref=obj)

    result = serialize_object_json(obj_ref, refs=["ref"])
    obj_snapshot = deserialize_object_json(result)

    assert obj_ref.id == obj_snapshot.id
    assert obj_ref.name == obj_snapshot.name
    assert obj_ref.ref.name == obj.name


def test_json_serialize_deserialize_deleted_obj():
    obj = Example.objects.create(name="test_name")
    obj_ref = ExampleReference.objects.create(name="refname", ref=obj)

    result = serialize_object_json(obj_ref, refs=["ref"])

    expect_data = {
        "model": "tests.examplereference",
        "pk": obj_ref.id,
        "fields": {"name": "refname", "long_name": "", "ref": obj.id},
        "refs": {
            "ref": {
                "model": "tests.example",
                "pk": obj.id,
                "fields": {"name": "test_name"},
                "refs": {},
            }
        },
    }

    obj.delete()
    obj_ref.delete()

    assert json.loads(result) == expect_data

    obj_snapshot = deserialize_object_json(result)

    assert obj_ref.name == obj_snapshot.name
    assert obj_ref.ref.name == obj.name


def test_json_serialize_deserialize_with_non_existed_fields():
    obj = Example.objects.create(name="test_name")
    obj_ref = ExampleReference.objects.create(name="refname", ref=obj)

    result = serialize_object_json(obj_ref, refs=["ref"])
    result_dict = json.loads(result)
    # Unexisted fields and refs must be ignore
    result_dict["fields"]["slug"] = "removed field"
    result = json.dumps(result_dict)
    obj_snapshot = deserialize_object_json(result)
    assert obj_ref.id == obj_snapshot.id
    assert obj_ref.name == obj_snapshot.name
    assert obj_ref.ref.name == obj.name


def test_json_serialize_deserialize_with_new_fields():
    obj = Example.objects.create(name="test_name")
    obj_ref = ExampleReference.objects.create(name="refname", ref=obj)

    result = serialize_object_json(obj_ref, refs=["ref"])
    result_dict = json.loads(result)
    # Maybe ref has been create after serialization
    del result_dict["fields"]["long_name"]
    result = json.dumps(result_dict)
    obj_snapshot = deserialize_object_json(result)
    assert obj_ref.id == obj_snapshot.id
    assert obj_ref.name == obj_snapshot.name
    assert obj_ref.ref.name == obj.name
