import re

NAME = 'beeg.com'
BASE_URL = 'http://beeg.com'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_MORE = 'icon-more.png'

####################################################################################################
def Start():

	Plugin.AddPrefixHandler('/video/beeg', MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

	MediaContainer.art = R(ART)
	MediaContainer.title1 = NAME
	MediaContainer.viewGroup = 'InfoList'
	MediaContainer.userAgent = ''
	DirectoryItem.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0'

###################################################################################################
def MainMenu():

	dir = MediaContainer()

	for category in HTML.ElementFromURL(BASE_URL).xpath('//*[@class="menu" or @class="menu-extra"]//a[contains(@href, "http://")]'):
		url = category.get('href')
		try:
			title = category.xpath('.//span')[0].text.strip()
		except:
			title = category.text.strip()

		if title == 'Home':
			title = 'All'

		dir.Append(Function(DirectoryItem(Videos, title=title), title=title, url=url))

	return dir

####################################################################################################
def Videos(sender, title, url, page=1):

	dir = MediaContainer(title2=title, httpCookies=HTTP.CookiesForURL(BASE_URL))
	page_url = '%s%d/' % (url, page)
	html = HTML.ElementFromURL(page_url)

	for video in html.xpath('//div[@id="thumbs"]/a'):
		video_url = video.get('href')
		video_title = video.xpath('./img')[0].get('alt').strip()
		video_thumb = video.xpath('./img')[0].get('src').replace('192x144', '240x180')

		dir.Append(Function(VideoItem(PlayVideo, title=video_title, thumb=Function(GetThumb, url=video_thumb)), url=video_url))

	if (len(html.xpath('//div[@id="pagerBox"]/a')) > page):
		dir.Append(Function(DirectoryItem(Videos, title='Next page...', thumb=R(ICON_MORE)), title=title, url=url, page=page+1))

	return dir

####################################################################################################
def PlayVideo(sender, url):

	page = HTTP.Request(url).content
	video_url = re.search("'file':(\s)*'(?P<video_url>[^']+)'", page).group('video_url')
	return Redirect(video_url)

####################################################################################################
def GetThumb(url):

	try:
		data = HTTP.Request(url, cacheTime=CACHE_1MONTH, sleep=1).content
		return DataObject(data, 'image/jpeg')
	except:
		pass

	return Redirect(R(ICON))
