from django.db import models


class Data_Chant(models.Model):
    cantus_id = models.CharField(("cantus_id"), max_length=20)
    siglum = models.CharField(("siglum"), max_length=20, null=True)
    feast_id = models.CharField(("feast_id"), max_length=20)
    source_id = models.CharField(("source_id"), max_length=500, null=True)


class Source(models.Model):
    title = models.CharField(max_length=200)
    provenance_id = models.CharField(("provenance_id"), max_length=20, null=True)
    century = models.CharField(("century"), max_length=50, null=True)
    drupal_path = models.CharField(("drupal_path"), max_length=500, null=True)


class Geography(models.Model):
    provenance_id = models.CharField(("provenance_id"), max_length=20, null=True)
    provenance = models.CharField(("provenance"), max_length=500, null=True)
    latitude = models.FloatField(("latitude"))
    longitude = models.FloatField(("longitude"))
