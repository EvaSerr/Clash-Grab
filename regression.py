import json, os

# referencing: https://rubikscode.net/2020/10/26/ml-optimization-pt-1-gradient-descent-with-python/
class pickrateRegression():
    def __init__(self, championName):
        self.championName = championName
        self.winrateWeight = 0
        self.kdaWeight = 0
        self.masteryWeight = 0
        self.constant = 0
        self.percentageLearningRate = 0.01
        self.kdaLearningRate = 0.1
        self.iterations = 100

    @staticmethod
    def getObservedData(self, summonerChampDataPath='parsedSummonerData/summonerDataByChamp.json'):
        observations = dict()
        with open(summonerChampDataPath, 'r') as allData:
            summonerChampData = json.load(allData)
        
        for summonerName in summonerChampData[self.championName]:
            observations[summonerName] = summonerChampData[self.championName][summonerName]['pickrate']

        return observations

    def getPredictedData(self, summonerChampDataPath='parsedSummonerData/summonerDataByChamp.json'):
        predictions = dict()
        with open(summonerChampDataPath, 'r') as allData:
            summonerChampData = json.load(allData)

        for summonerName in summonerChampData[self.championName]:
            predictedPickrate = (self.winrateWeight*summonerChampData[self.championName][summonerName]['winrate'] + self.kdaWeight*summonerChampData[self.championName][summonerName]['KDA'] + 
                                self.masteryWeight*summonerChampData[self.championName][summonerName]['masteryPercentage'] + self.constant)
            predictions[summonerName] = predictedPickrate
        
        return predictions

    def getMSE(self):
        numberOfDatapoints = len(observedData)
        mseScalar = 1 / numberOfDatapoints
        mseSum = 0

        observedData = getObservedData('parsedSummonerData/summonerDataByChamp.json')
        predictedData = getPredictedData('parsedSummonerData/summonerDataByChamp.json')

        for summonerName in observedData:
            localError = (observedData[summonerName] - predictedData[summonerName])**2
            mseSum += localError
        
        mse = mseScalar * mseSum

        return mse
    
    def fitLine(self, summonerChampData):
        prevMSE = self.getMSE()
        weightsInPercentage = [self.winrateWeight, self.masteryWeight, self.constant]
        for specWeight in weightsInPercentage:
            for i in range(self.iterations):
                specWeight += self.percentageLearningRate
                tempMSE = self.getMSE()
                if tempMSE < prevMSE:
                    prevMSE = tempMSE
                else:
                    specWeight -= 2 * self.percentageLearningRate
                    tempMSE = self.getMSE()
                    if tempMSE < prevMSE:
                        prevMSE = tempMSE
                    else:
                        specWeight += self.percentageLearningRate
                        break

        for i in range(self.iterations):
            self.kdaWeight += self.kdaLearningRate
            tempMSE = self.getMSE()
            if tempMSE < prevMSE:
                prevMSE = tempMSE
            else:
                self.kdaWeight -= 2 * self.kdaLearningRate
                tempMSE = self.getMSE()
                if tempMSE < prevMSE:
                    prevMSE = tempMSE
                else:
                    self.kdaWeight += self.kdaLearningRate
                    break

        return {'winrateWeight': self.winrateWeight, 'kdaWeight': self.kdaWeight, 'masteryWeight':self.masteryWeight, 'constant':self.constant}

        def predictPickrate(self, summonerData):
            summonerWinrate = summonerData['winrate']
            summonerKDA = summonerData['KDA']
            summonerMastery = summonerData['mastery']

            predictedPickrate = (self.winrateWeight*summonerChampData[self.championName][summonerName]['winrate'] + self.kdaWeight*summonerChampData[self.championName][summonerName]['KDA'] + 
                                self.masteryWeight*summonerChampData[self.championName][summonerName]['masteryPercentage'] + self.constant)

            return predictedPickrate