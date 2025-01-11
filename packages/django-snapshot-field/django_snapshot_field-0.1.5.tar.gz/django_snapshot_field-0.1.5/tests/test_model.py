# -*- coding: utf-8 -*-
from tests.models import Example, ExampleReference, ExampleSnapshotModel


def test_model_create():
    obj = Example.objects.create(name='test_name')
    obj_ref = ExampleReference.objects.create(name='refname', ref=obj)

    snap = ExampleSnapshotModel.objects.create(snapshot=obj, snapshot_refs=obj_ref)
    assert snap.snapshot.name == obj.name
    assert snap.snapshot_refs.name == obj_ref.name
    assert snap.snapshot_refs.ref.name == obj.name


def test_model_save():
    obj = Example.objects.create(name='test_name')
    obj_ref = ExampleReference.objects.create(name='refname', ref=obj)

    snap = ExampleSnapshotModel.objects.create(snapshot=None, snapshot_refs=obj_ref)
    assert not snap.snapshot
    assert snap.snapshot_refs.name == obj_ref.name
    snap.snapshot_refs = obj
    snap.save()
    snap = ExampleSnapshotModel.objects.get()
    assert not snap.snapshot
    assert snap.snapshot_refs.name == obj.name


def test_model_delete():
    obj = Example.objects.create(name='test_name')
    obj_ref = ExampleReference.objects.create(name='refname', ref=obj)

    snap = ExampleSnapshotModel.objects.create(snapshot=obj, snapshot_refs=obj_ref)

    obj.delete()
    obj_ref.delete()
    snap.refresh_from_db()

    assert snap.snapshot.name == obj.name
    assert snap.snapshot_refs.name == obj_ref.name
    assert snap.snapshot_refs.ref.name == obj.name
