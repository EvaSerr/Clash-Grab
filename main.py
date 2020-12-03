from parseData import *
from regression import *

def findChampionRegressions():
    championRegressions = dict()

    with open('parsedSummonerData/summonerDataByChamp.json') as summonerChampData:
        availableChampions = json.load(summonerChampData)
#        print(f'in: {availableChampions}')
#    print(f'out: {availableChampions}')

    iterations = 0
    for championName in availableChampions:
        print(f'iterations: {iterations}')
        regressionModel = PickrateRegression(championName)
        weights = regressionModel.fitLine()
        # print(weights)
        championRegressions[championName] = regressionModel
        iterations += 1
    
    return championRegressions

def main():
    allChampionRegressions = findChampionRegressions()
    with open('championRegressionData.json', 'w') as championRegressions:
        json.dump(allChampionRegressions, championRegressions, indent=2, cls=PickrateRegressionEncoder)

if (__name__ == '__main__'):
    main()