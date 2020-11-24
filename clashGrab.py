from riotwatcher import LolWatcher, ApiError

lol_watcher = LolWatcher('RGAPI-d4e17890-be4b-4fdf-921d-328090cc960b')

def findSummonerList(lol_watcher):
    # queues Gold IV - I, Platinum IV - I, Diamond IV - I
    summonerRegion = 'na1'
    tierList = ['GOLD']
    divisionList = ['IV', 'III', 'II', 'I']
    queueType = 'RANKED_SOLO_5x5'

    summonerNames = dict()
    for tier in tierList:
        for division in divisionList:
            leagueUUID = lol_watcher.league.entries(summonerRegion, queueType, tier, division)
            for summonerData in leagueUUID:
                # print(summonerData)
                try:
                    name = summonerData['summonerName']
                    summonerId = summonerData['summonerId']
                    summonerNames[name] = summonerId
                except:
                    pass
    print(len(summonerNames))
    return summonerNames

def findChampMasteries(lol_watcher, summonerDict):
    summonerRegion = 'na1'

    versions = lol_watcher.data_dragon.versions_for_region(summonerRegion)
    champions_version = versions['n']['champion']

    current_champ_list = lol_watcher.data_dragon.champions(champions_version)
    champData = current_champ_list['data']
    champKeys = dict()
    for champ in champData:
        champKeys[champData[champ]['key']] = champ

    championMasteries = dict()
    depth = 0
    for summonerName in summonerDict:
        championMasteries[summonerName] = dict()
        try:
            print(f'doing {depth}')
            champMasteryDTO = lol_watcher.champion_mastery.by_summoner(summonerRegion, summonerDict[summonerName])
            for championMastery in champMasteryDTO:
                tempKey = str(championMastery['championId'])
                champName = champKeys[tempKey]
                championMasteries[summonerName][champName] = championMastery['championPoints']
            depth += 1
        except ApiError as err:
            if err.response.status_code == 429:
                print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
                print('this retry-after is handled by default by the RiotWatcher library')
                print('future requests wait until the retry-after time passes')
            elif err.response.status_code == 404:
                print('Summoner with that ridiculous name not found.')
            else:
                raise

    return championMasteries

names = findSummonerList(lol_watcher)
# print(names)
champMasteries = findChampMasteries(lol_watcher, names)
print(champMasteries)