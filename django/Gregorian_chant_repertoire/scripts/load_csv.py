"""
Python script that loads data from csv to django databases
Data_Chant
Sources
Geography
Feasts

Loads only chants from surces where we have more than 100 chants from that source
"""

from Map_repertoire.models import Data_Chant, Sources, Geography, Feasts
from django.conf import settings
import pandas as pd


def run():
    """
    Main function of script load_csv.py that loads data from csv files (merged, filtered) to django database
    """
    # CSV ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Get dataframes ready
    antiphones = pd.read_csv('all-ci-antiphons.csv', usecols=['cantus_id', 'feast_id', 'drupal_path'])  # converters={'cantus_id' : str})
    responsories = pd.read_csv('all-ci-responsories.csv', usecols=['cantus_id', 'feast_id', 'drupal_path'])
    sources = pd.read_csv('sources-of-all-ci-antiphones.csv', usecols=['title', 'siglum', 'provenance_id', 'century', 'drupal_path'])
    geography = pd.read_csv('provenances_data.csv', usecols=['provenance_id', 'provenance', 'latitude', 'longitude'])
    feasts = pd.read_csv('feast.csv', usecols=['id', 'name', 'feast_code'])

    # Merge antiphons and responsories
    chant_data = pd.concat([antiphones, responsories])
    
    # Filter sources to use only those with more than 100 chants
    freq_of_sources = chant_data['drupal_path'].value_counts()
    bigger_sources = freq_of_sources.drop(freq_of_sources[freq_of_sources.values < 100].index).index.tolist()
    sources_f = sources[sources['drupal_path'].isin(bigger_sources)]

    # Filter feasts to use onlz those used in filtered sources
    freq_of_feasts = chant_data['feast_id'].value_counts()
    print("number of all feasts in bigger sources:", len(freq_of_feasts))
    bigger_feasts = freq_of_feasts.drop(freq_of_feasts[freq_of_feasts.values < 10].index).index.tolist()
    print("number of all bigger feasts in bigger sources:", len(bigger_sources))
    feasts_f = feasts[feasts['id'].isin(bigger_feasts)]

    # Filter chants based on filtered sources
    chant_data_f = chant_data[chant_data['drupal_path'].isin(sources_f['drupal_path'])]


    # Database ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Get ready databases
    Data_Chant.objects.all().delete()
    Sources.objects.all().delete()
    Geography.objects.all().delete()
    Feasts.objects.all().delete()

    # Fill Chant info
    row_iter = chant_data_f.iterrows()
    objs = [
        Data_Chant( 
            cantus_id=row['cantus_id'],
            feast_id=row['feast_id'],
            source_id=row['drupal_path']
        )
        for index, row in row_iter
    ]
    Data_Chant.objects.bulk_create(objs)

    # Fill Sources info
    row_iter = sources_f.iterrows()
    objs = [
        Sources(
            title=row['title'],
            provenance_id=row['provenance_id'],
            century=row['century'],
            siglum=row['siglum'],
            drupal_path=row['drupal_path']
        )
        for index, row in row_iter
    ]
    Sources.objects.bulk_create(objs)

    # Fill Geography info
    row_iter = geography.iterrows()
    objs = [
        Geography(
            provenance_id=row['provenance_id'],
            provenance=row['provenance'],
            latitude=row['latitude'],
            longitude=row['longitude']
        )
        for index, row in row_iter
    ]
    Geography.objects.bulk_create(objs)

    # Fill Feasts info
    row_iter = geography.iterrows()
    objs = [
        Feasts(
            feast_id=row['id'],
            name=row['name'],
            feast_code=row['feast_code']
        )
        for index, row in row_iter
    ]
    Feasts.objects.bulk_create(objs)