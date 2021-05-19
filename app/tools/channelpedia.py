from collections import defaultdict
import json
import requests

def get_categories():
    r = requests.get("http://channelpedia.yavdr.com/restful/sources")
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        return {}
    cat_data = r.json().get('result', {})
    return cat_data

def get_channels():
    channel_data= defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    #for source, position_dict in get_categories().items():
    for source, position_dict in {'DVB-C': {'de_KabelDeutschland_Muenchen': ['de', 'sky_de']}}.items():
        for position, groups in position_dict.items():
            if not groups:
                groups = ['all']
            for group in groups:
                url = f"http://channelpedia.yavdr.com/restful/channelgroups/{source}/{position}/{group}/all/json"
                r = requests.get(url)
                r.raise_for_status()
                channel_data[source][position][group] += r.json().get('result', [])
    return channel_data

if __name__ == '__main__':
    with open('channelpedia_data_DVB-C_münchen.json', 'w') as f:
        json.dump(get_channels(), f, indent=2)