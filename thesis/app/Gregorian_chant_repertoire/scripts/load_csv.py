"""
Python script that loads data from csv files (from folder data) to django database
Data_Chant - all_ci_antiphons.csv, all_ci_responsories.csv
Sources - sources-with-provenance-ids-and-two-centuries.csv
Geography - geography_data.csv
Feasts - feast.csv

To Data_Chant and Sources it adds info about being CI_base dataset from admin

Loads only chants from surces where we have more than 100 chants from that source
and belongig to feast where there are more than 5 chants for it
"""

from Map_repertoire.models import Data_Chant, Sources, Geography, Feasts

from django.db.models import Q
import pandas as pd

OFFICES = {'office_v' : 'V', 'office_c' : 'C', 'office_m' : 'M', 'office_l' : 'L', 'office_p' : 'P', 'office_t' :'T', 'office_s' :'S', 
                'office_n' : 'N', 'office_v2' :'V2', 'office_d' :'D', 'office_r' :'R', 'office_e' : 'E', 'office_h' : 'H', 'office_ca' : 'CA', 
                'office_x' : 'X', 'unknown' : 'UNKNOWN'}

def run():
    """
    Main function of script load_csv.py that gets data from csv files (merged, filtered) via pandas library 
    and loads it to modules of prepared django database 
    """
    # CSV ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Get dataframes ready
    antiphons = pd.read_csv('data/generated/all-ci-antiphons_feast_codes.csv', usecols=['cantus_id', 'feast_code', 'source_id', 'office_id', 'incipit'])
    responsories = pd.read_csv('data/generated/all-ci-responsories_feast_codes.csv', usecols=['cantus_id', 'feast_code', 'source_id', 'office_id', 'incipit'])
    bigger_sources = pd.read_csv('data/generated/sources-with-provenance-ids-and-two-centuries.csv', usecols=['title', 'siglum', 'century', 'num_century', 'provenance_id', 'provenance', 'drupal_path', 'cursus'])
    geography = pd.read_csv('data/given/geography_data.csv', usecols=['provenance_id', 'provenance', 'latitude', 'longitude'])
    feasts = pd.read_csv('data/given/feast.csv', usecols=['id', 'name', 'feast_code'])

    # Merge antiphons and responsories
    chant_data = pd.concat([antiphons, responsories])

    # Filter feasts to use only those having more than 5 chants 
    freq_of_feasts = chant_data['feast_code'].value_counts()
    bigger_feasts = freq_of_feasts.drop(freq_of_feasts[freq_of_feasts.values < 5].index).index.tolist()
    feasts_without_fragments = feasts[feasts['feast_code'].isin(bigger_feasts)]

    # Filter chants based on being in bigger sources and bigger feasts
    chant_data_filtered = chant_data[chant_data['source_id'].isin(bigger_sources['drupal_path']) & chant_data['feast_code'].isin(feasts_without_fragments['feast_code'])]
    # Fill in missing values
    chant_data_filtered['office_id'].fillna('unknown', inplace=True)

    # Database ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Get ready databases - delete old CI_base records and all Feast and Geography
    CI_base = Q(dataset="admin_CI_base")
    Data_Chant.objects.filter(CI_base).delete()
    Sources.objects.filter(CI_base).delete()

    Geography.objects.all().delete()
    Feasts.objects.all().delete()

    
    # Fill Chant info
    row_iter = chant_data_filtered.iterrows()
    objs = []
    for index, row in row_iter:
        try:
            objs.append(
                Data_Chant( 
                    cantus_id=row['cantus_id'],
                    feast_code=row['feast_code'],
                    source_id=row['source_id'],
                    office_id=OFFICES[row['office_id']],
                    incipit=row['incipit'],
                    dataset="admin_CI_base",
                ))
        except:
            objs.append(
                Data_Chant( 
                    cantus_id=row['cantus_id'],
                    feast_code=row['feast_code'],
                    source_id=row['source_id'],
                    office_id='UNKNOWN',
                    incipit=row['incipit'],
                    dataset="admin_CI_base",
                ))

    Data_Chant.objects.bulk_create(objs)

    # Fill Sources info
    row_iter = bigger_sources.iterrows()
    objs = [
        Sources(
            title=row['title'],
            provenance_id=row['provenance_id'],
            century=row['century'],
            num_century=row['num_century'],
            siglum=row['siglum'],
            provenance=row['provenance'],
            drupal_path=row['drupal_path'],
            cursus=row['cursus'],
            dataset="admin_CI_base"
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
    row_iter = feasts_without_fragments.iterrows()
    objs = [
        Feasts(
            feast_code=row['feast_code'],
            name=row['name']
        )
        for index, row in row_iter
    ]
    Feasts.objects.bulk_create(objs)
