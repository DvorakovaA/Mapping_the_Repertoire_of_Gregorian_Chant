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
    Main function of script load_csv.py that gets data from csv files (merged, filtered) via pandas library 
    and loads it to django database 
    """
    # CSV ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Get dataframes ready
    antiphons = pd.read_csv('all-ci-antiphons.csv', usecols=['cantus_id', 'feast_id', 'source_id', 'office_id'])  # converters={'cantus_id' : str})
    responsories = pd.read_csv('all-ci-responsories.csv', usecols=['cantus_id', 'feast_id', 'source_id', 'office_id'])
    sources = pd.read_csv('sources-with-provenance-ids-and-two-centuries.csv', usecols=['title', 'siglum', 'century', 'num_century', 'provenance_id', 'drupal_path'])
    geography = pd.read_csv('geography_data.csv', usecols=['provenance_id', 'provenance', 'latitude', 'longitude'])
    feasts = pd.read_csv('feast.csv', usecols=['id', 'name', 'feast_code'])

    # Merge antiphons and responsories
    chant_data = pd.concat([antiphons, responsories])
    
    # Filter sources to use only those with more than 100 chants
    freq_of_sources = chant_data['source_id'].value_counts()
    bigger_sources = freq_of_sources.drop(freq_of_sources[freq_of_sources.values < 100].index).index.tolist()
    sources_f = sources[sources['drupal_path'].isin(bigger_sources)]

    # Filter feasts to use only those used in filtered sources
    freq_of_feasts = chant_data['feast_id'].value_counts()
    bigger_feasts = freq_of_feasts.drop(freq_of_feasts[freq_of_feasts.values < 10].index).index.tolist()
    feasts_f = feasts[feasts['id'].isin(bigger_feasts)]

    # Filter chants based on filtered sources
    chant_data_f = chant_data[chant_data['source_id'].isin(sources_f['drupal_path'])]


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
            source_id=row['source_id'],
            office_id=row['office_id']
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
            num_century=row['num_century'],
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
    row_iter = feasts_f.iterrows()
    objs = [
        Feasts(
            feast_id=row['id'],
            name=row['name'],
            feast_code=row['feast_code']
        )
        for index, row in row_iter
    ]
    Feasts.objects.bulk_create(objs)

    print('Feast', len(Feasts.objects.all()), len(feasts_f))
    print('Chant', len(Data_Chant.objects.all()), len(chant_data_f))
    print('Source', len(Sources.objects.all()), len(sources_f))
    print('Geo', len(Geography.objects.all()))