from riotwatcher import LolWatcher, ApiError
import json, os

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
            summonerCount = 0
            leagueUUID = lol_watcher.league.entries(summonerRegion, queueType, tier, division)
            for summonerData in leagueUUID:
                # print(summonerData)
                name = summonerData['summonerName']
                if name.isalnum():
                    summonerId = summonerData['summonerId']
                    summonerNames[name] = summonerId
                    summonerCount += 1
                    if summonerCount >= 50:
                        break
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
        except ApiError as err: # error code copied from: https://riot-watcher.readthedocs.io/en/latest/
            if err.response.status_code == 429:
                print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
                print('this retry-after is handled by default by the RiotWatcher library')
                print('future requests wait until the retry-after time passes')
            elif err.response.status_code == 404:
                print('Summoner with that ridiculous name not found.')
            else:
                raise

    return championMasteries

def findChamps(lol_watcher):
    summonerRegion = 'na1'

    versions = lol_watcher.data_dragon.versions_for_region(summonerRegion)
    champions_version = versions['n']['champion']

    current_champ_list = lol_watcher.data_dragon.champions(champions_version)
    champData = current_champ_list['data']
    
    champNameSet = set()
    for champ in champData:
        champNameSet.add(champData[champ]['name'])

    return champNameSet

def parseRankedData(path):
    path = path
    summonerList = os.listdir(path)
    s10ChampDataParsed = dict()
    for summonerTxt in summonerList:
        with open(path + '/' + summonerTxt) as s10ChampDataTxt:
            # read and split by champion, pop unnecessary JS header
            s10ChampDataRaw = s10ChampDataTxt.read()
            s10ChampDataRawList = s10ChampDataRaw.split('<td class="ChampionImage Cell">')
            s10ChampDataRawList.pop(0)

            # set result dict, remove all lines that do not contain relevantClasses
            s10ChampDataParsedBySummoner = dict()
            relevantClasses = ['<td class="ChampionName Cell', '<td class="RatioGraph Cell', '<td class="KDA Cell']
            for champCellRaw in s10ChampDataRawList:
                tempParse = []
                champCellRaw = champCellRaw.splitlines()
                for relevantClass in relevantClasses:
                    for jsLine in champCellRaw:
                        if relevantClass in jsLine:
                            tempParse.append(jsLine)
                            break

                # split by quotes to find data-value, return only the data-value
                s10ChampDataParsedList = []
                for tempChampDataRaw in tempParse:
                    classSplit = tempChampDataRaw.split('"')
                    dataValue = classSplit[len(classSplit) - 2]
                    s10ChampDataParsedList.append(dataValue)
                
                s10ChampDataParsedBySummoner[s10ChampDataParsedList[0]] = {'winRate':s10ChampDataParsedList[1], 'KDA':s10ChampDataParsedList[2]}
        s10ChampDataParsed[summonerTxt[:len(summonerTxt) - 4]] = s10ChampDataParsedBySummoner
    return s10ChampDataParsed

# code copied from: https://www.geeksforgeeks.org/working-with-json-data-in-python/

'''
names = findSummonerList(lol_watcher)
champMasteriesDict = findChampMasteries(lol_watcher, names)

with open('rawSummonerData/allSummoners.json', 'w') as allSummonerNames:
    json.dump(names, allSummonerNames, indent=2)

with open('parsedSummonerData/champMasteries.json', 'w') as masteryData:
    json.dump(champMasteriesDict, masteryData, indent=2)
'''

'''
# print(findChamps(lol_watcher))
with open('rawSummonerData/1v9r.txt', 'r') as s10ChampDataTxt:
    s10ChampDataRaw = s10ChampDataTxt.read()
    s10ChampDataRawList = s10ChampDataRaw.split('<td class="ChampionImage Cell">')
    s10ChampDataRawList.pop(0)

    s10ChampDataParsed = dict()
    relevantClasses = ['<td class="ChampionName Cell', '<td class="RatioGraph Cell', '<td class="KDA Cell']
    for champCellRaw in s10ChampDataRawList:
        tempParse = []
        champCellRaw = champCellRaw.splitlines()
        for relevantClass in relevantClasses:
            for jsLine in champCellRaw:
                if relevantClass in jsLine:
                    tempParse.append(jsLine)
                    break

        s10ChampDataParsedList = []
        for tempChampDataRaw in tempParse:
            classSplit = tempChampDataRaw.split('"')
            dataValue = classSplit[len(classSplit) - 2]
            s10ChampDataParsedList.append(dataValue)
        
        s10ChampDataParsed[s10ChampDataParsedList[0]] = {'winRate':s10ChampDataParsedList[1], 'KDA':s10ChampDataParsedList[2]}
    print(s10ChampDataParsed)
'''
with open('parsedSummonerData/champDataBySummoner.json', 'w') as parsedOPGG:
    json.dump(parseRankedData('rawSummonerData'), parsedOPGG, indent=2)