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

# background image is from http://commons.wikimedia.org/wiki/File:Justice_in_concert.jpg
# icon/cover by Jay Del Turco

import re, string
import datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *


LMA_PREFIX   = "/music/LMA"

CACHE_INTERVAL = 3600


###################################################################################################
def Start():
  Plugin.AddPrefixHandler(LMA_PREFIX, MainMenu, 'Live Music Archive', 'icon-default.png', 'art-default.png')
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  MediaContainer.title1 = 'Live Music Archive'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.png')
  DirectoryItem.thumb=R('nothing.png')

  HTTP.SetCacheTime(CACHE_INTERVAL)

###################################################################################################

def CreatePrefs():
  Prefs.Add(id='lossless', type='bool', default=True, label='Prefer Lossless (Flac16, SHN)')
  Prefs.Add(id='flac24', type='bool', default=False, label='Prefer FLAC24 if Available (needs fairly good internet connection)')
  Prefs.Add(id='itunesIP', type='text',default='127.0.0.1', label='IP address of iTunes library')

def MainMenu():
	dir = MediaContainer(viewGroup='List')
	mainPage = XML.ElementFromURL("http://www.archive.org/details/etree", isHTML=True, errors="ignore")
	dir.Append(Function(DirectoryItem(letters, title="Browse Archive by Artist")))
	dir.Append(Function(InputDirectoryItem(showList, title="Seach the Live Music Archive", prompt="Search..."), title2="Search Results"))
	now = datetime.datetime.now()
	month = str(now.month)
	day = str(now.day)
	if now.month < 10:
		month = '0' + month
	if now.day < 10:
		day = '0' + day
	todayURL = "http://www.archive.org/search.php?query=collection:etree%20AND%20%28date:19??-"+month+"-"+day+"%20OR%20date:20??-"+month+"-"+day+"%29&sort=-/metadata/date"
	dir.Append(Function(DirectoryItem(showList, title='Shows This Day in History'), title2="This Day in History", pageURL=todayURL))

	dir.Append(Function(DirectoryItem(showList, title="Most Recently Added Shows"), title2="Recently Added Shows", pageURL="http://www.archive.org/search.php?query=collection%3Aetree&sort=-%2Fmetadata%2Fpublicdate"))
#	dir.Append(Function(DirectoryItem(newArtists, title="Recently Added Artists",))) # useless since most are empty
	dir.Append(Function(DirectoryItem(showList, title="Most Downloaded Shows"), title2="Most Downloaded", pageURL="http://www.archive.org/search.php?query=%28%28collection%3Aetree%20OR%20mediatype%3Aetree%29%20AND%20NOT%20collection%3AGratefulDead%29%20AND%20-mediatype%3Acollection&sort=-downloads"))
	dir.Append(Function(DirectoryItem(showList, title="Most Downloaded Shows Last Week"), title2="Last Week", pageURL="http://www.archive.org/search.php?query=%28%28collection%3Aetree%20OR%20mediatype%3Aetree%29%20AND%20NOT%20collection%3AGratefulDead%29%20AND%20-mediatype%3Acollection&sort=-week"))
	dir.Append(Function(DirectoryItem(staff, title="Staff Picks")))

#	spotlightURL = str(mainPage.xpath("//div[@id='spotlight']/a/@href")).strip("[]'")
#	name = str(mainPage.xpath("//div[@id='spotlight']/a/text()")).strip("[]'")
#	dir.Append(Function(DirectoryItem(concert, title="Spotlight Show", summary=name, thumb=R('nothing.png')), page=spotlightURL, showName=name))

	dir.Append(Function(DirectoryItem(itunes, title="Find Shows for Artists in My iTunes Library")))

	dir.Append(PrefsItem("Preferences...", thumb=R('nothing.png')))
	return dir	

##################################################################################################
def letters(sender):
	dir = MediaContainer(title2="Artists", viewGroup='List')
	dir.Append(Function(DirectoryItem(artists, title="#"), letter='#'))
	for c in string.ascii_uppercase:
		dir.Append(Function(DirectoryItem(artists, title=c,), letter=c))
	
	return dir



def artists(sender, letter=None):
	dir = MediaContainer(title2="Artists-" + str(letter), viewGroup='List',)

	artistsURL = "http://www.archive.org/advancedsearch.php?q=mediatype%3Acollection+collection%3Aetree&fl[]=collection&fl[]=identifier&fl[]=mediatype&sort[]=identifier+asc&sort[]=&sort[]=&rows=5000&fmt=xml&xmlsearch=Search#raw"
	artistsList = XML.ElementFromURL(artistsURL, errors='ignore',)
	artists = artistsList.xpath("//str[@name='identifier']/text()")
	for identifier in artists:
		identifier = str(identifier)
		if letter=="#":
			for n in string.digits:
				if identifier[0] == n:
					pageURL= "http://www.archive.org/search.php?query=collection%3A" + identifier + "&sort=-date&page=1"
					dir.Append(Function(DirectoryItem(showList, title=identifier), pageURL=pageURL, title2=identifier, isArtistPage=True, identifier=identifier))
		else:
			if identifier[0] == letter:
				pageURL= "http://www.archive.org/search.php?query=collection%3A" + identifier + "&sort=-date&page=1"
				dir.Append(Function(DirectoryItem(showList, title=identifier), pageURL=pageURL, title2=identifier, isArtistPage=True, identifier=identifier))

	return dir

def showList(sender, title2, pageURL=None, isArtistPage=False, identifier=None, query=None):
	dir = MediaContainer(title2=title2, viewGroup='List')
	if query != None:
		query = String.URLEncode(query)
		pageURL="http://www.archive.org/search.php?query="+query+"%20AND%20collection%3Aetree"
	
	
	showsList = XML.ElementFromURL(pageURL, isHTML=True, errors='ignore',)
	if showsList != None:

		# auto detect show numbers and split by year if high
		if isArtistPage == True:
			numShows = showsList.xpath("//div[3]//tr[2]//td[1]//b[2]//text()")
			if numShows != []:
				numShows = int(numShows[0].replace(",",""))
				if numShows >= 51:
					# get the years list
					yearsPage = XML.ElementFromURL("http://www.archive.org/browse.php?collection=" + identifier + "&field=year", isHTML=True, errors="ignore")
					years = yearsPage.xpath("//table[@id='browse']//ul//a/text()")
					yearURLs = yearsPage.xpath("//table[@id='browse']//ul//a/@href")
					for year, url in zip(years, yearURLs):
						dir.Append(Function(DirectoryItem(showList, title=str(year)), title2=str(year), pageURL="http://www.archive.org" + url + "&sort=date",))
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
		dir.Append(TrackItem("http://www.archive.org" + url, title=title, artist=artist, album=album, thumb=R('icon-default.png')))
	
	
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


def newArtists(sender):
	# useless since most are empty
	
	dir = MediaContainer(title2="New Artists")
	page = XML.ElementFromURL("http://www.archive.org/search.php?query=mediatype%3Acollection%20collection%3Aetree&sort=-%2Fmetadata%2Faddeddate", isHTML=True, errors="ignore")
	names = page.xpath("//a[@class='titleLink']/text()")
	urls = page.xpath("//a[@class='titleLink']/@href")
	for name, url in zip(names, urls):
		identifier = str(name).replace("/details/", "")
		pageURL= "http://www.archive.org/search.php?query=collection%3A" + identifier + "&sort=-date&page=1"
		dir.Append(Function(DirectoryItem(showList, title=str(name)), title2=str(name), pageURL=pageURL, isArtistPage=True))
	
	return dir

def itunes(sender):
	dir = MediaContainer(title2="itunes", title3="title3")
	itunesURL = "http://" + Prefs.Get('itunesIP') + ":32400/music/iTunes/Artists"
	itunesArtistsPage = XML.ElementFromURL(itunesURL, errors='ignore')
	itunesArtists = itunesArtistsPage.xpath('//Artist/@artist')
	Log(itunesArtists)
	
	return dir


