import uuid
from django.db import models


class EquipmentDataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    original_filename = models.CharField(max_length=255)
    csv_file = models.FileField(upload_to="uploads/")

    total_count = models.PositiveIntegerField(default=0)
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)

    # type -> count (or percentage)
    type_distribution = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # latest first

    def __str__(self):
        return self.name or self.original_filename
