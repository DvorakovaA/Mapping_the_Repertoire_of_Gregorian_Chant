"""
Script that process desired changes in csvs:
- add provenance_id into source file (-> sources-with-provenance-ids.csv)
- add new century column into source file that can be used for century groups in map (leave only number) 
"""
import pandas as pd

geography = pd.read_csv('geography_data.csv')
sources_old = pd.read_csv('sources-of-almost-all-ci-antiphons.csv')

antiphons = pd.read_csv('all-ci-antiphons.csv')
responsories = pd.read_csv('all-ci-responsories.csv')
chant_data = pd.concat([antiphons, responsories])

freq_of_sources = chant_data['source_id'].value_counts()
bigger_sources = freq_of_sources.drop(freq_of_sources[freq_of_sources.values < 100].index).index.tolist()
sources_old_f = sources_old[sources_old['drupal_path'].isin(bigger_sources)]


#sources_new = pd.DataFrame(columns=['drupal_path', 'title', 'siglum', 'century', 'provenance'])
sources_new = []

for index, row in sources_old_f.iterrows():
    #geo = geography['provenance' == row['provenance']] #['provenance_id']
    try:
        filt_prov = geography['provenance'] == row['provenance']
        geo = (geography[filt_prov]['provenance_id']).to_list()
        #geo = geography['provenance' == row['provenance']] #['provenance_id']
        sources_new.append({
            'drupal_path' : row['drupal_path'],
            'title' : row['title'],
            'siglum' : row['siglum'],
            'century' : row['century'],
            'provenance_id' : geo[0]
        })
    except:
        sources_new.append({
            'drupal_path' : row['drupal_path'],
            'title' : row['title'],
            'siglum' : row['siglum'],
            'century' : row['century']
        })


new_csv = pd.DataFrame.from_dict(sources_new)
new_csv.to_csv('sources-with-provenance-ids.csv')

new_century = []
old_century = new_csv['century'].to_numpy()

for cent in old_century:
    if '9th century' == cent or '09th century' == cent:
        new_century.append(9)
    elif ' c. 1200' == cent or 'c. 1200' == cent:
        new_century.append(13)
    elif 'mid 14th century' == cent:
        new_century.append(14)
    else:
        new_century.append(int(cent[0:2]))



new_csv.insert(4, "num_century", new_century, allow_duplicates=True)
new_csv.to_csv('sources-with-provenance-ids-and-two-centuries.csv')
