# -*- coding: utf-8 -*-
import pytest as pytest

from snapshot_field.utils import serialize_object_json, deserialize_object_json

try:
    from measurement.measures import Distance
except ImportError:
    Distance = None


@pytest.mark.skipif(not Distance, reason="django-measurement not installed")
def test_measurement_json_serialize_deserialize():
    from tests.models import MeasurementModel

    obj = MeasurementModel.objects.create(height=Distance(cm=20.0))

    result = serialize_object_json(obj)
    obj_snapshot = deserialize_object_json(result)
    assert obj_snapshot
    assert obj_snapshot.height == obj.height


@pytest.mark.skipif(not Distance, reason="django-measurement not installed")
def test_model_save():
    from tests.models import MeasurementModel, ExampleSnapshotModel

    obj = MeasurementModel.objects.create(height=Distance(cm=12.5))

    snap = ExampleSnapshotModel.objects.create(snapshot=obj)
    assert snap.snapshot
    assert snap.snapshot.height == obj.height
    snap = ExampleSnapshotModel.objects.get()
    assert snap.snapshot
    assert snap.snapshot.height == obj.height
