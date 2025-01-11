[![ci](https://github.com/Apkawa/django-snapshot-field/actions/workflows/ci.yml/badge.svg)](https://github.com/Apkawa/django-snapshot-field/actions/workflows/ci.yml)

[![PyPi](https://img.shields.io/pypi/v/django-snapshot-field.svg)](https://pypi.python.org/pypi/django-snapshot-field)
[![PyPI](https://img.shields.io/pypi/pyversions/django-snapshot-field.svg)](https://pypi.python.org/pypi/django-snapshot-field)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A field in a model that stores a snapshot of a model object and retrieves it as a read-only model object

# Installation

```bash
pip install django-snapshot-field
```

or from git

```bash
pip install -e git+https://githib.com/Apkawa/django-snapshot-field.git#egg=django-snapshot-field
```

## Django and python version compatibles


| Python<br/>Django | 3.8 | 3.9 | 3.10 | 3.11 | 3.12 | 3.13 |
|:-----------------:|-----|----|------|------|------|------|
|        4.2        | ✅   | ✅  | ✅    | ✅    | ✅    | ✅    |
|        5.0        | ❌   | ❌   | ✅    | ✅    | ✅    | ✅    |
|        5.1        | ❌   | ❌   | ✅    | ✅    | ✅    | ✅    |
|        5.2        | ❌   | ❌   | ✅    | ✅    | ✅    | ✅    |



# Usage

```python
from django.db import models
from snapshot_field.fields import SnapshotModelField

class Example(models.Model):
    name = models.CharField(max_length=20)

class ExampleReference(models.Model):
    name = models.CharField(max_length=20)
    ref = models.ForeignKey(Example)


class ExampleSnapshotModel(models.Model):
    snapshot = SnapshotModelField(null=True)
    snapshot_refs = SnapshotModelField(
        ['tests.Example', ['ExampleReference', {'fields': ['name', 'ref'], 'refs': ['ref']}]]
    )


obj = Example.objects.create(name='test_name')
obj_ref = ExampleReference.objects.create(name='refname', ref=obj)

snap = ExampleSnapshotModel.objects.create(snapshot=obj, snapshot_refs=obj_ref)

assert snap.snapshot.name == obj.name
assert snap.snapshot_refs.name == obj_ref.name
assert snap.snapshot_refs.ref.name == obj.name

obj.delete()
obj_ref.delete()
snap.refresh_from_db()

assert snap.snapshot.name == obj.name
assert snap.snapshot_refs.name == obj_ref.name
assert snap.snapshot_refs.ref.name == obj.name
```
