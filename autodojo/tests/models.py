"""
The unit tests for the autodojo lib require some ORM
models to be defined. Note: We don't actually need a database
behind these, as we're only testing what AutoDojo will
create when fed these model definitions.
"""

from django.db import models


class DummyModel(models.Model):
    count = models.IntegerField()
    name = models.TextField()

    class Meta:
        # We need to specify this to ensure the model resolution will work
        app_label = "autodojo"


class RelatedDummyModel(models.Model):
    dummy = models.ForeignKey(DummyModel, on_delete=models.CASCADE)
    relation = models.TextField()

    class Meta:
        # We need to specify this to ensure the model resolution will work
        app_label = "autodojo"
