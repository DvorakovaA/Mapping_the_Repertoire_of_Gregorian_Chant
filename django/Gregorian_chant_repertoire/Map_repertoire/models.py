"""
Script containing definitions of used models (= database tables) 
"""

from django.db import models


class Data_Chant(models.Model):
    """
    Table for data about all antiphons and responsories (chants)
    """
    cantus_id = models.CharField(("cantus_id"), max_length=20) # PK
    feast_id = models.CharField(("feast_id"), max_length=20) #FK
    source_id = models.CharField(("source_id"), max_length=500, null=True) #FK
    office_id = models.CharField(("office_id"), max_length=20, null=True)
    incipit = models.CharField(("incipit"), max_length=500, null=True)


class Sources(models.Model):
    """
    Table for important data about all sources of our chants
    """
    title = models.CharField(max_length=200)
    provenance_id = models.CharField(("provenance_id"), max_length=20, null=True) #FK
    provenance = models.CharField(("provenance"), max_length=500, null=True)
    century = models.CharField(("century"), max_length=50, null=True)
    num_century = models.CharField(("num_century"), max_length=7, null = True) # Not integer bc UNKNOWN century
    siglum = models.CharField(("siglum"), max_length=20, null=True)
    drupal_path = models.CharField(("drupal_path"), max_length=500, null=True) #PK
    cursus = models.CharField(("cursus"), max_length=10, null=True)


class Geography(models.Model):
    """
    Table for geography data about provenances
    """
    provenance_id = models.CharField(("provenance_id"), max_length=20, null=True) #PK
    provenance = models.CharField(("provenance"), max_length=500, null=True)
    latitude = models.FloatField(("latitude"), null=True)
    longitude = models.FloatField(("longitude"), null=True)


class Feasts(models.Model):
    """
    Table for data about all feasts that can possibly be searched
    """
    feast_id = models.CharField(("feast_id"), max_length=20, primary_key=True) #PK
    feast_code = models.CharField(("feast_code"), max_length=20)
    name = models.CharField(("name"), max_length=500)
