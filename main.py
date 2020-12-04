from parseData import *
from regression import *
from cmu_112_graphics import *

class clashGrabUI(App):
    def appStarted(self):
        self.numTabs = 3
        self.tabWidth = self.width // 8
        self.tabHeight = self.height // 12
        self.tabMargin = min(self.width, self.height) // 200
        self.tabFont = f'Helvetica {self.tabHeight // 4} bold'
        self.tabColor = 'orchid3'
        self.tabTextColor = 'thistle1'

        self.tabs = ['Home', 'Data', 'Regression']
        self.currentTab = 0
        self.inputHTML = ''
        self.summonerQueryName = ''

        self.backgroundColor = 'orchid2'
        self.mainTextColor = 'thistle2'

        self.cx = self.width // 2
        self.cy = self.height // 2
        self.buttonWidth = self.width // 3
        self.buttonHeight = self.height // 4
        self.buttonText = 'Click to enter data'
        self.buttonFont = f'Helvetica {self.buttonHeight // 6} bold'
        self.buttonTextColor = 'thistle1'
        self.buttonColor = 'orchid4'
        self.buttonOutline = min(self.width, self.height) // 100

        self.readyToProceed = False

    def timerFired(self):
        self.numTabs = 3
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

    def mousePressed(self, event):
        if ((self.cx-self.buttonWidth//2 <= event.x <= self.cx+self.buttonWidth//2) and 
        (self.cy-self.buttonHeight//2 <= event.y <= self.cy+self.buttonHeight//2)):
            self.summonerQueryName = self.getUserInput('Insert summoner name here:')
            self.inputHTML = self.getUserInput('Copy summoner champ HTML here: \n  (inspect element find last instance of "tbody.Body")')
            if '<tr class="Row TopRanker" role="row">' not in self.inputHTML.splitlines()[1]:
                self.showMessage('Please go to the Summoner -> Champions tab')
                self.readyToProceed = False
            else:
                dataTxt = open(f'rawInputData/{self.summonerQueryName}.txt', 'w')
                dataTxt.write(self.inputHTML)
                with open('rawInputData/inputSummoners.json', 'r') as inputSummonersRead:
                    currentInputSummoners = json.load(inputSummonersRead)
                    if currentInputSummoners == None:
                        currentInputSummoners = dict()
                with open('rawInputData/inputSummoners.json', 'w') as inputSummonersWrite:
                    currentInputSummoners[self.summonerQueryName] = lol_watcher.summoner.by_name('na1', self.summonerQueryName)['id']
                    currentSummoner = {self.summonerQueryName:lol_watcher.summoner.by_name('na1', self.summonerQueryName)['id']}
                    json.dump(currentInputSummoners, inputSummonersWrite, indent=2)
                
                with open('parsedInputData/inputChampMasteries.json', 'w') as inputChampDataBySummoner:
                    json.dump(findChampMasteries(lol_watcher, currentSummoner), inputChampDataBySummoner, indent=2)

                with open('parsedInputData/InputOPggDataBySummoner.json', 'w') as opggData:
                    json.dump(parseRankedData('rawInputData'), opggData, indent=2)

                combineOpggDataAndMastery('parsedInputData/InputOPggDataBySummoner.json', 'parsedInputData/inputChampMasteries.json', 'parsedInputData/inputChampDataBySummoner.json')

                percentizeMastery('parsedInputData/inputChampDataBySummoner.json')

                addPickrateEntry('parsedInputData/inputChampDataBySummoner.json')

                with open('parsedInputData/inputSummonerDataByChamp.json', 'w') as parsedData:
                    json.dump(convertToByChamp('parsedInputData/inputChampDataBySummoner.json'), parsedData, indent=2)

                self.readyToProceed = True
                self.showMessage('Data is ready')

    def drawTabs(self, canvas):
        for i in range(self.numTabs):
            x0, y0, x1, y1 = self.tabMargin + self.tabWidth*i, self.tabMargin, self.tabMargin + self.tabWidth*(i+1), self.tabMargin + self.tabHeight
            if i == self.currentTab:
                canvas.create_rectangle(x0, y0, x1, y1, fill=self.backgroundColor, outline=self.backgroundColor, width=self.tabMargin)
            else:
                canvas.create_rectangle(x0, y0, x1, y1, fill=self.tabColor, width=self.tabMargin)
            canvas.create_text((x1+x0)//2, (y1+y0)//2, text=self.tabs[i], fill=self.tabTextColor, font=self.tabFont)

    def drawButton(self, canvas):
        canvas.create_rectangle(self.cx-self.buttonWidth//2, self.cy-self.buttonHeight//2, self.cx+self.buttonWidth//2, 
        self.cy+self.buttonHeight//2, fill=self.buttonColor, width=self.buttonOutline)
        canvas.create_text(self.cx, self.cy, text=self.buttonText, fill=self.buttonTextColor, font=self.buttonFont)

    def drawContent(self, canvas):
        # draw background
        xTabsEnd = self.tabMargin + self.tabWidth*self.numTabs
        y0TabsEnd, y1TabsEnd = self.tabMargin, 1.5*self.tabMargin + self.tabHeight
        canvas.create_rectangle(xTabsEnd + self.tabMargin, y0TabsEnd, self.width, y1TabsEnd, fill='orchid4', outline='orchid4', width=self.tabMargin)
        
        canvas.create_rectangle(0, y1TabsEnd, self.width, self.height, fill=self.backgroundColor, outline=self.backgroundColor)
        # canvas.create_line(xTabsEnd, self.tabHeight+self.tabMargin // 2, self.width, self.tabHeight+self.tabMargin // 2, )
    
    def drawData(self, canvas):
        # adfasdfas

    def redrawAll(self, canvas):
        self.drawTabs(canvas)
        self.drawContent(canvas)
        self.drawButton(canvas)
        if self.readyToProceed:
            self.drawData(canvas)
    
def main():
    '''
    allChampionRegressions = findChampionRegressions()
    with open('championRegressionData.json', 'w') as championRegressions:
        json.dump(allChampionRegressions, championRegressions, indent=2, cls=PickrateRegressionEncoder)
    '''

    clashGrabUI(width=704, height=400)

if (__name__ == '__main__'):
    main()