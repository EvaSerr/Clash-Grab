# Clash Grab
## Project Summary
Clash Grab is a 15-112 Term Project meant to help with the drafting stage of the game league of legends: specifically targetted towards the draft phase in the gamemode "Clash".  

It gathers raw data from Op.gg, specifically KDA, Winrate, and Pickrate for each champion played in any ranked gamemode (Summoner's Rift 5v5 or Flex). These along with champion mastery are used as variables in a Multiple Linear Regression with the independent variables being KDA, Winrate, and Mastery for every champion played by every summoner in the dataset with Pickrate being the associated dependent variable.

## Usage
On running main, the application will open. At this point the only selectable tab will be "Home". After selecting the "Enter data here" button, a new window will pop up, within which you will enter the Summoner Name of the user who you wish to query. Subsequently, a new window will pop up asking for the raw data associated with that summoner. The instructions for getting said data are as follows:  
1. Head to Op.gg
2. Search the Summoner Name that was previously enterd
3. Head to the champions tab for that summoner
4. Select Season 2020
5. Open the page inspection
6. Search "tbody.Body" within that page
7. Go to the last entry
8. Copy that header
9. Paste into the entry window
10. Proceed

If the data is correct, a popup will confirm that the results are ready. The other tabs will now be available and will display the relevant result information.

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