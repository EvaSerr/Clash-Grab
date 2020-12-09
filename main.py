from parseData import *
from regression import *
from getData import *
from cmu_112_graphics import *

class clashGrabUI(App):
    def appStarted(self):
        # colors taken from https://coolors.co/084887-758bfd-aeb8fe-f1f2f6-416165
        self.yaleBlue = '#084887'
        self.cornFlowerBlue = '#758BFD'
        self.maximumBluePurple = '#AEB8FE'
        self.cultured = '#F1F2F6'
        self.deepSpaceSparkle = '#416165'

        self.region = 'na1'
        self.queue = '420' # Ranked Solo 5x5
        self.season='13' # season 2019
        self.clashFilter = False
        self.summonerLimit = True
        self.apiRegression = False

        self.tabWidth = self.width // 8
        self.tabHeight = self.height // 12
        self.tabMargin = min(self.width, self.height) // 200
        self.tabFont = f'Helvetica {self.tabHeight // 4} bold'
        self.tabColor = self.cornFlowerBlue
        self.tabTextColor = self.cultured
        self.noTabColor = 'white'
        self.outlineColor = self.cultured

        self.tabs = ['Home', 'Data', 'Regression', 'Instructions', 'Analysis', 'Settings']
        self.numTabs = len(self.tabs)
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

        self.instructions = ['1. Click on the button labelled "Click to enter data"', 
                            '2. In the search bar that appears, enter a summoner name', 
                            '3. Wait until a pop-up informs you that the data is ready', 
                            '4. Select the data tab (or any other)',
                            '5. Employ said pick predictions in your next game if you so choose!']

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

        self.queueButtons = ['Ranked Solo', 'Ranked Flex (API crashes here)', 'Clash', 'API Regression']
        self.currentQueueButton = 0
        self.numQueueButtons = len(self.queueButtons) - 1
        self.queueButtonMargin = 2*self.tabMargin
        self.queueButtonWidth = self.width - (2*self.width//12)
        self.queueButtonHeight = (self.height - 3*self.tabMargin - self.tabHeight) // 4 - 10*self.queueButtonMargin
        self.queueButtonFont = f'Helvetica {self.buttonHeight // 4} bold'

        self.readyToProceed = False

        # image creation from: https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#imageSize
        # champion images from: https://developer.riotgames.com/docs/lol under section "Data Dragon"
        self.imageOriginalSize = 120
        self.imageSize = (self.height-self.tabMargin-self.tabHeight) // 14
        self.imageDict = dict()
        champIconList = os.listdir('champion')
        for champIconPath in champIconList:
            champIcon = self.loadImage('champion/' + champIconPath)
            imageScaled = self.imageSize / self.imageOriginalSize
            champIconScaled = self.scaleImage(champIcon, imageScaled)
            self.imageDict[champIconPath[:-4]] = champIconScaled

        # image from: https://fontspool.com/generator/league-of-legends-font
        self.titleOriginalSize = 1000
        self.titleTargetSize = 1.75*self.buttonWidth
        self.titleScale = self.titleTargetSize / self.titleOriginalSize
        self.title = self.loadImage('clashGrabTitle.png')
        self.titleScaled = self.scaleImage(self.title, self.titleScale)

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

        self.imageSize = (self.height-self.tabMargin-self.tabHeight) // 14
        self.imageDict = dict()
        champIconList = os.listdir('champion')
        for champIconPath in champIconList:
            champIcon = self.loadImage('champion/' + champIconPath)
            imageScaled = self.imageSize / self.imageOriginalSize
            champIconScaled = self.scaleImage(champIcon, imageScaled)
            self.imageDict[champIconPath[:-4]] = champIconScaled

        self.titleTargetSize = 1.75*self.buttonWidth
        self.titleScale = self.titleTargetSize / self.titleOriginalSize
        self.titleScaled = self.scaleImage(self.title, self.titleScale)

        self.queueButtonWidth = self.width - (2*self.width//12)
        self.queueButtonHeight = (self.height - 3*self.tabMargin - self.tabHeight) // 4 - 10*self.queueButtonMargin
        self.queueButtonFont = f'Helvetica {self.buttonHeight // 4} bold'

    def getRegressionData(self, regressionPath='championRegressionData.json'):
        with open(regressionPath, 'r') as championRegressionDataRead:
            championRegressionData = json.load(championRegressionDataRead)
        
        with open('APIData/inputSummonerByChamp.json', 'r') as parsedDataRead:
            parsedData = json.load(parsedDataRead)

        # [(champion, winrate), ...]
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
    
    def getAPIRegression(self):
        # gather data and find regression with api (takes a very long time depending on variables)
        # currently set to look at Ranked Solo 5x5
        loadAllSummonersDict = findSummonerDict(lol_watcher, clashFilter=self.clashFilter, summonerLimit=self.summonerLimit)
        with open('APIData/allSummoners.json', 'w') as allSummonersWrite:
            json.dump(loadAllSummonersDict, allSummonersWrite, indent=2)

        with open('APIData/allSummoners.json', 'r') as allSummonersRead:
            allSummonersDict = json.load(allSummonersRead)

        noMasteryDataBySummoner = dict()
        for summonerName in allSummonersDict:
            summoner = Summoner(summonerName, 'na1')
            print('getting matchlistQueue')
            matchlistQueue = summoner.getMatchlistQueue(queue=self.queue)
            print('getting gamesByChampion')
            gamesByChampion = summoner.getGamesByChampion(matchlist=matchlistQueue)
            print('parsing game data')
            rankedData = summoner.parseGameData(matchlistByChamp=gamesByChampion)
            noMasteryDataBySummoner[summonerName] = rankedData[summonerName]

        with open('APIData/noMasteryDataBySummoner.json', 'w') as noMasteryDataBySummonerWrite:
            json.dump(noMasteryDataBySummoner, noMasteryDataBySummonerWrite, indent=2)
        
        with open('APIData/dataBySummoner.json', 'w') as dataBySummonerWrite:
            json.dump(addMasteryData('APIData/noMasteryDataBySummoner.json', 'APIData/allSummoners.json'), dataBySummonerWrite, indent=2)
        

        percentizeMastery('APIData/dataBySummoner.json')

        addPickrateEntry('APIData/dataBySummoner.json')
        
        with open('APIData/dataByChamp.json', 'w') as parsedData:
            json.dump(convertToByChamp('APIData/dataBySummoner.json'), parsedData, indent=2)
        
        allChampionRegressions = findChampionRegressions(path='APIData/dataByChamp.json')
        with open('APIData/apiChampionRegressionData.json', 'w') as championRegressions:
            json.dump(allChampionRegressions, championRegressions, indent=2, cls=PickrateRegressionEncoder)
        
        return 'APIData/apiChampionRegressionData.json'
    

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
                inputSummoner = Summoner(self.summonerQueryName, self.region)
                print('getting matchlistQueue')
                matchlistQueue = inputSummoner.getMatchlistQueue(queue=self.queue, season=self.season)
                print('getting gamesByChampion')
                gamesByChampion = inputSummoner.getGamesByChampion(matchlist=matchlistQueue)
                print('parsing game data')
                rankedData = inputSummoner.parseGameData(matchlistByChamp=gamesByChampion)
                
                with open('APIData/inputSummoner.json', 'w') as inputSummonerWrite:
                    json.dump(rankedData, inputSummonerWrite, indent=2)
                
                addMasteryDataSingle('APIData/inputSummoner.json', inputSummoner.summonerName, region=self.region)

                percentizeMastery('APIData/inputSummoner.json')

                addPickrateEntry('APIData/inputSummoner.json')

                with open('APIData/inputSummonerByChamp.json', 'w') as inputSummonerBySummoner:
                    json.dump(convertToByChamp('APIData/inputSummoner.json'), inputSummonerBySummoner, indent=2)

                # get regression outputs
                if self.apiRegression:
                    self.regressionData = self.getRegressionData(regressionPath='APIData/apiChampionRegressionData.json')
                else:
                    self.regressionData = self.getRegressionData()

                self.readyToProceed = True
                self.showMessage('Data is ready')
        elif (self.cx-(2*self.buttonWidth//3)//2 <= event.x <= self.cx+(2*self.buttonWidth//3)//2 and 
              (self.cy+self.buttonHeight//2) + (self.height-self.tabMargin-(self.cy+self.buttonHeight//2))//2-(2*self.buttonHeight//3)//2 
              <= event.y <= (self.cy+self.buttonHeight//2) + (self.height-self.tabMargin-(self.cy+self.buttonHeight//2))//2+(2*self.buttonHeight//3)//2 and
              self.currentTab == 0):
              self.readyToProceed = False
              self.getAPIRegression()
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
        elif (self.tabMargin + 5*self.tabWidth <= event.x < self.tabMargin + 6*self.tabWidth and
                self.tabMargin <= event.y < self.tabMargin + self.tabHeight):
            self.currentTab = 5
        elif (self.width // 2 - self.queueButtonWidth//2 <= event.x <= self.width // 2 + self.queueButtonWidth//2 and
              (2*0+1) * ((self.height-3*self.tabMargin-self.tabHeight) // 8) + self.tabHeight + 2*self.tabMargin - self.queueButtonHeight//2 <= event.y 
              <= (2*0+1) * ((self.height-3*self.tabMargin-self.tabHeight) // 8) + self.tabHeight + 2*self.tabMargin + self.queueButtonHeight//2 and
              self.currentTab == 5):
            self.currentQueueButton = 0
            self.queue = '420'
            self.clashFilter = False
        elif (self.width // 2 - self.queueButtonWidth//2 <= event.x <= self.width // 2 + self.queueButtonWidth//2 and
              (2*1+1) * ((self.height-3*self.tabMargin-self.tabHeight) // 8) + self.tabHeight + 2*self.tabMargin - self.queueButtonHeight//2 <= event.y 
              <= (2*1+1) * ((self.height-3*self.tabMargin-self.tabHeight) // 8) + self.tabHeight + 2*self.tabMargin + self.queueButtonHeight//2 and
              self.currentTab == 5):
            self.currentQueueButton = 1
            self.queue = '440'
            self.clashFilter = False
        elif (self.width // 2 - self.queueButtonWidth//2 <= event.x <= self.width // 2 + self.queueButtonWidth//2 and
              (2*2+1) * ((self.height-3*self.tabMargin-self.tabHeight) // 8) + self.tabHeight + 2*self.tabMargin - self.queueButtonHeight//2 <= event.y 
              <= (2*2+1) * ((self.height-3*self.tabMargin-self.tabHeight) // 8) + self.tabHeight + 2*self.tabMargin + self.queueButtonHeight//2 and 
              self.currentTab == 5):
            self.currentQueueButton = 2
            self.queue = '700'
            self.clashFilter = True
        elif (self.width // 2 - self.queueButtonWidth//2 <= event.x <= self.width // 2 + self.queueButtonWidth//2 and
              (2*3+1) * ((self.height-3*self.tabMargin-self.tabHeight) // 8) + self.tabHeight + 2*self.tabMargin - self.queueButtonHeight//2 <= event.y 
              <= (2*3+1) * ((self.height-3*self.tabMargin-self.tabHeight) // 8) + self.tabHeight + 2*self.tabMargin + self.queueButtonHeight//2 and 
              self.currentTab == 5):
              self.apiRegression = not self.apiRegression

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

    def drawTitle(self, canvas):
        cx = self.cx
        cy = (2*self.tabMargin + self.tabHeight + self.cy-self.buttonHeight//2) // 2
        canvas.create_image(cx, cy, image=ImageTk.PhotoImage(self.titleScaled))

    def drawBackground(self, canvas):
        # draw background
        xTabsEnd = self.tabMargin + self.tabWidth*self.numTabs
        y0TabsEnd, y1TabsEnd = self.tabMargin, 2*self.tabMargin + self.tabHeight
        canvas.create_rectangle(xTabsEnd + self.tabMargin, y0TabsEnd, self.width-self.tabMargin, y1TabsEnd, fill=self.noTabColor, outline=self.noTabColor, width=self.tabMargin)
        
        canvas.create_rectangle(self.tabMargin, y1TabsEnd, self.width-self.tabMargin, self.height-self.tabMargin, fill=self.backgroundColor, outline=self.backgroundColor, width=self.tabMargin)
        # canvas.create_line(xTabsEnd, self.tabHeight+self.tabMargin // 2, self.width, self.tabHeight+self.tabMargin // 2, )

    def drawData(self, canvas):
        # get likelihoods only for top 10 champs
        for i in range(min(10, len(self.regressionData))):
            championName = self.regressionData[i][0]
            championPickrate = self.regressionData[i][1]
            rowCenter = i*self.dataRowHeight + self.dataRowHeight//2

            with open('APIData/currentChamplist.json', 'r') as champlistRead:
                champlist = json.load(champlistRead)

            # from: https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#imageSize
            champId = champlist[championName]['id']

            cx = (2*self.regressionTextMargin+self.imageSize) // 2
            cy = self.tabMargin+self.tabHeight+rowCenter
            canvas.create_rectangle(cx-self.imageSize/2, cy-self.imageSize/2, cx+self.imageSize/2, cy+self.imageSize/2,fill=None,
                                    outline=self.outlineColor, width=1.5*self.tabMargin)
            canvas.create_image(cx, cy, image=ImageTk.PhotoImage(self.imageDict[champId]))

            # round from: https://docs.python.org/3/library/functions.html#round
            displayText = f'{championName}: {round(championPickrate*100, 2)} pick score'
            canvas.create_text(2*self.regressionTextMargin+self.imageSize, self.tabMargin+self.tabHeight+rowCenter, text=displayText, anchor='w', font=self.regressionFont, fill=self.regressionTextColor)

    def drawRegression(self, canvas):
        with open('championRegressionData.json', 'r') as championRegressionDataRead:
            championRegressionData = json.load(championRegressionDataRead)

        # get regression data only for top 10 champs
        for i in range(min(10, len(self.regressionData))):
            championName = self.regressionData[i][0]
            rowCenter = i*self.dataRowHeight + self.dataRowHeight//2

            with open('APIData/currentChamplist.json', 'r') as champlistRead:
                champlist = json.load(champlistRead)

            # from: https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#imageSize
            champId = champlist[championName]['id']

            cx = (2*self.regressionTextMargin+self.imageSize) // 2
            cy = self.tabMargin+self.tabHeight+rowCenter
            canvas.create_rectangle(cx-self.imageSize/2, cy-self.imageSize/2, cx+self.imageSize/2, cy+self.imageSize/2,fill=None,
                                    outline=self.outlineColor, width=1.5*self.tabMargin)
            canvas.create_image(cx, cy, image=ImageTk.PhotoImage(self.imageDict[champId]))

            champWinrateWeight = round(championRegressionData[championName]['winrateWeight'], 2)
            champKDAWeight = round(championRegressionData[championName]['kdaWeight'], 2)
            champMasteryWeight = round(championRegressionData[championName]['masteryWeight'], 2)
            champConstant = round(championRegressionData[championName]['constant'], 2)
            displayText = f"{championName}'s  Winrate Weight: {champWinrateWeight}, KDA Weight: {champKDAWeight}, Mastery Weight: {champMasteryWeight}, Constant: {champConstant}"
            canvas.create_text(2*self.regressionTextMargin+self.imageSize, self.tabMargin+self.tabHeight+rowCenter, text=displayText, anchor='w', font=self.regressionFont, fill=self.regressionTextColor)

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

    def drawSettings(self, canvas):
        cx = self.width // 2
        for i in range(self.numQueueButtons):
            cy = (2*i+1) * ((self.height-3*self.tabMargin-self.tabHeight) // 8) + self.tabHeight + 2*self.tabMargin
            x0, y0, x1, y1 = cx - self.queueButtonWidth//2, cy - self.queueButtonHeight//2, cx + self.queueButtonWidth//2, cy + self.queueButtonHeight//2
            if i == self.currentQueueButton:
                canvas.create_rectangle(x0, y0, x1, y1, fill=self.backgroundColor, outline=self.outlineColor, width=self.queueButtonMargin)
            else:
                canvas.create_rectangle(x0, y0, x1, y1, fill=self.tabColor, outline=self.outlineColor, width=self.queueButtonMargin)
            canvas.create_text(cx, cy, text=self.queueButtons[i], fill=self.buttonTextColor, font=self.queueButtonFont)

        cy = (2*3+1) * ((self.height-3*self.tabMargin-self.tabHeight) // 8) + self.tabHeight + 2*self.tabMargin
        x0, y0, x1, y1 = cx - self.queueButtonWidth//2, cy - self.queueButtonHeight//2, cx + self.queueButtonWidth//2, cy + self.queueButtonHeight//2
        if self.apiRegression:
            canvas.create_rectangle(x0, y0, x1, y1, fill=self.backgroundColor, outline=self.outlineColor, width=self.queueButtonMargin)
        else:
            canvas.create_rectangle(x0, y0, x1, y1, fill=self.tabColor, outline=self.outlineColor, width=self.queueButtonMargin)
        canvas.create_text(cx, cy, text=self.queueButtons[3], fill=self.buttonTextColor, font=self.queueButtonFont)

    def drawGetRegression(self, canvas):
        cx = self.cx
        cy = (self.cy+self.buttonHeight//2) + (self.height-self.tabMargin-(self.cy+self.buttonHeight//2))//2
        canvas.create_rectangle(cx-(2*self.buttonWidth//3)//2, cy-(2*self.buttonHeight//3)//2, cx+(2*self.buttonWidth//3)//2, cy+(2*self.buttonHeight//3)//2, fill=self.buttonColor, outline=self.outlineColor, width=self.tabMargin)
        canvas.create_text(cx, cy, text='Get API regression', fill=self.buttonTextColor, font=f'Helvetica {(2*self.buttonHeight//3)//6} bold')
    
    def redrawAll(self, canvas):
        self.drawBackground(canvas)
        self.drawTabs(canvas)
        if self.currentTab == 0:
            self.drawTitle(canvas)
            self.drawButton(canvas)
            self.drawGetRegression(canvas)
        elif self.readyToProceed and self.currentTab == 1:
            self.drawData(canvas)
        elif self.readyToProceed and self.currentTab == 2:
            self.drawRegression(canvas)
        elif self.currentTab == 3:
            self.drawInstructions(canvas)
        elif self.currentTab == 4:
            self.drawAnalysis(canvas)
        elif self.currentTab == 5:
            self.drawSettings(canvas)
    
def main():
    # regression without api
    '''
    allChampionRegressions = findChampionRegressions()
    with open('championRegressionData.json', 'w') as championRegressions:
        json.dump(allChampionRegressions, championRegressions, indent=2, cls=PickrateRegressionEncoder)
    '''

    clashGrabUI(width=704, height=400)

if (__name__ == '__main__'):
    main()