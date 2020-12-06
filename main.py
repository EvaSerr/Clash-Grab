from parseData import *
from regression import *
from cmu_112_graphics import *

class clashGrabUI(App):
    def appStarted(self):
        # colors taken from https://coolors.co/084887-758bfd-aeb8fe-f1f2f6-416165
        self.yaleBlue = '#084887'
        self.cornFlowerBlue = '#758BFD'
        self.maximumBluePurple = '#AEB8FE'
        self.cultured = '#F1F2F6'
        self.deepSpaceSparkle = '#416165'

        self.numTabs = 5
        self.tabWidth = self.width // 8
        self.tabHeight = self.height // 12
        self.tabMargin = min(self.width, self.height) // 200
        self.tabFont = f'Helvetica {self.tabHeight // 4} bold'
        self.tabColor = self.cornFlowerBlue
        self.tabTextColor = self.cultured
        self.noTabColor = 'white'
        self.outlineColor = self.cultured

        self.tabs = ['Home', 'Data', 'Regression', 'Instructions', 'Analysis']
        self.currentTab = 0
        self.inputHTML = ''
        self.summonerQueryName = ''
        self.regressionData = [ ]

        self.backgroundColor = self.maximumBluePurple

        self.cx = self.width // 2
        self.cy = self.height // 2
        self.buttonWidth = self.width // 3
        self.buttonHeight = self.height // 4
        self.buttonText = 'Click to enter data'
        self.buttonFont = f'Helvetica {self.buttonHeight // 6} bold'
        self.buttonTextColor = self.cultured
        self.buttonColor = self.cornFlowerBlue
        self.buttonOutline = min(self.width, self.height) // 100

        self.dataRowHeight = (self.height-self.tabMargin-self.tabHeight) // 10
        self.regressionFont = f'Helvetica {self.dataRowHeight // 4} bold'
        self.regressionTextColor = self.cultured
        self.regressionTextMargin = self.dataRowHeight // 2

        self.instructions = ['1. Head to Op.gg', 
                            '2. Search the Summoner Name that was previously entered', 
                            '3. Head to the champions tab for that summoner', 
                            '4. Select Season 2020',
                            '5. Open the page inspection',
                            '6. Search "tbody.Body" within that page',
                            '7. Go to the last entry',
                            '8. Copy that header',
                            '9. Paste into the entry window',
                            '10. Proceed']

        self.analysis = ['Observations:',
                        'For champions with lower overall pickrates (across all summoners), mastery weighting tends to approach 1.',
                        'KDA weighting is never positive, but sometimes negative. This may be because if a given summoner has', 
                        'played a given champion a low number of times,', 
                        'they may have much higher average KDA then if they had played is many time: ie pickrate high, KDA low.',
                        'Winrate weighting is a magnitude lower than mastery weighting. Probably, pckrate is more dependent on', 
                        'character enjoyment over performance.',
                        'Anomalies:',
                        'The most prevalent anomaly is that if a champion has been played a very few number of times, one may have', 
                        '100% winrate on that champion.',
                        'Thereby, if the mastery weight is also relatively low, the winrate may make the predicted pick chance far', 
                        'higher then it should be.']

        self.readyToProceed = False
    # update GUI sizes
    def timerFired(self):
        self.tabWidth = self.width // 8
        self.tabHeight = self.height // 12
        self.tabMargin = min(self.width, self.height) // 200
        self.tabFont = f'Helvetica {self.tabHeight // 4} bold'

        self.cx = self.width // 2
        self.cy = self.height // 2
        self.buttonWidth = self.width // 3
        self.buttonHeight = self.height // 4
        self.buttonFont = f'Helvetica {self.buttonHeight // 6} bold'
        self.buttonOutline = min(self.width, self.height) // 100

        self.dataRowHeight = (self.height-self.tabMargin-self.tabHeight) // 10
        self.regressionFont = f'Helvetica {self.dataRowHeight // 4} bold'
        self.regressionTextMargin = self.dataRowHeight // 2

    # 
    def getRegressionData(self):
        with open('championRegressionData.json', 'r') as championRegressionDataRead:
            championRegressionData = json.load(championRegressionDataRead)
        
        with open('parsedInputData/inputSummonerDataByChamp.json', 'r') as parsedDataRead:
            parsedData = json.load(parsedDataRead)

        # [(chamipon, winrate), ...]
        pickrates = [ ]
        for champName in parsedData:
            try: # if not played, initialize values as 0
                inputWinrate = parsedData[champName][self.summonerQueryName]['winrate']
                inputKDA = parsedData[champName][self.summonerQueryName]['KDA']
                inputMastery = parsedData[champName][self.summonerQueryName]['masteryPercentage']
            except:
                inputWinrate = 0
                inputKDA = 0
                inputMastery = 0

            # add independent variables scaled by weight
            outputWinrate = championRegressionData[champName]['winrateWeight'] * inputWinrate
            outputKDA = championRegressionData[champName]['kdaWeight'] * inputKDA
            outputMastery = championRegressionData[champName]['masteryWeight'] * inputMastery

            outputPickrate = outputWinrate + outputKDA + outputMastery + championRegressionData[champName]['constant']
            champAndPickrate = (champName, outputPickrate)
            
            # make list of champ pickrates, highest pickrate first
            if len(pickrates) == 0:
                pickrates.append(champAndPickrate)
            elif len(pickrates) == 1:
                if outputPickrate >= pickrates[0][1]:
                    pickrates.insert(0, champAndPickrate)
                else:
                    pickrates.append(champAndPickrate)
            else:
                if outputPickrate >= pickrates[0][1]:
                    pickrates.insert(0, champAndPickrate)
                elif outputPickrate < pickrates[-1][1]:
                    pickrates.append(champAndPickrate)
                else:
                    for i in range(0, len(pickrates) - 2):
                        if pickrates[i][1] > outputPickrate >= pickrates[i+1][1]:
                            pickrates.insert(i+1, champAndPickrate)
                            break

        return pickrates

    def mousePressed(self, event):
        # if button pressed, parse data and get regressions
        if ((self.cx-self.buttonWidth//2 <= event.x <= self.cx+self.buttonWidth//2) and 
        (self.cy-self.buttonHeight//2 <= event.y <= self.cy+self.buttonHeight//2) and
        self.currentTab == 0):
            # copied from: https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#ioMethods
            self.summonerQueryName = self.getUserInput('Insert summoner name here:')
            # account for incorrect inputs
            if  self.summonerQueryName == None:
                self.showMessage('cancelled')
                self.readyToProceed = False
            else:
                self.inputHTML = self.getUserInput('Copy summoner champ HTML here: \n  (inspect element find last instance of "tbody.Body")')
                if self.inputHTML == None or self.summonerQueryName == None:
                    self.showMessage('cancelled')
                    self.readyToProceed = False
                elif '<tr class="Row TopRanker" role="row">' not in self.inputHTML.splitlines()[1]:
                    self.showMessage('Please go to the Summoner -> Champions tab')
                    self.readyToProceed = False
                else:
                    # make .txt file with OPgg HTML for given summoner
                    dataTxt = open(f'rawInputData/{self.summonerQueryName}.txt', 'w')
                    dataTxt.write(self.inputHTML)
                    # get all summoners queried
                    with open('rawInputData/inputSummoners.json', 'r') as inputSummonersRead:
                        currentInputSummoners = json.load(inputSummonersRead)
                        # account for initial query
                        if currentInputSummoners == None:
                            currentInputSummoners = dict()
                    # get masteries and summoner ID, write to file
                    with open('rawInputData/inputSummoners.json', 'w') as inputSummonersWrite:
                        currentInputSummoners[self.summonerQueryName] = lol_watcher.summoner.by_name('na1', self.summonerQueryName)['id']
                        currentSummoner = {self.summonerQueryName:lol_watcher.summoner.by_name('na1', self.summonerQueryName)['id']}
                        json.dump(currentInputSummoners, inputSummonersWrite, indent=2)
                    
                    with open('parsedInputData/inputChampMasteries.json', 'w') as inputChampDataBySummoner:
                        json.dump(findChampMasteries(lol_watcher, currentSummoner), inputChampDataBySummoner, indent=2)

                    # parse and process data
                    with open('parsedInputData/InputOPggDataBySummoner.json', 'w') as opggData:
                        json.dump(parseRankedData('rawInputData'), opggData, indent=2)

                    combineOpggDataAndMastery('parsedInputData/InputOPggDataBySummoner.json', 'parsedInputData/inputChampMasteries.json', 'parsedInputData/inputChampDataBySummoner.json')

                    percentizeMasterySingle('parsedInputData/inputChampDataBySummoner.json', self.summonerQueryName)

                    addPickrateEntry('parsedInputData/inputChampDataBySummoner.json')

                    with open('parsedInputData/inputSummonerDataByChamp.json', 'w') as parsedData:
                        json.dump(convertToByChamp('parsedInputData/inputChampDataBySummoner.json'), parsedData, indent=2)

                    # get regression outputs
                    self.regressionData = self.getRegressionData()

                    self.readyToProceed = True
                    self.showMessage('Data is ready')
        # move to the tab that's been clicked
        elif (self.tabMargin <= event.x < self.tabMargin + self.tabWidth and
                self.tabMargin <= event.y < self.tabMargin + self.tabHeight):
            self.currentTab = 0
        elif (self.tabMargin + self.tabWidth <= event.x < self.tabMargin + 2*self.tabWidth and
                self.tabMargin <= event.y < self.tabMargin + self.tabHeight and
                self.readyToProceed == True):
            self.currentTab = 1
        elif (self.tabMargin + 2*self.tabWidth <= event.x < self.tabMargin + 3*self.tabWidth and
                self.tabMargin <= event.y < self.tabMargin + self.tabHeight and
                self.readyToProceed == True):
            self.currentTab = 2
        elif (self.tabMargin + 3*self.tabWidth <= event.x < self.tabMargin + 4*self.tabWidth and
                self.tabMargin <= event.y < self.tabMargin + self.tabHeight):
            self.currentTab = 3
        elif (self.tabMargin + 4*self.tabWidth <= event.x < self.tabMargin + 5*self.tabWidth and
                self.tabMargin <= event.y < self.tabMargin + self.tabHeight):
            self.currentTab = 4

    def drawTabs(self, canvas):
        tabOrder = [self.currentTab]
        for i in range(self.numTabs):
            if i != self.currentTab:
                tabOrder.append(i)
        for i in tabOrder:
            x0, y0, x1, y1 = self.tabMargin + self.tabWidth*i, self.tabMargin, self.tabMargin + self.tabWidth*(i+1), self.tabMargin + self.tabHeight
            if i == self.currentTab:
                canvas.create_rectangle(x0, y0, x1, y1, fill=self.backgroundColor, outline=self.backgroundColor, width=self.tabMargin)
            else:
                canvas.create_rectangle(x0, y0, x1, y1, fill=self.tabColor, outline=self.outlineColor, width=self.tabMargin)
            canvas.create_text((x1+x0)//2, (y1+y0)//2, text=self.tabs[i], fill=self.tabTextColor, font=self.tabFont)

    def drawButton(self, canvas):
        canvas.create_rectangle(self.cx-self.buttonWidth//2, self.cy-self.buttonHeight//2, self.cx+self.buttonWidth//2, 
        self.cy+self.buttonHeight//2, fill=self.buttonColor, outline=self.outlineColor, width=self.tabMargin)
        canvas.create_text(self.cx, self.cy, text=self.buttonText, fill=self.buttonTextColor, font=self.buttonFont)

    def drawBackground(self, canvas):
        # draw background
        xTabsEnd = self.tabMargin + self.tabWidth*self.numTabs
        y0TabsEnd, y1TabsEnd = self.tabMargin, 2*self.tabMargin + self.tabHeight
        canvas.create_rectangle(xTabsEnd + self.tabMargin, y0TabsEnd, self.width-self.tabMargin, y1TabsEnd, fill=self.noTabColor, outline=self.noTabColor, width=self.tabMargin)
        
        canvas.create_rectangle(self.tabMargin, y1TabsEnd, self.width-self.tabMargin, self.height-self.tabMargin, fill=self.backgroundColor, outline=self.backgroundColor, width=self.tabMargin)
        # canvas.create_line(xTabsEnd, self.tabHeight+self.tabMargin // 2, self.width, self.tabHeight+self.tabMargin // 2, )

    def drawData(self, canvas):
        # get likelihoods only for top 10 champs
        for i in range(10):
            championName = self.regressionData[i][0]
            championPickrate = self.regressionData[i][1]
            rowCenter = i*self.dataRowHeight + self.dataRowHeight//2
            # round from: https://docs.python.org/3/library/functions.html#round
            displayText = f'{championName}: {round(championPickrate*100, 2)} pick chance'
            canvas.create_text(self.regressionTextMargin, self.tabMargin+self.tabHeight+rowCenter, text=displayText, anchor='w', font=self.regressionFont, fill=self.regressionTextColor)

    def drawRegression(self, canvas):
        with open('championRegressionData.json', 'r') as championRegressionDataRead:
            championRegressionData = json.load(championRegressionDataRead)

        # get regression data only for top 10 champs
        for i in range(10):
            championName = self.regressionData[i][0]
            rowCenter = i*self.dataRowHeight + self.dataRowHeight//2
            champWinrateWeight = round(championRegressionData[championName]['winrateWeight'], 2)
            champKDAWeight = round(championRegressionData[championName]['kdaWeight'], 2)
            champMasteryWeight = round(championRegressionData[championName]['masteryWeight'], 2)
            champConstant = round(championRegressionData[championName]['constant'], 2)
            displayText = f"{championName}'s regression weights: Winrate Weight={champWinrateWeight}, KDA Weight={champKDAWeight}, Mastery Weight={champMasteryWeight}, Constant={champConstant}"
            canvas.create_text(self.regressionTextMargin, self.tabMargin+self.tabHeight+rowCenter, text=displayText, anchor='w', font=self.regressionFont, fill=self.regressionTextColor)

    def drawInstructions(self, canvas):
        printInstructions = ''
        for instruction in self.instructions:
            printInstructions += instruction + '\n'
        canvas.create_text(self.regressionTextMargin, self.tabMargin+self.tabHeight+self.dataRowHeight//2, text=printInstructions, anchor='nw', font=self.regressionFont, fill=self.regressionTextColor)
    
    def drawAnalysis(self, canvas):
        printAnalysis = ''
        for info in self.analysis:
            if info in ['Obervations:', 'Anomalies:']:
                printAnalysis += '\n' + info + '\n'
            else:
                printAnalysis += info + '\n'
        canvas.create_text(self.regressionTextMargin, self.tabMargin+self.tabHeight+self.dataRowHeight//2, text=printAnalysis, anchor='nw', font=self.regressionFont, fill=self.regressionTextColor)

    def redrawAll(self, canvas):
        self.drawBackground(canvas)
        self.drawTabs(canvas)
        if self.currentTab == 0:
            self.drawButton(canvas)
        elif self.readyToProceed and self.currentTab == 1:
            self.drawData(canvas)
        elif self.readyToProceed and self.currentTab == 2:
            self.drawRegression(canvas)
        elif self.currentTab == 3:
            self.drawInstructions(canvas)
        elif self.currentTab == 4:
            self.drawAnalysis(canvas)
    
def main():
    '''
    allChampionRegressions = findChampionRegressions()
    with open('championRegressionData.json', 'w') as championRegressions:
        json.dump(allChampionRegressions, championRegressions, indent=2, cls=PickrateRegressionEncoder)
    '''

    clashGrabUI(width=704, height=400)

if (__name__ == '__main__'):
    main()