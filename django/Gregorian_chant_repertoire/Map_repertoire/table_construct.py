'''
Script providing function to construct result table of source communities 
found by Louvein algorithm for community detection
Table on page then contains info about particular chants
It is constructed as dictionary of three parts
    - head - header of table - CommunityXY and number of sources in it
    - body - offices as rows - chants ordered by frequnecy in particular community (column)
    - tail - drupal path and siglum of sources in community
'''

from matplotlib.colors import TwoSlopeNorm, rgb2hex
import matplotlib.pyplot as plt
from collections import Counter

from .models import Sources, Data_Chant



def get_table(communities : list[set [str]], feast_ids : list[str], filtering_office : list[str]) -> dict:
    '''
    Function that constructs data structure readable for django templating language,
    so it is possible to present results of community search for some feast(s) in table
    '''
    if communities != []:
        tab_data = {}
        tab_data['head'] = []
        tab_data['tail'] = []
        tab_data['body'] = {}

        # Color scale for header fields of table
        cmap = plt.get_cmap('plasma')
        offset = TwoSlopeNorm(vmin = 0, vcenter= (len(communities) / 2), vmax = len(communities))
        colors = []
        for b in range(len(communities)):
            scale = offset(b)
            color=rgb2hex(cmap(scale)) # without translation to hex it is blue - green scale
            colors.append(color)

        chants_of_community = {}
        i = 0
        for community in communities:
            chants_of_community[i] = []
            tab_data['head'].append({'com' : "Community "+str(i+1), 'sources' : str(len(community))+" sources", 'color' : colors[i]})
            tab_data['tail'].append([])
            for feast_id in feast_ids:
                chants_of_feast = Data_Chant.objects.filter(feast_id = feast_id).values()
                for source_id in community:
                    chants_of_source = [(chant['office_id'], chant['cantus_id'], chant['incipit']) for chant in chants_of_feast if chant['source_id'] == source_id]
                    chants_of_community[i]+= chants_of_source
                    tab_data['tail'][i].append({'source_id' : source_id, 'siglum' : Sources.objects.filter(drupal_path = source_id).values_list('siglum')[0][0]})
            i += 1


        offices = {'office_v' : 'V', 'office_c' : 'C', 'office_m' : 'M', 'office_l' : 'L', 'office_p' : 'P', 'office_t' :'T', 'office_s' :'S', 
                'office_n' : 'N', 'office_v2' :'V2', 'office_d' :'D', 'office_r' :'R', 'office_e' : 'E', 'office_h' : 'H', 'office_ca' : 'CA', 'office_x' : 'X'}
        if filtering_office == []:
            filtering_office = offices
        for office in filtering_office:
            for i in range(len(communities)):
                community_office_chants = [chant for chant in chants_of_community[i] if chant[0] == office]
                if community_office_chants != []:
                    # Frequency count
                    frequency = Counter(community_office_chants)
                    ordered_freq = [k for k in frequency.most_common()]
                    
                    uncollapsed_chant_info = []
                    # Take six most frequent chants
                    j = 0
                    while j < 6:
                        try:
                            uncollapsed_chant_info.append({'incipit' : ordered_freq[j][0][2], 'cantus_id' : ordered_freq[j][0][1], 'freq' : "("+str(ordered_freq[j][1])+" | "+str(round((ordered_freq[j][1]/len(communities[i]))*100, 2))+" %)"})
                        except:
                            break
                        j+=1
                    
                    collapsed_chant_info = []
                    # Take potencial rest of chants
                    for j in range(j, len(ordered_freq)):
                        collapsed_chant_info.append({'incipit' : ordered_freq[j][0][2], 'cantus_id' : ordered_freq[j][0][1], 'freq' : "("+str(ordered_freq[j][1])+" | "+str(round((ordered_freq[j][1]/len(communities[i]))*100, 2))+" %)"})

                    try:
                        tab_data['body'][offices[office]].append({'uncollapsed': uncollapsed_chant_info, 'collapsed' : collapsed_chant_info})
                    except:
                        tab_data['body'][offices[office]] = [{'uncollapsed': uncollapsed_chant_info, 'collapsed' : collapsed_chant_info}]
        print(tab_data)
        return tab_data
    
    return None