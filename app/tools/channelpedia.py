from collections import defaultdict
from typing import Mapping, Any
import json
import logging
# import requests

import aiohttp


async def get_categories():
    # channel_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    channel_categories = []
    async with aiohttp.ClientSession() as session:
        async with session.get('http://channelpedia.yavdr.com/restful/sources', raise_for_status=True) as resp:
            data = (await resp.json()).get('result')
            for source, position_dict in data.items():
                channel_categories.append({
                    "id": source,
                    "title": source,
                    "children": [
                        {
                            "id": f"{source}|{position}",
                            "title": position,
                            "children": [
                                {
                                    "id": f"{source}|{position}|{group}",
                                    "title": group,
                                    "children": [],
                                } for group in (groups if groups else ['all'])
                            ]
                        } for position, groups in position_dict.items()
                    ]
                })
                for position, groups in position_dict.items():
                    if not groups:
                        groups = ['all']
                    
        return channel_categories


async def get_channels():
    channel_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    #for source, position_dict in get_categories().items():
    for source, position_dict in {'DVB-C': {'de_KabelDeutschland_Muenchen': ['de', 'sky_de']}}.items():
        for position, groups in position_dict.items():
            if not groups:
                groups = ['all']
            for group in groups:
                channel_data[source][position][group] += await get_channel_group(source=source, position=position, group=group)
    return channel_data


async def get_channel_group(source, position, group) -> list[Mapping[str, Any]]:
    url = f"http://channelpedia.yavdr.com/restful/channelgroups/{source}/{position}/{group}/all/json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = (await resp.json())['result']
            return [
                {
                    "id": subgroup.get('x_label'),
                    "title": subgroup.get('friendlyname'),
                    "children": [
                            {
                                'channel_string': channel['string'],
                                'channel_id': channel['parameters']['x_unique_id'],
                                'is_group': False,
                                'name': f"{channel['parameters']['name']}",
                                'provider': f"{channel['parameters']['provider']}",
                                'ca': f"{channel['parameters']['caid']}",
                                'source':f"{channel['parameters']['source']}",
                            } for channel in subgroup.get('channels', [])
                        ]
                } for subgroup in data
            ]


if __name__ == '__main__':
    with open('channelpedia_data_DVB-C_münchen.json', 'w') as f:
        json.dump(get_channels(), f, indent=2)