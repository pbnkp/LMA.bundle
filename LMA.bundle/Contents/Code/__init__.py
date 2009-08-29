#Live Music Archive (from archive.org) plugin for plex media server

# copyright 2009 Billy Joe Poettgen
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re, string
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

LMA_PREFIX   = "/music/LMA"

CACHE_INTERVAL = 3600


###################################################################################################
def Start():
  Plugin.AddPrefixHandler(LMA_PREFIX, MainMenu, 'Live Music Archive', '', '')
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  MediaContainer.title1 = 'Live Music Archive'
  MediaContainer.content = 'Items'
  MediaContainer.art = ''
  Prefs.Add('lossless', 'bool', 'false', L("Prefer Lossless (FLAC16, SHN)"))
  Prefs.Add('flac24', 'bool', 'false', L("Prefer FLAC24 if available (needs pretty fast internet connecion)"))
  HTTP.SetCacheTime(CACHE_INTERVAL)

###################################################################################################
def MainMenu():
	dir = MediaContainer(viewGroup='InfoList')
	dir.Append(Function(DirectoryItem(artists, title="Browse Archive by Artist",)))
#	dir.Append(Function(DirectoryItem(doSearch, title="Seach the Live Music Archive",)))
#	dir.Append(Function(DirectoryItem(today, title="Shows this Day in History",)))
	dir.Append(Function(DirectoryItem(showList, title="Most Recently Added Shows",), title2="Recently Added Shows", pageURL="http://www.archive.org/search.php?query=collection%3Aetree&sort=-%2Fmetadata%2Fpublicdate"))
#	dir.Append(Function(DirectoryItem(newArtists, title="Recently Added Artists",)))
	dir.Append(Function(DirectoryItem(showList, title="Most Downloaded Shows"), title2="Most Downloaded", pageURL="http://www.archive.org/search.php?query=%28%28collection%3Aetree%20OR%20mediatype%3Aetree%29%20AND%20NOT%20collection%3AGratefulDead%29%20AND%20-mediatype%3Acollection&sort=-downloads"))
	dir.Append(Function(DirectoryItem(showList, title="Most Downloaded Shows Last Week",), title2="Last Week", pageURL="http://www.archive.org/search.php?query=%28%28collection%3Aetree%20OR%20mediatype%3Aetree%29%20AND%20NOT%20collection%3AGratefulDead%29%20AND%20-mediatype%3Acollection&sort=-week"))
	dir.Append(Function(DirectoryItem(staff, title="Staff Picks",)))

	mainPage = XML.ElementFromURL("http://www.archive.org/details/etree", isHTML=True, errors="ignore")
	spotlightURL = str(mainPage.xpath("//div[@id='spotlight']/a/@href")).strip("[]'")
	name = str(mainPage.xpath("//div[@id='spotlight']/a/text()")).strip("[]'")
	dir.Append(Function(DirectoryItem(concert, title="Spotlight Show", summary=name), page=spotlightURL, showName=name))
	dir.Append(PrefsItem("Preferences..."))
#	dir.Append(Function(DirectoryItem(concert, title="test"), page="/details/eo2004-09-19_24bit", showName="test"))
	return dir	

##################################################################################################


def artists(sender):
	dir = MediaContainer(title2="All Artists", viewGroup='List', letter=None)
	
	artistsURL = "http://www.archive.org/advancedsearch.php?q=mediatype%3Acollection+collection%3Aetree&fl[]=collection&fl[]=identifier&fl[]=mediatype&sort[]=titleSorter+asc&sort[]=&sort[]=&rows=50000&fmt=xml&xmlsearch=Search#raw"
	artistsList = XML.ElementFromURL(artistsURL, errors='ignore',)
	artists = artistsList.xpath("//str[@name='identifier']/text()")
	for identifier in artists:
		identifier = str(identifier)
		pageURL= "http://www.archive.org/search.php?query=collection%3A" + identifier + "&sort=-date&page=1"
		dir.Append(Function(DirectoryItem(showList, title=identifier), pageURL=pageURL, title2=identifier, isArtistPage=True, identifier=identifier))
	return dir

def showList(sender, title2, pageURL, isArtistPage=False, identifier=None, byDate=False):
	dir = MediaContainer(title2=title2, viewGroup='List')
	showsList = XML.ElementFromURL(pageURL, isHTML=True, errors='ignore')
	if showsList != None:

			#experiment to auto detect show numbers and split by year if high
		if isArtistPage == True:
			numShows = showsList.xpath("//div[3]//tr[2]//td[1]//b[2]//text()")
			if numShows != []:
				numShows = int(numShows[0].replace(",",""))
				Log(numShows)
				if numShows >= 51:
					# get the years list
					yearsPage = XML.ElementFromURL("http://www.archive.org/browse.php?collection=" + identifier + "&field=year", isHTML=True, errors="ignore")
					years = yearsPage.xpath("//table[@id='browse']//ul//a/text()")
					yearURLs = yearsPage.xpath("//table[@id='browse']//ul//a/@href")
					for year, url in zip(years, yearURLs):
						dir.Append(Function(DirectoryItem(showList, title=str(year)), title2=str(year), pageURL="http://www.archive.org" + url + "&sort=date", byDate=True))
					return dir


		showURLs = showsList.xpath("//a[@class='titleLink']/@href")
		showTitles = showsList.xpath("//a[@class='titleLink']")
		# pain in my fucking ass roundabout way to get propper show titles for artists split by date
		titles = []
		for i in range(len(showTitles)):
			y = showsList.xpath("//table[@class='resultsTable']//tr[%i]/td[2]/a[1]//text()" % (i+1))
			# the +1 is because python list indexes start from 0 and indexes in xpath start at 1
			title = ''.join(y)
			titles.append(title)
		
		for url, title in zip(showURLs, titles):				
				
			dir.Append(Function(DirectoryItem(concert, title=str(title)), page=str(url), showName=str(title)))

		next = showsList.xpath("//a[text()='Next']/@href")
		if next != []:
			pageURL = "http://www.archive.org" + next[0]
			dir.Append(Function(DirectoryItem(showList, title="Next 50 Results"), pageURL=pageURL, title2=title2))

	return dir



def concert(sender, page, showName):
	dir = MediaContainer(title2=showName)
	page = XML.ElementFromURL("http://www.archive.org" + page, isHTML=True, errors="ignore")
	artist = str(page.xpath("/html/body/div[3]/a[3]/text()")).strip("[]'")
	album = str(page.xpath("/html/body/div[5]/div/p[1]/span[6]/text()")).strip("[]'")
	urls = []
	
	#get mp3
	media_type = page.xpath("//table[@id='ff2']//tr[1]//td[text()='VBR MP3']")
	if media_type != []:
		i = len(media_type[0].xpath('preceding-sibling::*')) 
		urls = page.xpath("//table[@id='ff2']//tr/td[%i]/a/@href" % (i+1))
		Log("found mp3s")
	
	
	#get flac16, shn
	if Prefs.Get('lossless') == True:
		media_type = page.xpath("//table[@id='ff2']//tr[1]//td[text()='Flac']")
		Log("looking for Flac")
		if media_type != []:
			i = len(media_type[0].xpath('preceding-sibling::*')) 
			urls = page.xpath("//table[@id='ff2']//tr/td[%i]/a/@href" % (i+1))
			Log("found Flacs")
		elif media_type == []:
			media_type = page.xpath("//table[@id='ff2']//tr[1]//td[text()='Shorten']")
			Log("looking for shorten")
			if media_type != []:
				i = len(media_type[0].xpath('preceding-sibling::*')) 
				urls = page.xpath("//table[@id='ff2']//tr/td[%i]/a/@href" % (i+1))
				Log("found shn")

	#Get FLAC24
	if Prefs.Get('flac24') == True:
		media_type = page.xpath("//table[@id='ff2']//tr[1]//td[text()='24bit Flac']")
		Log("looking for Flac24")
		if media_type != []:
			i = len(media_type[0].xpath('preceding-sibling::*')) 
			urls = page.xpath("//table[@id='ff2']//tr/td[%i]/a/@href" % (i+1))
			Log("found Flac24")
	
	#get titles
	titles = page.xpath("//table[@id='ff2']//td[1]/text()")
	if titles != []:
		del titles[0]
	
	#append tracks
	for url, title in zip(urls, titles):
		dir.Append(TrackItem("http://www.archive.org" + url, title=title, artist=artist, album=album))
	
	
	return dir

# staff picks top level menu
def staff(sender):
	dir = MediaContainer(title2="Staff Picks")
	page = XML.ElementFromURL("http://www.archive.org/details/etree", isHTML=True, errors="ignore")
	titles = page.xpath("//div[@id='picks']//a//text()")
	urls = page.xpath("//div[@id='picks']//a//@href")
	for url, title in zip(urls, titles):
		dir.Append(Function(DirectoryItem(concert, title=str(title)), page=str(url), showName=str(title)))



	return dir
