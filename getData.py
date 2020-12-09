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
lol_watcher = LolWatcher('RGAPI-d4e17890-be4b-4fdf-921d-328090cc960b')

# region = 'na1'

def findSummonerList(lol_watcher):
    # queues Gold IV - I, Platinum IV - I, Diamond IV - I
    summonerRegion = 'na1'
    tierList = ['GOLD', 'PLATINUM', 'DIAMOND']
    divisionList = ['IV', 'III', 'II', 'I']
    queueType = 'RANKED_SOLO_5x5'
    pages = 1

    summonerNames = dict()
    for tier in tierList:
        for division in divisionList:
            for i in range(pages):
                leagueUUID = lol_watcher.league.entries(summonerRegion, queueType, tier, division, page=i)
                for summonerData in leagueUUID:
                    # print(summonerData)
                    name = summonerData['summonerName']

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
                print(doing)
                matchData = lol_watcher.match.by_id(self.region, match)

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

funghi3 = Summoner('funghi3', 'na1')