from collections import defaultdict
import json
# import requests

import aiohttp

from .channel_interfaces import Channel, Subgroup, ChannelpediaSubgroup


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




async def get_channel_group(source, position, group) -> list[Subgroup]:
    url = f"http://channelpedia.yavdr.com/restful/channelgroups/{source}/{position}/{group}/all/json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data: list[ChannelpediaSubgroup] = [ChannelpediaSubgroup(**subgroup) for subgroup in (await resp.json()).get('result', [])]

            return [
                Subgroup(
                    id=subgroup.x_label,
                    title=subgroup.friendlyname,
                    children=[
                        Channel(
                            channel_string=channel.string,
                            channel_id=channel.parameters.x_unique_id,
                            is_group=False,
                            is_radio=channel.parameters.vpid in (0, '0'),
                            name=f"{channel.parameters.name}",
                            provider=f"{channel.parameters.provider}",
                            ca=f"{channel.parameters.caid}",
                            source=f"{channel.parameters.source}",
                            number=9999,
                            ) for channel in subgroup.channels
                    ]
                ) for subgroup in data
            ]


if __name__ == '__main__':
    with open('channelpedia_data_DVB-C_münchen.json', 'w') as f:
        json.dump(get_channels(), f, indent=2)