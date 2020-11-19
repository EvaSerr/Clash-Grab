# the following code, until indicated is taken from the example at:
# https://riot-watcher.readthedocs.io/en/latest/index.html
from riotwatcher import LolWatcher, ApiError

lol_watcher = LolWatcher('RGAPI-d4e17890-be4b-4fdf-921d-328090cc960b')

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
    region = input()

    print(f'\nInput your summoner name: ', end='')
    summonerName = input()
    summonerData = lol_watcher.summoner.by_name(region, summonerName)
    summonerId = summonerData['id']

    rankedData = lol_watcher.league.by_summoner(region, summonerId)
    print(rankedData)
    sumTier, sumRank = rankedData[1]['tier'], rankedData[1]['rank']
    leagueUUID = lol_watcher.league.entries(region, 'RANKED_SOLO_5x5', sumTier, sumRank)
    print(f'leagueUUID: {leagueUUID}')