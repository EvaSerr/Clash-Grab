# the following code, until indicated is taken from the example at:
# https://riot-watcher.readthedocs.io/en/latest/index.html
from riotwatcher import LolWatcher, ApiError

lol_watcher = LolWatcher('development key')

def riotWatcherExample(lol_watcher):
    my_region = 'na1'

    funghi3 = lol_watcher.summoner.by_name(my_region, 'funghi3')
    # print(funghi3)

    funghi3Ranked = lol_watcher.league.by_summoner(my_region, funghi3['id'])
    # print(funghi3Ranked)

    versions = lol_watcher.data_dragon.versions_for_region(my_region)
    champions_version = versions['n']['champion']
    # print(f'versions: {versions} \n\nchampions_version: {champions_version}')

    current_champ_list = lol_watcher.data_dragon.champions(champions_version)
    print(current_champ_list)

    # For Riot's API, the 404 status code indicates that the requested data wasn't found and
    # should be expected to occur in normal operation, as in the case of a an
    # invalid summoner name, match ID, etc.
    #
    # The 429 status code indicates that the user has sent too many requests
    # in a given amount of time ("rate limiting").
    try:
        response = lol_watcher.summoner.by_name(my_region, 'this_is_probably_not_anyones_summoner_name')
    except ApiError as err:
        if err.response.status_code == 429:
            print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
            print('this retry-after is handled by default by the RiotWatcher library')
            print('future requests wait until the retry-after time passes')
        elif err.response.status_code == 404:
            print('Summoner with that ridiculous name not found.')
        else:
            raise

################################################################################
#                       default example code ends here
################################################################################

def clashApiDemo(lol_watcher):
    print(f'Input your region: ', end='')
    region = input()

    print(f'\nInput your summoner name: ', end='')
    summonerName = input()
    summonerData = lol_watcher.summoner.by_name(region, summonerName)
    summonerId = summonerData['id']

    clashRegData = lol_watcher.clash.by_summoner(region, summonerId)
    print(f'\nclashRegData: {clashRegData}')
    teamId = clashRegData[0]['teamId']

    clashTourney = lol_watcher.clash.tournament_by_team(region, teamId)
    print(f'\nclashTourney: {clashTourney}')

    upcomingClash = lol_watcher.clash.tournaments(region)
    print(f'\nupcomingClash: {upcomingClash}')

def riotApiDemo(lol_watcher):
    print(f'Input your region: ', end='')
    summonerRegion = input()

    print(f'\nInput your summoner name: ', end='')
    summonerName = input()
    summonerData = lol_watcher.summoner.by_name(summonerRegion, summonerName)
    # print(summonerData)
    summonerId = summonerData['id']
    print(f'summonerId: {summonerId}')
    accountId = summonerData['accountId']
    print(f'accountId: {accountId}')
    myQueueType = 'RANKED_SOLO_5x5'
    myQueueTypeSet = {'RANKED_SOLO_5x5'}
    # print(type(myQueueTypeSet))

    rankedData = lol_watcher.league.by_summoner(summonerRegion, summonerId)
    # print(rankedData)
    sumTier, sumRank = rankedData[1]['tier'], rankedData[1]['rank']
    print(sumTier, sumRank)
    leagueUUID = lol_watcher.league.entries(summonerRegion, myQueueType, sumTier, sumRank)
    # print(f'leagueUUID: {leagueUUID}')
    leagueSummoners = set()
    for rankedSoloData in leagueUUID:
        leagueSummoners.add(rankedSoloData['summonerId'])

    versions = lol_watcher.data_dragon.versions_for_region(summonerRegion)
    champions_version = versions['n']['champion']

    current_champ_list = lol_watcher.data_dragon.champions(champions_version)
    # print(current_champ_list)
    champData = current_champ_list['data']
    # print(champData)
    champKeys = dict()
    for champ in champData:
        champKeys[champ] = champData[champ]['key']
    # print(champKeys)
    
    matchHist = lol_watcher.match.matchlist_by_account(summonerRegion, accountId, queue={420}, season={13}, champion={champKeys['Ashe']})
    # print(matchHist)

def findSummonerList(lol_watcher):
    # queues Gold IV - I, Platinum IV - I, Diamond IV - I
    summonerRegion = 'na1'
    rankList = ['GOLD', 'PLATINUM', 'DIAMOND']
    divisionList = ['IV', 'III', 'II', 'I']
    queueType = 'RANKED_SOLO_5x5'

    summonerNames = []
    for rank in rankList:
        for division in divisionList:
            leagueUUID = lol_watcher.league.entries(summonerRegion, queueType, division, rank)
            for summonerData in leagueUUID:
                summonerNames.append(leagueUUID['summonerName'])