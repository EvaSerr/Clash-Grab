from riotwatcher import LolWatcher, ApiError
import json, os

# raw data is taken from OP.GG

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
        champKeys[champData[champ]['key']] = champData[champ]['name']

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
    print(current_champ_list)
    
    champNameSet = set()
    for champ in champData:
        champNameSet.add(champData[champ]['name'])

    return champNameSet

def parseRankedData(path):
    summonerList = os.listdir(path)
    s10ChampDataParsed = dict()
    for summonerTxt in summonerList:
        if summonerTxt[len(summonerTxt)-4:] != '.txt':
            continue
        with open(path + '/' + summonerTxt) as s10ChampDataTxt:
            # read and split by champion, pop unnecessary JS header
            s10ChampDataRaw = s10ChampDataTxt.read()
            s10ChampDataRawList = s10ChampDataRaw.split('<td class="ChampionImage Cell">')
            s10ChampDataRawList.pop(0)

            # set result dict, remove all lines that do not contain relevantClasses
            s10ChampDataParsedBySummoner = dict()
            relevantClasses = ['<td class="ChampionName Cell', '<td class="RatioGraph Cell', '<div class="Text Left">', '<div class="Text Right">', '<td class="KDA Cell', '<span class="Kill">', '<span class="Assist">']
            for champCellRaw in s10ChampDataRawList:
                tempParse = []
                champCellRaw = champCellRaw.splitlines()
                for relevantClass in relevantClasses:
                    for jsLine in champCellRaw:
                        if relevantClass in jsLine:
                            tempParse.append(jsLine)
                            break

                # print(f'tempParse: {tempParse}')
                tempParsedGeneral = tempParse[:2] + [tempParse[len(tempParse) - 3]]
                # print(f'tempParsedGeneral: {tempParsedGeneral}')
                tempParsedGames = []
                if len(tempParse) == 7:
                    tempParsedGames = tempParse[2:4]
                else:
                    tempParsedGames = [tempParse[2]]
                # print(f'tempParsedGames: {tempParsedGames}')
                
                tempParsedKA = tempParse[5:]
                kPlusA = 0
                for tempKADataRaw in tempParsedKA:
                    classSplit = tempKADataRaw.split('>')
                    classSplit = classSplit[1].split('<')

                    kPlusA += float(classSplit[0])

                # split by quotes to find data-value, return only the data-value
                s10ChampDataParsedList = []
                for tempChampDataRaw in tempParsedGeneral:
                    classSplit = tempChampDataRaw.split('"')
                    dataValue = classSplit[len(classSplit) - 2]
                    # I hate Nunu in HTML
                    if dataValue == 'Nunu &amp; Willump':
                        dataValue = 'Nunu & Willump'
                    # account for perfect KDA
                    if dataValue == 'Perfect':
                        dataValue = f'{kPlusA}'
                    s10ChampDataParsedList.append(dataValue)

                totalGames = 0
                for tempGameDataRaw in tempParsedGames:
                    # parse format for win/losses
                    # print(f'classSplit1: {classSplit}')
                    classSplit = tempGameDataRaw.split('>')
                    # print(f'classSplit2: {classSplit}')
                    classSplit = classSplit[1].split('<')
                    # print(f'classSplit3: {classSplit}')
                    classSplit = classSplit[0]

                    totalGames += int(classSplit[:-1])

                    s10ChampDataParsedList.append(classSplit)
                
                s10ChampDataParsedList.append(totalGames)

                if len(s10ChampDataParsedList) == 6:
                    s10ChampDataParsedBySummoner[s10ChampDataParsedList[0]] = {'winrate':float(s10ChampDataParsedList[1]) / 100, 'KDA':float(s10ChampDataParsedList[2]), 'wins':int(s10ChampDataParsedList[3][:-1]), 
                    'losses':int(s10ChampDataParsedList[4][:-1]), 'totalGames':s10ChampDataParsedList[5]}
                elif s10ChampDataParsedList[len(s10ChampDataParsedList) - 2][-1] == 'W':
                    s10ChampDataParsedBySummoner[s10ChampDataParsedList[0]] = {'winrate':float(s10ChampDataParsedList[1]) / 100, 'KDA':float(s10ChampDataParsedList[2]), 'wins':int(s10ChampDataParsedList[3][:-1]), 
                    'losses':0, 'totalGames':s10ChampDataParsedList[4]}
                else:
                    s10ChampDataParsedBySummoner[s10ChampDataParsedList[0]] = {'winrate':float(s10ChampDataParsedList[1]) / 100, 'KDA':float(s10ChampDataParsedList[2]), 'wins':0,
                    'losses':int(s10ChampDataParsedList[3][:-1]), 'totalGames':s10ChampDataParsedList[4]}
                
        s10ChampDataParsed[summonerTxt[:len(summonerTxt) - 4]] = s10ChampDataParsedBySummoner
    return s10ChampDataParsed

def addPickrateEntry(path):
    pickrateData = dict()
    with open(path, 'r') as winsLossesData:
        prevData = json.load(winsLossesData)
        pickrateData = prevData.copy()

        for summonerName in prevData:
            totalGamesAllChamps = 0
            for championName in prevData[summonerName]:
                totalGamesAllChamps += prevData[summonerName][championName]['totalGames']

            for championName in prevData[summonerName]:
                pickrateData[summonerName][championName]['pickrate'] = prevData[summonerName][championName]['totalGames'] / totalGamesAllChamps
            
    with open(path, 'w') as opggWithPickrate:
        json.dump(pickrateData, opggWithPickrate, indent=2)
        
    return path

def combineOpggDataAndMastery(pathOpggData, pathMastery, pathTarget):
    with open(pathOpggData, 'r') as parsedOPGG:
        tempCombination = json.load(parsedOPGG)
        with open(pathMastery, 'r') as parsedMastery:
            masteryDict = json.load(parsedMastery)
            with open(pathTarget, 'w') as summonerData:
                for summonerName in masteryDict:
                    # print(f'name: {summonerName}')
                    for champName in masteryDict[summonerName]:
                        tempCombination[summonerName].get(champName, dict())['mastery'] = masteryDict[summonerName][champName]
                        # print(tempCombination)
                json.dump(tempCombination, summonerData, indent=2)
    
    return pathTarget

def percentizeMastery(path):
    with open(path, 'r') as summonerDataRead:
        tempData = json.load(summonerDataRead)
        # print(tempData)
        resultData = tempData.copy()
        for summonerName in tempData:
            totalMastery = 0
            for champName in tempData[summonerName]:
                # print(tempData[summonerName][champName]['mastery'])
                totalMastery += tempData[summonerName][champName]['mastery']
            for champName in resultData[summonerName]:
                resultData[summonerName][champName]['masteryPercentage'] = tempData[summonerName][champName]['mastery'] / totalMastery

    with open(path, 'w') as summonerDataWrite:
        json.dump(resultData, summonerDataWrite, indent=2)
    
    return path

def percentizeMasterySingle(path, summonerName):
    with open(path, 'r') as summonerDataRead:
        tempData = json.load(summonerDataRead)
        # print(tempData)
        resultData = tempData.copy()
        totalMastery = 0
        for champName in tempData[summonerName]:
            # print(tempData[summonerName][champName]['mastery'])
            totalMastery += tempData[summonerName][champName]['mastery']
        for champName in resultData[summonerName]:
            resultData[summonerName][champName]['masteryPercentage'] = tempData[summonerName][champName]['mastery'] / totalMastery

    with open(path, 'w') as summonerDataWrite:
        json.dump(resultData, summonerDataWrite, indent=2)

def convertToByChamp(path):
    with open(path, 'r') as summonerData:
        tempData = json.load(summonerData)
        resultData = dict()
        for summonerName in tempData:
            for championName in tempData[summonerName]:
                if championName in resultData:
                    resultData[championName][summonerName] = tempData[summonerName][championName]
                else:
                    resultData[championName] = {summonerName:tempData[summonerName][championName]}

    return resultData

# code copied from: https://www.geeksforgeeks.org/working-with-json-data-in-python/

with open('parsedSummonerData/opggDataBySummoner.json', 'w') as opggData:
    json.dump(parseRankedData('rawSummonerData'), opggData, indent=2)

combineOpggDataAndMastery('parsedSummonerData/opggDataBySummoner.json', 'parsedSummonerData/champMasteries.json', 'parsedSummonerData/champDataBySummoner.json')

percentizeMastery('parsedSummonerData/champDataBySummoner.json')

addPickrateEntry('parsedSummonerData/champDataBySummoner.json')

with open('parsedSummonerData/summonerDataByChamp.json', 'w') as parsedData:
    json.dump(convertToByChamp('parsedSummonerData/champDataBySummoner.json'), parsedData, indent=2)