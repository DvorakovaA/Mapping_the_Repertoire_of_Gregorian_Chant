"""
File with 
* function check_chants_validity() that checks validity of users chants file 
  and returns possible missing sources and error text
* function check_sources_validity() that for given sources files checks its validity
  and for given missing sources that it completes situation
* function integrate_chants_file() that 
"""

import pandas as pd
import numpy as np

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


def add_dataset_record(name : str, user : str):
    """
    Creates complete record in Datasets
    """
    id = user+"_"+name
    new_entry = Datasets()
    new_entry.dataset_id = id
    new_entry.name = name
    new_entry.owner = user
    new_entry.save()


def integrate_chants_file(name : str, user : str, chants_file, sources_file):
    """
    Add new record of dataset to Datasets
    Add new chants to Data_Chants
    Add possible new sources to Sources
    (Both files validity should be checked already! Mandatory fields are complete)
    """
    # New dataset record
    add_dataset_record(name, user)

    #~ New chants ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    chants_file.seek(0)
    new_chants = pd.read_csv(chants_file)
    # check if office_id column is present
    if 'office_id' not in new_chants.columns:
        new_chants.insert(4, "office_id", 'UNKNOWN', allow_duplicates=True)

    # possibly fill office_id by value expected in table_construct
    new_chants['office_id'].fillna('UNKNOWN', inplace=True)
    
    # Fill DB
    row_iter = new_chants.iterrows()
    objs = []
    for index, row in row_iter:
        if row['office_id'] in OFFICES:
            office_id = row['office_id']
        else:
            office_id = 'UNKNOWN'
        objs.append(Data_Chant(
            cantus_id=row['cantus_id'],
            #feast_id=Feasts.objects.filter(feast_code=row['feast_id']).values_list('feast_id')[0],
            feast_id=row['feast_code'],
            source_id=row['source_id'],
            office_id=office_id,
            incipit=row['incipit'],
            dataset=user+"_"+name,
        ))
    #objs = [
    #    Data_Chant( 
    #        cantus_id=row['cantus_id'],
    #        #feast_id=Feasts.objects.filter(feast_code=row['feast_id']).values_list('feast_id')[0],
    #        feast_id=row['feast_code'],
    #        source_id=row['source_id'],
    #        office_id=row['office_id'],
    #       incipit=row['incipit'],
    #        dataset=user+"_"+name,
    #   )
    #   for index, row in row_iter
    #]
    Data_Chant.objects.bulk_create(objs)

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

        new_sources.insert(1, 'num_century', numerical_century, allow_duplicates=True)

        # try to match provenance to provenance_id
        new_sources.insert(1,'provenance_id',"")
        for index, row in new_sources.iterrows():
            if Sources.objects.filter(provenance=row['provenance']).exists():
                row['provenance_id'] = Sources.objects.filter(provenance=row['provenance']).values_list('provenance_id')[0]
        
        # add or fill title column with siglum...
        if 'title' not in new_sources.columns:
            new_sources['title'] = np.nan
        new_sources['title'].fillna(new_sources['siglum'], inplace=True)

        # add or fill cursus
        if 'cursus' not in new_sources.columns:
            new_sources['cursus'] = np.nan
        new_sources['cursus'].fillna("Unknown", inplace=True)

        # Fill DB
        row_iter = new_sources.iterrows()
        objs = [
            Sources(
                title=row['title'],
                provenance_id=row['provenance_id'],
                century=row['century'],
                num_century=row['num_century'],
                siglum=row['siglum'],
                provenance=row['provenance'],
                drupal_path=row['source_id'],
                cursus=row['cursus'],
                dataset=user+"_"+name
            )
            for index, row in row_iter
        ]
        Sources.objects.bulk_create(objs)




def delete_dataset(dataset_id: str):
    """
    Delete record from Datasets
    Delete all records from Data_Chants
    Delete all (possible) records from Sources
    """
    Datasets.objects.filter(dataset_id=dataset_id).delete()
    Data_Chant.objects.filter(dataset=dataset_id).delete()
    Sources.objects.filter(dataset=dataset_id).delete()

