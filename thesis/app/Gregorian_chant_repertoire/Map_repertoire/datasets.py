"""
File with 
* function check_chants_validity() that checks validity of users chants file 
  and returns possible missing sources and error text
* function check_sources_validity() that for given sources files checks its validity
  and for given missing sources that it completes situation
* function integrate_chants_file() that ensures new sources and given chants are 
  uploaded into DB
* functions that covers safe updates of geography data in DB
"""

import pandas as pd
import numpy as np
import regex as re
import functools

from django.db.models import Q
from .models import Sources, Datasets, Data_Chant, Feasts

MANDATORY_CHANTS_FIELDS = ['cantus_id', 'source_id', 'feast_code', 'incipit']
OPTIONAL_CHANTS_FIELDS = ['office_id']
MANDATORY_SOURCES_FIELDS = ['source_id', 'siglum']
OPTIONAL_SOURCES_FIELDS = ['century', 'provenance']

OFFICES = ['V','C', 'M', 'L', 'P', 'T', 'S', 'N',  'V2', 'D', 'R',  'E',  'H', 'CA', 'X', 'UNKNOWN']


def correct_dataset_name(name : str, user : str) -> bool:
    """
    Checks if dataset name is new to such user
    """
    if not Datasets.objects.filter(dataset_id=user+"_"+name).exists():
        # not duplicity
        return True
    
    return False


def check_complete_chants_columns(new_chants):
    """
    Function that checks if all mandatory columns of user dataset are present
    and that they contain all values
    """
    user_columns = set(new_chants.columns)
    for mand_column in MANDATORY_CHANTS_FIELDS:
        if mand_column not in user_columns or (mand_column in new_chants.columns[new_chants.isna().any()].tolist()):
            return False, mand_column
    
    return True, ""


def check_files_validity(name : str, user : str, chants_file, sources_file) -> tuple[bool, str]:
    """
    Validity means:
    * different name than other datasets of such user
    * all mandatory fields present
    * all present sources known by database
    """
    if correct_dataset_name(name, user):
        try:
            new_chants = pd.read_csv(chants_file)
        except:
            return (False, "Something is wrong with your chants file. Check it with instructions in Help section please.")
        all_ch_columns, missing_ch = check_complete_chants_columns(new_chants)
        if all_ch_columns:
            # check if all sources are known
            unknown_sources = []
            if sources_file is None:
                for source_id in set(new_chants['source_id'].to_list()):
                    if not Sources.objects.filter(drupal_path=source_id).exists():
                        unknown_sources.append(source_id)
            
            else:
                try:
                    sources_file.seek(0) # otherwise Empty columns error...
                    new_sources = pd.read_csv(sources_file)
                except:
                    return (False, "Something is wrong with your sources file. Check it with instructions in Help section please.")
                
                all_s_columns, missing_s = check_sources_validity(new_sources)
                if all_s_columns:
                    for source_id in set(new_chants['source_id'].to_list()):
                        if not Sources.objects.filter(drupal_path=source_id).exists() and not source_id in new_sources['source_id'].tolist():
                            unknown_sources.append(source_id)
                else:
                    return (False, "Mandatory column " + missing_s + " (or value in such column) of your sources file is missing. Check what is mandatory in Help section.")

            if unknown_sources == []:
                return (True, "")
            else:
                error_m = "Unknown sources. Please upload source file with these sources: \n"
                for source in unknown_sources:
                    error_m += source+"\n"
                error_m += " Please upload both files again."
                return (False, error_m)
        else:
            return (False, "Mandatory column "+ missing_ch +" (or value in such column) of your dataset is missing. Check what is mandatory in Help section.")
    else:
        return (False, "Add new dataset name. " + name + " is already present in your datasets.")



def check_sources_validity(new_sources):
    """
    Checks if all mandatory columns are present
    """
    user_columns = set(new_sources.columns)
    for mand_column in MANDATORY_SOURCES_FIELDS:
        if mand_column not in user_columns or mand_column in new_sources.columns[new_sources.isna().any()].tolist():
            return False, mand_column

    return True, ""


def add_dataset_record(name : str, user : str, visibility : str):
    """
    Creates complete record in Datasets
    """
    id = user+"_"+name
    new_entry = Datasets()
    new_entry.dataset_id = id
    new_entry.name = name
    new_entry.owner = user
    if visibility == 'private':
        new_entry.public = False
    else: # public dataset
        new_entry.public = True
    new_entry.save()


def integrate_chants_file(name : str, user : str, chants_file, sources_file, visibility : str) -> tuple[list[str], list[str]]:
    """
    Add new record of dataset to Datasets
    Add new chants to Data_Chants
    Add possible new sources to Sources
    (Both files validity should be checked already! Mandatory fields are complete)
    Also returns unknown values for feasts and office_ids and unmatched or unknown provenances
    """
    unknown_values = []

    # New dataset record
    add_dataset_record(name, user, visibility)

    #~ New sources ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if sources_file is not None:
        sources_file.seek(0)
        new_sources = pd.read_csv(sources_file)

        # fill for empty optional values - possibly create new unknown columns
        if 'century' in new_sources.columns:
            new_sources['century'].fillna('unknown', inplace=True)
        else:
            new_sources.insert(1, 'century', 'unknown')
        if 'provenance' in new_sources.columns:
            new_sources['provenance'].fillna('unknown', inplace=True)
        else:
            new_sources.insert(1, 'provenance', 'unknown')

        # create num_century
        numerical_century = []
        for cent in new_sources['century'].to_numpy():
            if cent[0:2].isnumeric():
                if cent[2].isnumeric():
                    numerical_century.append(str(int(cent[0:2])+1))
                else:
                    numerical_century.append(cent[0:2])
            else:
                numerical_century.append('unknown')
                if cent != 'unknown':
                    unknown_values.append(cent)

        new_sources.insert(1, 'num_century', numerical_century, allow_duplicates=True)
        
        # try to match provenance to provenance_id
        new_sources['provenance_id'] = ""
        for index, row in new_sources.iterrows():
            if Sources.objects.filter(provenance=row['provenance']).exists():
                new_sources.at[index, 'provenance_id'] = Sources.objects.filter(provenance=row['provenance']).values_list('provenance_id')[0]
            else:
                print("does not exist provenance in sources")
                new_sources.at[index, 'provenance_id'] = "unknown"

        # add or fill title column with siglum...
        if 'title' not in new_sources.columns:
            new_sources['title'] = ""
        new_sources['title'] = np.where(new_sources['title'] == "", new_sources['siglum'], new_sources['title'])
        new_sources['title'].fillna(new_sources.siglum, inplace=True)

        # add or fill cursus
        if 'cursus' not in new_sources.columns:
            new_sources['cursus'] = ""
        new_sources['cursus'].replace(to_replace="", value="Unknown", inplace=True)
        new_sources['cursus'].fillna("Unknown", inplace=True)

        # Fill DB
        known_sources = Sources.objects.values_list('drupal_path', flat=True)
        row_iter = new_sources.iterrows()
        objs = []
        for index, row in row_iter:
            if row['source_id'] not in known_sources: # First entry of source is authoritative
                objs.append(Sources(
                    title=row['title'],
                    provenance_id=row['provenance_id'],
                    century=row['century'],
                    num_century=row['num_century'],
                    siglum=row['siglum'],
                    provenance=row['provenance'],
                    drupal_path=row['source_id'],
                    cursus=row['cursus'],
                    dataset=user+"_"+name
                ))
        
        Sources.objects.bulk_create(objs)


    #~ New chants ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    chants_file.seek(0)
    new_chants = pd.read_csv(chants_file, dtype={'feast_code' : str})
    # check if office_id column is present
    if 'office_id' not in new_chants.columns:
        new_chants.insert(4, "office_id", 'UNKNOWN', allow_duplicates=True)

    # possibly fill office_id by value expected in table_construct
    new_chants['office_id'].fillna('UNKNOWN', inplace=True)
    
    # Fill DB
    feast_codes = list(Feasts.objects.all().values_list('feast_code', flat=True))
    row_iter = new_chants.iterrows()
    objs = []
    for index, row in row_iter:
        # Catch bad office_ids
        if row['office_id'] in OFFICES:
            office_id = row['office_id']
        else:
            office_id = 'UNKNOWN'
            unknown_values.append(row['office_id'])
        # Catch bad feast_codes
        if row['feast_code'] in feast_codes:
            feast_code = row['feast_code']
        else:
            feast_code = 'unknown'
            unknown_values.append(row['feast_code'])
        # Save for upload
        objs.append(Data_Chant(
            cantus_id=row['cantus_id'],
            feast_code=feast_code,
            source_id=row['source_id'],
            office_id=office_id,
            incipit=row['incipit'],
            dataset=user+"_"+name,
        ))

    Data_Chant.objects.bulk_create(objs)

    # Check unmatched provenances
    unmatched_provenances = []
    used_sources = list(Data_Chant.objects.filter(dataset=user+"_"+name).values_list('source_id', flat=True))
    for source_id in used_sources:
        s_info = Sources.objects.filter(drupal_path=source_id).values()[0]
        if s_info['provenance_id'] == 'unknown':
            unmatched_provenances.append(s_info['provenance'])

    return list(set(unknown_values)), list(set(unmatched_provenances))


def delete_dataset(dataset_id : str):
    """
    Delete record from Datasets
    Delete all records from Data_Chants
    Delete all (possible) records from Sources
    """
    Datasets.objects.filter(dataset_id=dataset_id).delete()
    Data_Chant.objects.filter(dataset=dataset_id).delete()
    Sources.objects.filter(dataset=dataset_id).delete()



# ~ GEOGRAPHY RELATED STUFF ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@functools.lru_cache(maxsize=None)
def levenstein(a : str, b : str) -> float:
    """
    Calculates Levenstein distance between strings a and b 
    while leaving out non letters
    """
    a = "".join(re.split("[^a-z]*", a.lower()))
    b = "".join(re.split("[^a-z]*", b.lower()))
    top_dists = range(len(b) + 1)
    for ind_a, char_a in enumerate(a):
        next_dists = [ind_a + 1]
        for ind_b, char_b in enumerate(b):
            next_dists.append(top_dists[ind_b] if char_a == char_b
                              else min(top_dists[ind_b],
                                       top_dists[ind_b + 1],
                                       next_dists[-1]) + 1)
        top_dists = next_dists
    return top_dists[-1]



def get_provenance_sugestions(provenance : str) -> list[str]:
    """
    For name of provenace returns possible variants from those already
    present in database
    """
    distances = {}
    for source in Sources.objects.filter(~Q(provenance_id='unknown')).values():
        distances[source['provenance']] = levenstein(source['provenance'], provenance)
    return dict(sorted(distances.items(), key=lambda x:x[1], reverse=False)).keys()



def get_reachable_sources(user : str):
    """
    Collects what sources content user can reach and returns such sources IDs
    """
    his_and_public_sets = Datasets.objects.filter(Q(owner=user) | Q(public=True)).values_list('dataset_id', flat=True)
    his_and_public_data = Sources.objects.filter(dataset__in=his_and_public_sets).values_list('drupal_path', flat=True)
    ci_base = Sources.objects.filter(dataset="admin_CI_base").values_list('drupal_path', flat=True)

    return list(set(list(his_and_public_data) + list(ci_base)))



def get_unknown_provenances(user : str) -> list[str]:
    """
    Returns list of all provenances in database that are not matched
    with existing provenance_id
    """
    unknown_provenances = []
    reachable_sources = get_reachable_sources(user)
    for source in Sources.objects.filter(Q(provenance_id='unknown') & Q(drupal_path__in=reachable_sources)).values():
        unknown_provenances.append(source['provenance'])

    return list(set(unknown_provenances).difference({'unknown'}))



def add_new_coordinates(provenance : str, lat : str, long : str):
    """
    Function upload new record to Geography 
    (provenance, latitude and longitude are given, new provenance_id is generated)
    Then updates Sources where there is similar porvenance for source
    """
    pass



def add_matched_provenance(new_prov : str, existing_prov : str):
    """
    
    """
    pass