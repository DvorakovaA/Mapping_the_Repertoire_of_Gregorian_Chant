"""
Script containing definitions of used models (= database tables) 
"""

from django.db import models


class Data_Chant(models.Model):
    """
    Table for data about all antiphons and responsories (chants)
    """
    cantus_id = models.CharField(("cantus_id"), max_length=20)
    feast_id = models.CharField(("feast_id"), max_length=20)
    source_id = models.CharField(("source_id"), max_length=500, null=True)


class Sources(models.Model):
    """
    Table for important data about all sources of our chants
    """
    title = models.CharField(max_length=200)
    provenance_id = models.CharField(("provenance_id"), max_length=20, null=True)
    century = models.CharField(("century"), max_length=50, null=True)
    siglum = models.CharField(("siglum"), max_length=20, null=True)
    drupal_path = models.CharField(("drupal_path"), max_length=500, null=True)


class Geography(models.Model):
    """
    Table for geography data about provenances
    """
    provenance_id = models.CharField(("provenance_id"), max_length=20, null=True)
    provenance = models.CharField(("provenance"), max_length=500, null=True)
    latitude = models.FloatField(("latitude"), null=True)
    longitude = models.FloatField(("longitude"), null=True)


class Feasts(models.Model):
    """
    Table for data about all feasts that can possibly be searched
    """
    feast_id = models.CharField(("feast_id"), max_length=20, primary_key=True)
    feast_code = models.CharField(("feast_code"), max_length=20)
    name = models.CharField(("name"), max_length=500)