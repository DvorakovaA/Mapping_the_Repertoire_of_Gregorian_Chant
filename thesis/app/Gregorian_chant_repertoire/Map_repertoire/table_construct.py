'''
File providing function to construct result table of already found source communities 
Results table on tool page then contains info about particular chants for each community and each office
It is constructed as dictionary of three parts
    - head - header of table - CommunityXY and number of sources in it with certain colour background
           - list of dicts
    - body - offices as rows - chants ordered by frequnecy in particular community (column)
           - complicated dictionary structure of rows (by office)
    - tail - drupal path and siglum of sources in community
           - list of lists of dicts
'''

from matplotlib.colors import TwoSlopeNorm, rgb2hex
import matplotlib.pyplot as plt
from collections import Counter

from .models import Sources, Data_Chant



def get_table_data(communities : list[set [str]], feast_codes : list[str], filtering_office : list[str], datasets : list[str]) -> dict:
    '''
    Function that constructs data structure readable for django templating language,
    so it is possible to present results of community search for some feast(s) in table
    Structure of tab_data:
    {
        'head': [{'com':'CommunityX, 'sources':'XY sources','color':'hex'}, {}, ...],
        'body': {'OFFICE_CODE_V': [{'collapsed':[{'incipit':'Text','cantus_id':'XXXXXX','freq':X}, {}, ...],'uncollapsed':[{'incipit':,...}, ...]}],
                 'OFFICE_CODE_C': [{...}, {...}, ...], 'OFFICE_CODE_M':[{...}], ...}
        'tail': [[{'source_id':'https//..', 'siglum':'XY'}, {}, ...], [{}, {}, ...], [{}]]
    }
    '''
    OFFICES = ['V','C', 'M', 'L', 'P', 'T', 'S', 'N',  'V2', 'D', 'R',  'E',  'H', 'CA', 'X', 'UNKNOWN']
    

    if communities != []:
        # Get ready the base of returned structure
        tab_data = {}
        tab_data['head'] = []
        tab_data['body'] = {}
        tab_data['tail'] = []
        
        # Color scale for header fields of table (same as in map_construct)
        cmap = plt.get_cmap('plasma')
        offset = TwoSlopeNorm(vmin = 0, vcenter= (len(communities) / 2), vmax = len(communities))
        colors = []
        for b in range(len(communities)):
            scale = offset(b)
            color=rgb2hex(cmap(scale)) # without translation to hex it is blue - green scale
            colors.append(color)

        # Get head part, tail part and collect chants and offices
        chants_of_community = {}
        used_offices = []
        i = 0  # number for assignement to each community in header and for indexing in construction
        for community in communities:
            # Head part
            tab_data['head'].append({'com' : "Community "+str(i+1), 'sources' : str(len(community))+" sources", 'color' : colors[i]})
            
            # Tail part
            tab_data['tail'].append([])
            for source_id in community:
                tab_data['tail'][i].append({'source_id' : source_id, 'siglum' : Sources.objects.filter(drupal_path = source_id).values_list('siglum')[0][0]})
            # Sort sources based on siglum to nicer display in table tail
            tab_data['tail'][i].sort(key=lambda x : x['siglum'])

            # Collecting part
            chants_of_community[i] = []
            # All feasts
            if feast_codes == ['All']:
                chants_of_community[i] = []
                for source_id in community:
                    # Check for duplicates of CIDs within one source
                    chants_of_source_dict = {}
                    for dataset in datasets:
                        for chant in Data_Chant.objects.filter(source_id=source_id, dataset=dataset).values():
                            chants_of_source_dict[(chant['office_id'], chant['cantus_id'])] = chant['incipit']
                        used_offices += list(Data_Chant.objects.filter(source_id=source_id, dataset=dataset).values_list('office_id', flat=True))
                    # 
                    chants_of_source = [(key[0], key[1], chants_of_source_dict[key]) for key in chants_of_source_dict]
                    chants_of_community[i] += chants_of_source
                
            else: # Not all feasts
                chants_of_feasts = []
                for feast_code in feast_codes:
                        chants_of_feasts = []
                        for dataset in datasets:
                            chants_of_feasts += Data_Chant.objects.filter(feast_code=feast_code, dataset=dataset).values()
                        used_offices += [chant['office_id'] for chant in chants_of_feasts]
                        for source_id in community:
                            # Check for duplicates of CIDs within one table cell
                            chants_of_source_dict = {}
                            for chant in chants_of_feasts:
                                if chant['source_id'] == source_id:
                                    chants_of_source_dict[(chant['office_id'], chant['cantus_id'])] = chant['incipit']
                            chants_of_source = [(key[0], key[1], chants_of_source_dict[key]) for key in chants_of_source_dict]
                            chants_of_community[i] += chants_of_source
            i += 1
        used_offices = set(used_offices)

        # Fill body
        # Check for possible filter
        if filtering_office == []:
            filtering_office = OFFICES
        # Go over data in office point of view (= rows)
        for office in filtering_office:
            # Check for empty rows (empty offices)
            if office in used_offices:
                for i in range(len(communities)):
                    # Get info into better structure for computation and display
                    community_office_chants_dict = {}
                    community_office_chants = []
                    for chant in chants_of_community[i]: # chant = (office, cantus, incipit)
                        if chant[0] == office:
                            community_office_chants_dict[chant[1]] = chant[2]  #cantus_id -> incipit 
                            community_office_chants.append(chant[1])
                    # Frequency count
                    frequency = Counter(chant for chant in community_office_chants)
                    ordered_freq = [k for k in frequency.most_common()]
                    uncollapsed_chant_info = []
                    # Take six most frequent chants for being uncollapsed
                    j = 0
                    while j < 6:
                        try:
                            uncollapsed_chant_info.append({'incipit' : community_office_chants_dict[ordered_freq[j][0]], 'cantus_id' : ordered_freq[j][0], 'freq' : "("+str(ordered_freq[j][1])+" | "+str(round((ordered_freq[j][1]/len(communities[i]))*100, 2))+" %)"})
                        except:
                            break
                        j+=1
                    
                    collapsed_chant_info = []
                    # Take potencial rest of chants
                    for j in range(j, len(ordered_freq)):
                        collapsed_chant_info.append({'incipit' : community_office_chants_dict[ordered_freq[j][0]], 'cantus_id' : ordered_freq[j][0], 'freq' : "("+str(ordered_freq[j][1])+" | "+str(round((ordered_freq[j][1]/len(communities[i]))*100, 2))+" %)"})

                    try:
                        tab_data['body'][office].append({'uncollapsed': uncollapsed_chant_info, 'collapsed' : collapsed_chant_info})
                    except:
                        tab_data['body'][office] = [{'uncollapsed': uncollapsed_chant_info, 'collapsed' : collapsed_chant_info}]

        return tab_data
    
    # Nothing to be displayed
    return None