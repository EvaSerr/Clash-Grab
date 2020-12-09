from riotwatcher import LolWatcher, ApiError
import json, os

lol_watcher = LolWatcher('RGAPI-d4e17890-be4b-4fdf-921d-328090cc960b')

region = 'na1'

def getChampionList(lol_watcher=lol_watcher):
    # from: https://riot-watcher.readthedocs.io/en/latest/index.html
    versions = lol_watcher.data_dragon.versions_for_region(region)
    championsVersion = versions['n']['champion']
    
    currentChampList = lol_watcher.data_dragon.champions(championsVersion)['data']

    championsDict = dict()
    for champion in currentChampList:
        championsDict[currentChampList[champion]['name']] = {'id':currentChampList[champion]['id'], 'key':currentChampList[champion]['key']}

    with open('currentChampList.json', 'w') as champList:
        json.dump(championsDict, champList, indent=2)

    return championsDict
