"""
Script that process desired changes in csvs:
- add provenance_id into source file (based on provenance_ids.csv)
- add new century column into source file that can be used for century groups in map (leave only number)
- generate new csv file with only bigger sources (over 100 chants) and 
  with these additions (sources-with-provenance-ids-and-two-centuries.csv)
- check if there are any new uknown provenances in given data (not existing in provenance_ids.csv)
  and tell user via console (plus suggest new unused provenance_ids - might be problematic bs of users datasets!!!)
- enrich antiphons and responsories with feast_code (besides feast_id)
"""

import pandas as pd


def run():
    """ 
    Main function providing all data operations to create file
    sources-with-provenance-ids-and-two-centuries.csv with help of pandas library
    """
    # Read data
    provenance_ids = pd.read_csv('data/given/provenance_ids.csv')
    original_sources = pd.read_csv('data/given/sources-of-all-ci-antiphons_OPTIONAL-CENTURY.csv')

    antiphons = pd.read_csv('data/given/all-ci-antiphons.csv')
    responsories = pd.read_csv('data/given/all-ci-responsories.csv')
    chant_data = pd.concat([antiphons, responsories])

    feasts = pd.read_csv('data/given/feast.csv')

    # Filter sources to avoid working with fragments (to use only those with more than 100 chants)
    freq_of_sources = chant_data['source_id'].value_counts()
    bigger_sources = freq_of_sources.drop(freq_of_sources[freq_of_sources.values < 100].index).index.tolist()
    sources_without_fragments = original_sources[original_sources['drupal_path'].isin(bigger_sources)]

    # Change nan in provenance / cursus column to unknown
    sources_without_fragments['provenance'] = sources_without_fragments['provenance'].fillna('unknown')
    sources_without_fragments['cursus'] = sources_without_fragments['cursus'].fillna('Unknown')

    # Add provenance_id to sources file and collect unknown
    sources_with_new_info = []
    unknown_provenances = []
    for index, row in sources_without_fragments.iterrows():
        try:
            filt_prov = provenance_ids['provenance'] == row['provenance'].strip()
            prov_id = (provenance_ids[filt_prov]['provenance_id']).to_list()
            sources_with_new_info.append({
                'drupal_path' : row['drupal_path'],
                'title' : row['title'],
                'provenance' : row['provenance'],
                'siglum' : row['siglum'],
                'century' : row['century'],
                'cursus' : row['cursus'],
                'provenance_id' : prov_id[0]
            })
        except:
            sources_with_new_info.append({
                'drupal_path' : row['drupal_path'],
                'title' : row['title'],
                'provenance' : row['provenance'],
                'siglum' : row['siglum'],
                'cursus' : row['cursus'],
                'century' : row['century'],
                'provenance_id' : 'unknown'
            })
            unknown_provenances.append(row['provenance'].strip())


    new_csv = pd.DataFrame.from_dict(sources_with_new_info)
    
    # Change nan in century column to unknown
    new_csv['century'] = new_csv['century'].fillna('unknown')

    # Add new numeric century column to sources file
    numerical_century = []
    original_century = new_csv['century'].to_numpy()

    print("Unresolved centuries:")
    for cent in original_century:
        if '9th century' == cent or '09th century' == cent:
            numerical_century.append('9')
        elif ' c. 1200' == cent or 'c. 1200' == cent:
            numerical_century.append('13')
        elif 'mid 14th century' == cent:
            numerical_century.append('14')
        elif cent[0:2].isnumeric():
            if cent[2].isnumeric():
                numerical_century.append(str(int(cent[0:2])+1))
            else:
                numerical_century.append(cent[0:2])
        # Century unknown
        else:
            numerical_century.append('unknown')
    print()
    
    # Save edited file with two new columns and only big sources
    new_csv.insert(4, "num_century", numerical_century, allow_duplicates=True)
    new_csv.to_csv('data/generated/sources-with-provenance-ids-and-two-centuries.csv')


    # Inform about unknown provenances 
    unknown_provenances = set(unknown_provenances).difference({'unknown'})
    last_suggested_id = max(provenance_ids['provenance_id'].to_list())

    print("Unknown provenances:")
    print("(Be careful with using suggestions and first check state of app database Sources!)")
    for new in unknown_provenances:
        new_id = "provenance_" + str(int(last_suggested_id[-3:]) + 1)
        last_suggested_id = new_id
        print(new, '\n Suggested new provenance_id:', new_id, '\n')
    
    print('Unknown provenances found:', len(unknown_provenances))
    
    # Provide feast_code addition
    def get_feast_code(feast_id):
        try:
            feast_code = feasts[feasts['id'] == feast_id]['feast_code']
            return feast_code.item()
        except:
            return 'unknown'
        
    antiphons['feast_code'] = antiphons['feast_id'].apply(get_feast_code)
    antiphons.to_csv('data/generated/all-ci-antiphons_feast_codes.csv')
    
    responsories['feast_code'] = responsories['feast_id'].apply(get_feast_code)
    responsories.to_csv('data/generated/all-ci-responsories_feast_codes.csv')