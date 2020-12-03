import json, os, string
from json import JSONEncoder

# referencing: https://rubikscode.net/2020/10/26/ml-optimization-pt-1-gradient-descent-with-python/
class PickrateRegression(object):
    def __init__(self, championName):
        self.championName = championName
        self.winrateWeight = 0.0
        self.kdaWeight = 0.0
        self.masteryWeight = 0.0
        self.constant = 0.0
        self.percentageLearningRate = 0.01
        self.kdaLearningRate = 0.001
        self.iterations = 1000

    def __repr__(self):
        return {'winrateWeight': self.winrateWeight, 'kdaWeight': self.kdaWeight, 'masteryWeight':self.masteryWeight, 'constant':self.constant}

    def getObservedData(self, summonerChampDataPath='parsedSummonerData/summonerDataByChamp.json'):
        observations = dict()
        with open(summonerChampDataPath, 'r') as allData:
            summonerChampData = json.load(allData)
            # print(type(summonerChampData))
        
        for summonerName in summonerChampData[self.championName]:
            observations[summonerName] = summonerChampData[self.championName][summonerName]['pickrate']

        return observations

    def getPredictedData(self, summonerChampDataPath='parsedSummonerData/summonerDataByChamp.json'):
        predictions = dict()
        with open(summonerChampDataPath, 'r') as allData:
            summonerChampData = json.load(allData)

        for summonerName in summonerChampData[self.championName]:
            # print(f'summonerChampData: {summonerChampData}')
            temp = summonerChampData[self.championName][summonerName]['winrate']
            # print('break')
            '''
            for tempKey in temp:
                print(f'{tempKey}: {temp[tempKey]}, type: {type(tempKey)}')
            '''
            # print(f'weights: {self.winrateWeight}, {self.kdaWeight}, {self.masteryWeight}')
            predictedPickrate = (self.winrateWeight*summonerChampData[self.championName][summonerName]['winrate'] + self.kdaWeight*summonerChampData[self.championName][summonerName]['KDA'] + 
                                self.masteryWeight*summonerChampData[self.championName][summonerName]['masteryPercentage'] + self.constant)
            # print(predictedPickrate)
            predictions[summonerName] = predictedPickrate
        
        return predictions

    def getMSE(self, summonerChampDataPath='parsedSummonerData/summonerDataByChamp.json'):
        observedData = self.getObservedData(summonerChampDataPath)
        predictedData = self.getPredictedData(summonerChampDataPath)
        # print(f'observedData: {observedData}')
        # print(f'predictedData: {predictedData}')
        
        numberOfDatapoints = len(observedData)
        mseScalar = 1 / numberOfDatapoints
        mseSum = 0

        for summonerName in observedData:
            localError = (observedData[summonerName] - predictedData[summonerName])**2
            mseSum += localError
        
        mse = mseScalar * mseSum

        return mse
    
    def fitLine(self):
        prevMSE = self.getMSE()
        # print(f'prevMSE: {prevMSE}')

        for i in range(self.iterations):
            self.winrateWeight += self.percentageLearningRate
            tempMSE = self.getMSE()
            if tempMSE < prevMSE:
                prevMSE = tempMSE
            else:
                self.winrateWeight -= 2 * self.percentageLearningRate
                tempMSE = self.getMSE()
                if tempMSE < prevMSE:
                    prevMSE = tempMSE
                else:
                    self.winrateWeight += self.percentageLearningRate
                    break

        for i in range(self.iterations):
            self.masteryWeight += self.percentageLearningRate
            tempMSE = self.getMSE()
            if tempMSE < prevMSE:
                prevMSE = tempMSE
            else:
                self.masteryWeight -= 2 * self.percentageLearningRate
                tempMSE = self.getMSE()
                if tempMSE < prevMSE:
                    prevMSE = tempMSE
                else:
                    self.masteryWeight += self.percentageLearningRate
                    break
        
        for i in range(self.iterations):
            self.kdaWeight += self.kdaLearningRate
            # print(f'self.kdaWeight BIG: {self.kdaWeight}')
            tempMSE = self.getMSE()
            # print(f'tempMSE: {tempMSE}')
            if tempMSE < prevMSE:
                prevMSE = tempMSE
            else:
                self.kdaWeight -= 2 * self.kdaLearningRate
                # print(f'self.kdaWeight SMALL: {self.kdaWeight}')
                tempMSE = self.getMSE()
                if tempMSE < prevMSE:
                    prevMSE = tempMSE
                else:
                    self.kdaWeight += self.kdaLearningRate
                    # print(f'self.kdaWeight FINAL: {self.kdaWeight}')
                    break

        for i in range(self.iterations):
            self.constant += self.percentageLearningRate
            tempMSE = self.getMSE()
            if tempMSE < prevMSE:
                prevMSE = tempMSE
            else:
                self.constant -= 2 * self.percentageLearningRate
                tempMSE = self.getMSE()
                if tempMSE < prevMSE:
                    prevMSE = tempMSE
                else:
                    self.constant += self.percentageLearningRate
                    break

        return {'winrateWeight': self.winrateWeight, 'kdaWeight': self.kdaWeight, 'masteryWeight':self.masteryWeight, 'constant':self.constant}

    def predictPickrate(self, summonerData):
        summonerWinrate = summonerData['winrate']
        summonerKDA = summonerData['KDA']
        summonerMastery = summonerData['mastery']

        predictedPickrate = (self.winrateWeight*summonerChampData[self.championName][summonerName]['winrate'] + self.kdaWeight*summonerChampData[self.championName][summonerName]['KDA'] + 
                            self.masteryWeight*summonerChampData[self.championName][summonerName]['masteryPercentage'] + self.constant)

        return predictedPickrate

    def getWeights(self):
        return {'winrateWeight': self.winrateWeight, 'kdaWeight': self.kdaWeight, 'masteryWeight':self.masteryWeight, 'constant':self.constant}

# copied from: https://pynative.com/make-python-class-json-serializable/

class PickrateRegressionEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__