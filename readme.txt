# Clash Grab
## Project Summary
Clash Grab is a 15-112 Term Project meant to help with the drafting stage of the game league of legends: specifically targetted towards the draft phase in the gamemode "Clash".  

It gathers raw data from Op.gg, specifically KDA, Winrate, and Pickrate for each champion played in any ranked gamemode (Summoner's Rift 5v5 or Flex). This data is gathered from 50 Summoners from each division of the Gold rank. These along with champion mastery are used as variables in a Multiple Linear Regression with the independent variables being KDA, Winrate, and Mastery for every champion played by every summoner in the dataset with Pickrate being the associated dependent variable.

## Usage
Note that Riot has a rate limiter on their personal use dvelopment keys, which may cause 2min delays at regular intervals.

You will first have to paste your Riot developer key into the areas labelled 'development key', otherwise the program will not work. A development key will be provided to my TP mentor.

You will want to run "main". On running main, the application will open. At this point the you will want to select the tab "Home". After selecting the "Enter data here" button, a new window will pop up, within which you will enter the Summoner Name of the user who you wish to query. Simply type that in and press enter.

If the summoner name is valid, a popup will confirm that the results are ready. The other tabs will now be available and will display the relevant result information.

Furthermore, if you'd like to query the Clash queue for data to input into the regression instead of Ranked Solo Queue, simply select that option in the "Settings" tab. Furthermore, if you would like to use a regression model derived from API data, simply toggle the "API Regression" button in "Settings". If you'd like to generate and fit a new model from the API, given queue choice, select "Get API regression" in the home screen.

## Libraries
You will need to have the following installed:
1. riotwatcher: https://riot-watcher.readthedocs.io/en/latest/
2. cmu_112_graphics

## Shortcuts
Much of previously gathered data is stored as dictionaries in the .json files within the project contents. Those may provide insight and allow for the skipping of many steps of data processing.

## Cited Pages
1. op.gg
2. https://coolors.co/084887-758bfd-aeb8fe-f1f2f6-416165
3. https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#ioMethods
4. https://docs.python.org/3/library/functions.html#round
5. https://rubikscode.net/2020/10/26/ml-optimization-pt-1-gradient-descent-with-python/
6. https://en.wikipedia.org/wiki/Mean_squared_error#Predictor
7. https://pynative.com/make-python-class-json-serializable/
8. https://riot-watcher.readthedocs.io/en/latest/index.html
9. https://riot-watcher.readthedocs.io/en/latest/
10. https://www.geeksforgeeks.org/working-with-json-data-in-python/
11. https://developer.riotgames.com/apis
12. https://developer.riotgames.com/docs/lol
13. https://fontspool.com/generator/league-of-legends-font