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
  dir = MediaContainer()
  

  return dir

