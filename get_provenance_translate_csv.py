import pandas as pd

geography = pd.read_csv('geography_data.csv')

translate_pair = []
for index, row in geography.iterrows():
        translate_pair.append({
              'provenance' : row['provenance'],
              'provenance_id' : row['provenance_id']
        })

new_csv = pd.DataFrame.from_dict(translate_pair)
new_csv.to_csv('provenance_ids.csv')