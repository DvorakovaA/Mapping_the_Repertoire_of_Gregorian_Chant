"""
Script that process desired changes in csvs:
- add provenance_id into source file (-> sources-with-provenance-ids.csv)
- add new century column into source file that can be used for century groups in map (leave only number) 
- check if there are any new uknown provenances in given data (not existing in geography_data.csv)
  and tell user via console (plus suggest new unused provenance_ids)
"""
import pandas as pd

def run():
    geography = pd.read_csv('data/given/geography_data.csv')
    sources_without = pd.read_csv('data/given/sources-of-all-ci-antiphons.csv')

    antiphons = pd.read_csv('data/given/all-ci-antiphons.csv')
    responsories = pd.read_csv('data/given/all-ci-responsories.csv')
    chant_data = pd.concat([antiphons, responsories])

    freq_of_sources = chant_data['source_id'].value_counts()
    bigger_sources = freq_of_sources.drop(freq_of_sources[freq_of_sources.values < 100].index).index.tolist()
    sources_without_f = sources_without[sources_without['drupal_path'].isin(bigger_sources)]

    # Add provenance_id to sources file and save uknown
    sources_with = []
    unknown_provenances = []
    for index, row in sources_without_f.iterrows():
        try:
            filt_prov = geography['provenance'] == row['provenance']
            geo = (geography[filt_prov]['provenance_id']).to_list()
            sources_with.append({
                'drupal_path' : row['drupal_path'],
                'title' : row['title'],
                'siglum' : row['siglum'],
                'century' : row['century'],
                'provenance_id' : geo[0]
            })
        except:
            sources_with.append({
                'drupal_path' : row['drupal_path'],
                'title' : row['title'],
                'siglum' : row['siglum'],
                'century' : row['century']
            })
            unknown_provenances.append(row['provenance'].strip())


    new_csv = pd.DataFrame.from_dict(sources_with)

    # Add new numeric century column to sources file
    numerical_century = []
    old_century = new_csv['century'].to_numpy()

    for cent in old_century:
        if '9th century' == cent or '09th century' == cent:
            numerical_century.append(9)
        elif ' c. 1200' == cent or 'c. 1200' == cent:
            numerical_century.append(13)
        elif 'mid 14th century' == cent:
            numerical_century.append(14)
        elif cent[0:2].isnumeric():
            numerical_century.append(int(cent[0:2]))


    # Edited file with new columns
    new_csv.insert(4, "num_century", numerical_century, allow_duplicates=True)
    new_csv.to_csv('data/generated/sources-with-provenance-ids-and-two-centuries.csv')


    # Back to unknown provenances 
    unknown_provenances = set(unknown_provenances)
    print('Unknown provenances found:', len(unknown_provenances))
    last_suggested_id = max(geography['provenance_id'].to_list())
    #print(sorted(geography['provenance_id'].to_list()))
    for new in unknown_provenances:
        new_id = "provenance_" + str(int(last_suggested_id[-3:]) + 1)
        last_suggested_id = new_id
        print(new, '\n Suggested new provenance_id:', new_id, '\n')
    
