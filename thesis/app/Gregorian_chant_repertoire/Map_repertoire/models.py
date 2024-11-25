"""
Class definitions of used models (= database tables) and their fields 
"""

from django.db import models


class Data_Chant(models.Model):
    """
    Table for data about all antiphons and responsories (chants)
    """
    cantus_id = models.CharField(("cantus_id"), max_length=20) # PK - setting it as "primary_key = True" did not work
    feast_code = models.CharField(("feast_code"), max_length=20, null=True) #FK
    source_id = models.CharField(("source_id"), max_length=500, null=True) #FK
    office_id = models.CharField(("office_id"), max_length=20, null=True)
    incipit = models.CharField(("incipit"), max_length=500, null=True)
    dataset = models.CharField(("dataset"), max_length=500, null=True) #FK


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
    dataset = models.CharField(("dataset"), max_length=500, null=True) #FK


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
    feast_code = models.CharField(("feast_code"), max_length=20, default='unknown') #PK
    name = models.CharField(("name"), max_length=500)


class Datasets(models.Model):
    """
    Table for info about user's datasets
    ID in form: Owner_DatasetName (contcatenation of owner user name and provided dataset name)
    """
    dataset_id = models.CharField(("dataset_id"), max_length=100, null=True) #PK
    name = models.CharField(("name"), max_length=500)
    owner = models.CharField(("owner"), max_length=50)
    public = models.BooleanField(("public"), default=False)
