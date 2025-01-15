# FBRef Stats
### A python script to scrape football data from [FBRef]
#### Check out the [documentation](https://github.com/mbrahimi25/fbrefstats/blob/main/DOCUMENTATION.md)

![Static Badge](https://img.shields.io/badge/License-GNU-red) ![Static Badge](https://img.shields.io/badge/Python-yellow)

### About
FBRef Stats is a Python script which uses *BeautifulSoup* and *requests* to scrape data from [FBRef].
This is a small side project I work on in my free time. As an avid soccer fan and someone who finds sports stats interesting, I tried making a program which takes player stats into account so I could gain an advantage on my fantasy leagues with my friends. However, I could not find many good free libraries which provided soccer data, so I resolved to build one myself.


### Installation
As of now, the project is not available as a standalone library. To use this product currently, you can **download the script** and import it into any other Python scripts you wish to use using:
```sh
from fbrefstats import LeagueScraper, GeneralScraper, StatStrings
```

### Usage
As seen above, there are three classes within the ```fbrefstats``` script:
(The names of these classes may change in the future, they are currently placeholders)
- ```LeagueScraper```
  - Contains scraping methods relating to leagues. An object is needed to access these methods, with each object representing a specific league.
- ```GeneralScraper```
  - Contains scraping methods that are *independant*. They are static and do not tie into any specific league.
- ```StatStrings```
  - Class full of variables holding strings, which are used when calling the method ```LeagueScraper.getLeagueLeaders()```

**Check out the [documentation](DOCUMENTATION.md) for info on how to use the script.**

### Other libraries used
As of now, the libraries used within this project are:
- ```BeautifulSoup4```
- ```requests```
- ```pandas```
- ```StringIO```
- ```fake-http-reader``` | Link to the repo [here](https://github.com/MichaelTatarski/fake-http-header)

### To-do
As of right now, this script is still in a very early development phase, and I am only working on it as a personal side project. I have a few things I am thinking of adding:

- **Update ```README.md``` (Urgent)** ☑
- **Add a documentation file** ☑
- **Update [the documentation file](DOCUMENTATION.md)** ☑
- **Static functions** ☑\
Split the ```Scraper``` class into two classes: ```LeagueScraper``` and ```GeneralScraper```, which contains **static methods**
- **Randomized ```requests``` headers to avoid detectability when scraping** ☑
- **Different table formats** ☑\
I've learnt that pandas dataframes already have built-in functions for this: ```pandas.DataFrame.to_csv()``` and ```pandas.DataFrame.to_string()```

- **Turn *FBScraper* into a library** ☐\
I have never made an actual library before, so I would like to research how to turn this into a real installable Python library.

- **More scraping!** ☐\
There is so much data available on [FBRef], so I would love to add more methods so that this data can be accessed through the script

- **Add support for different league formats** ☐\
As of right now, there are very few leagues supported as I am yet to add functionality to leagues with different formats (promotion/relegation playoffs, MLS post-season, or Apertura/Clausura formats commonly found in Latin America)

- **Add nationality argument to ```GeneralScraper.getPlayerLink()```** ☐\
Currently, ```GeneralScraper.getPlayerLink()``` takes one argument: ```inputted_player_name```. The method returns a list of URLs depending on which players were found when searching with ```inputted_player_name```. This can get annoying when there are many players with similar names, so adding a *nationality* argument would be useful for searching.

### License
GNU GPL

[FBRef]: <https://fbref.com>
