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
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.title1 = 'Live Music Archive'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('')
  HTTP.SetCacheTime(CACHE_INTERVAL)

###################################################################################################
def MainMenu():
	dir = MediaContainer(viewGroup='Details')
	dir.Append(Function(DirectoryItem(artists, title="Browse Archive by Artist",)))
#	dir.Append(Function(DirectoryItem(doSearch, title="Seach the Live Music Archive",)))
#	dir.Append(Function(DirectoryItem(today, title="Shows this Day in History",)))
#	dir.Append(Function(DirectoryItem(recent, title="Most Recently Added Shows",)))
#	dir.Append(Function(DirectoryItem(newArtists, title="Recently Added Artists",)))
#	dir.Append(Function(DirectotyItem(mostDown, title="Most Downloaded Shows",)))
#	dir.Append(Function(DirectoryItem(lastWeek, title="Most Downloaded Shows Last Week",)))
#	dir.Append(Function(DirectoryItem(staff, title="Staff Picks",)))

	mainPage = XML.ElementFromURL("http://www.archive.org/details/etree", isHTML=True, errors="ignore")
	spotlightURL = str(mainPage.xpath("//div[@id='spotlight']/a/@href")).strip("[]'")
	name = str(mainPage.xpath("//div[@id='spotlight']/a/text()")).strip("[]'")
	dir.Append(Function(DirectoryItem(concert, title="Spotlight Show", summary=name), page=spotlightURL, showName=name))
	return dir

##################################################################################################


def artists(sender):
	dir = MediaContainer(title2="All Artists")
	
	artistsURL = "http://www.archive.org/advancedsearch.php?q=mediatype%3Acollection+collection%3Aetree&fl[]=collection&fl[]=identifier&fl[]=mediatype&sort[]=titleSorter+asc&sort[]=&sort[]=&rows=50000&fmt=xml&xmlsearch=Search#raw"
	artistsList = XML.ElementFromURL(artistsURL, errors='ignore',)
	artists = artistsList.xpath("//str[@name='identifier']/text()")
	for identifier in artists:
		Log(identifier)
	
	return dir

def showList(sender, identifier):
	
	
	return dir



def concert(sender, page, showName):
	dir = MediaContainer(title2=showName)
	page = XML.ElementFromURL("http://www.archive.org" + page, isHTML=True, errors="ignore")
	artist = str(page.xpath("/html/body/div[3]/a[3]/text()")).strip("[]'")
	album = str(page.xpath("/html/body/div[5]/div/p[1]/span[6]/text()")).strip("[]'")
	tracks = page.xpath("//table[@id='ff2']//td[5]/a/@href")
	if tracks != []:
		names = page.xpath("//table[@id='ff2']//td[5]/a/parent::*/parent::*/td[1]/text()")
		for track, name in zip(tracks, names):
			dir.Append(TrackItem("http://www.archive.org" + track, title=name, artist=artist, album=album))
	elif tracks == []:
		Log("bad xpath or no mp3s")	
	
	
	return dir



