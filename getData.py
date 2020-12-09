from riotwatcher import LolWatcher, ApiError
import json, os
##############################################################################################
#                                                                                            #
# see: https://riot-watcher.readthedocs.io/en/latest/riotwatcher/LeagueOfLegends/index.html, #
# https://developer.riotgames.com/docs/lol,                                                  #
# and https://developer.riotgames.com/apis#champion-v3/GET_getChampionInfo                   #
# for API docs                                                                               #
#                                                                                            #
##############################################################################################
lol_watcher = LolWatcher('development key')

# region = 'na1'

def findSummonerDict(lol_watcher, clashFilter=False, summonerLimit=False, region='na1'):
    # queues Gold IV - I, Platinum IV - I, Diamond IV - I
    # tierList = ['GOLD', 'PLATINUM', 'DIAMOND']
    tierList = ['PLATINUM']
    divisionList = ['IV', 'III', 'II', 'I']
    queueType = 'RANKED_SOLO_5x5'
    pages = 1
    doing = -1

    summonerNames = dict()
    for tier in tierList:
        for division in divisionList:
            numSummoners = 0
            for i in range(pages):
                leagueUUID = lol_watcher.league.entries(region, queueType, tier, division, page=(i+1))
                for summonerData in leagueUUID:
                    if not numSummoners >= 50: 
                        doing += 1
                        print(f'doing: {doing}')
                        if clashFilter:
                            name = summonerData['summonerName']
                            try:
                                accountId = lol_watcher.summoner.by_name(region, name)['accountId']
                                matchlistByQueue = lol_watcher.match.matchlist_by_account(region, accountId, queue='700', season='13')
                                summonerId = summonerData['summonerId']
                                summonerNames[name] = summonerId
                                if summonerLimit:
                                    numSummoners += 1
                            except ApiError as err: # error code copied from: https://riot-watcher.readthedocs.io/en/latest/
                                if err.response.status_code == 429:
                                    print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
                                    print('this retry-after is handled by default by the RiotWatcher library')
                                    print('future requests wait until the retry-after time passes')
                                elif err.response.status_code == 404:
                                    print(f"{name} hasn't played clash.")
                                else:
                                    raise
                        else:
                            name = summonerData['summonerName']
                            summonerId = summonerData['summonerId']
                            summonerNames[name] = summonerId
                            if summonerLimit:
                                numSummoners += 1
                    else:
                        print(f'division: {division} complete.')
                        break

    print(len(summonerNames))
    return summonerNames

def getChampionList(region='na1'):
    # from: https://riot-watcher.readthedocs.io/en/latest/index.html
    versions = lol_watcher.data_dragon.versions_for_region(region)
    championsVersion = versions['n']['champion']
    
    currentChamplist = lol_watcher.data_dragon.champions(championsVersion)['data']

    championsDict = dict()
    for champion in currentChamplist:
        championsDict[currentChamplist[champion]['name']] = {'id':currentChamplist[champion]['id'], 'key':currentChamplist[champion]['key']}

    with open('APIData/currentChamplist.json', 'w') as champList:
        json.dump(championsDict, champList, indent=2)

    return championsDict

def addMasteryData(pathSummonerData, pathSummonersDict, region='na1'):
    with open(pathSummonersDict, 'r') as summonersDictRead:
        summonersDict = json.load(summonersDictRead)

    versions = lol_watcher.data_dragon.versions_for_region(region)
    champions_version = versions['n']['champion']

    current_champ_list = lol_watcher.data_dragon.champions(champions_version)
    champData = current_champ_list['data']
    champKeys = dict()
    for champ in champData:
        champKeys[champData[champ]['key']] = champData[champ]['name']

    championMasteries = dict()
    depth = 0
    for summonerName in summonersDict:
        championMasteries[summonerName] = dict()
        try:
            print(f'doing {depth}')
            champMasteryDTO = lol_watcher.champion_mastery.by_summoner(region, summonersDict[summonerName])
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

    with open(pathSummonerData, 'r') as summonerDataRead:
        summonerData = json.load(summonerDataRead)
    
    summonerDataWithMastery = summonerData.copy()
    for summonerName in summonerData:
        summonerChampMasteries = championMasteries[summonerName]
        for championName in summonerData[summonerName]:
            summonerDataWithMastery[summonerName][championName]['mastery'] = summonerChampMasteries[championName]

    return summonerDataWithMastery

def addMasteryDataSingle(pathSummonerData, summonerName, region='na1'):
    versions = lol_watcher.data_dragon.versions_for_region(region)
    champions_version = versions['n']['champion']

    current_champ_list = lol_watcher.data_dragon.champions(champions_version)
    champData = current_champ_list['data']
    champKeys = dict()
    for champ in champData:
        champKeys[champData[champ]['key']] = champData[champ]['name']

    summonerId = lol_watcher.summoner.by_name(region, summonerName)['id']
    championMasteries = dict()
    depth = 0
    try:
        champMasteryDTO = lol_watcher.champion_mastery.by_summoner(region, summonerId)
        for championMastery in champMasteryDTO:
            print(f'doing {depth}')
            tempKey = str(championMastery['championId'])
            champName = champKeys[tempKey]
            championMasteries[champName] = championMastery['championPoints']
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
    
    with open(pathSummonerData, 'r') as summonerDataNoMasteryRead:
        summonerDataNoMastery = json.load(summonerDataNoMasteryRead)
    
    summonerDataWithMastery = summonerDataNoMastery.copy()
    for champName in summonerDataWithMastery[summonerName]:
        summonerDataWithMastery[summonerName][champName]['mastery'] = championMasteries[champName]
    
    with open(pathSummonerData, 'w') as summonerDataNoMasteryWrite:
        json.dump(summonerDataWithMastery, summonerDataNoMasteryWrite, indent=2)

    return pathSummonerData

class Summoner(object):
    def __init__(self, summonerName, region):
        self.summonerName = summonerName
        self.region = region
        self.accountId = lol_watcher.summoner.by_name(region, self.summonerName)['accountId']

    def __repr__(self):
        return self.summonerName

    def getMatchlistChampion(self, championName, queue='700', season='13'):
        with open('APIData/currentChamplist.json', 'r') as currentChamplistRead:
            currentChamplist = json.load(currentChamplistRead)

        matchlistByChampion = lol_watcher.match.matchlist_by_account(self.region, self.accountId, queue=queue, season=season,
                                                                     champion=currentChamplist[championName]['key'])

        return matchlistByChampion

    def getMatchlistQueue(self, queue='700', season='13'):
        matchlistByQueue = lol_watcher.match.matchlist_by_account(self.region, self.accountId, queue=queue, season=season)

        return matchlistByQueue

    def getGamesByChampion(self, matchlist=0):
        if matchlist == 0:
            matchlist = self.getMatchlistQueue()
        matches = matchlist['matches']
        # print(matches)

        champlistByKey = dict()
        with open('APIData/currentChamplist.json', 'r') as champlistRead:
            champlist = json.load(champlistRead)
        for champ in champlist:
            champlistByKey[champlist[champ]['key']] = champ
        # print(f'champlistByKey: {champlistByKey}')

        matchesByChampKey = dict()
        for match in matches:
            if matchesByChampKey.get(str(match['champion']), None) == None:
                matchesByChampKey[str(match['champion'])] = [match['gameId']]
            else:
                matchesByChampKey[str(match['champion'])].append(match['gameId'])
        # print(f'matchesByChampKey: {matchesByChampKey}')

        matchesByChamp = dict()
        for champKey in matchesByChampKey:
            # print(type(champKey))
            matchesByChamp[champlistByKey[champKey]] = matchesByChampKey[champKey]

        return matchesByChamp

    def parseGameData(self, matchlistByChamp=dict()):
        doing = -1
        if matchlistByChamp == dict():
            matchlistByChamp = self.getGamesByChampion()

        summonerData = {self.summonerName: dict()}
        # print(matchlistByChamp)
        for champ in matchlistByChamp:
            wins = 0
            losses = 0
            totalGames = len(matchlistByChamp[champ])
            kills = 0
            deaths = 0
            assists = 0
            KDA = 0

            for match in matchlistByChamp[champ]:
                doing += 1
                print(f'doing: {doing}')
                try:
                    matchData = lol_watcher.match.by_id(self.region, match)
                except ApiError as err: # error code copied from: https://riot-watcher.readthedocs.io/en/latest/
                    # error codes from: https://developer.riotgames.com/apis#match-v4
                    if err.response.status_code == 429:
                        print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
                        print('this retry-after is handled by default by the RiotWatcher library')
                        print('future requests wait until the retry-after time passes')
                    elif err.response.status_code == 404 or err.response.status_code == 503:
                        print(f"{match} doesn't exist.")
                        continue
                    elif err.response.status_code == 504:
                        print(f"Gateway Timeout for match: {match}")
                        continue
                    elif err.response.status_code == 401:
                        print(f"Unauthorized")
                        continue
                    elif err.response.status_code == 403:
                        print(f"Forbidden")
                        continue
                    elif err.response.status_code == 405:
                        print(f"Method not allowed")
                        continue
                    elif err.response.status_code == 415:
                        print(f"Unsupported media type")
                        continue
                    elif err.response.status_code == 500:
                        print(f"Internal server error for match: {match}")
                        continue
                    elif err.response.status_code == 502:
                        print(f"Bad gateway for match: {match}")
                        continue
                    else:
                        raise

                participantIdentities = matchData['participantIdentities']
                participantId = 0
                for participantIdentity in participantIdentities:
                    # print(participantIdentities)
                    if participantIdentity['player']['accountId'] == self.accountId:
                        participantId = participantIdentity['participantId']
                        break

                participants = matchData['participants']
                for participant in participants:
                    if participant['participantId'] == participantId:
                        participantStats = participant['stats']
                        kills += participantStats['kills']
                        deaths += participantStats['deaths']
                        assists += participantStats['assists']
                        won = participantStats['win']
                        if won:
                            wins += 1
                        else:
                            losses += 1

            if deaths == 0:
                KDA = kills + assists
            else:
                KDA = (kills + assists) / deaths
            
            winrate = wins / totalGames

            summonerData[self.summonerName][champ] = {'winrate': winrate, 'KDA': KDA, 'wins': wins, 'losses': losses, 'totalGames': totalGames}
        
        return summonerData

# funghi3 = Summoner('funghi3', 'na1')