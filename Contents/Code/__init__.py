NAME = 'beeg'
BASE_URL = 'http://beeg.com'
SECTION_URL = 'http://beeg.com/section/%s/%%d/'
TAG_URL = 'http://beeg.com/tag/%s/%%d/'
THUMB_URL = 'http://cdn.anythumb.com/640x360/%s.jpg'

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

RE_VIDEO_IDS = Regex('var tumbid.*=.*\[(.+?)\];')
RE_TITLES = Regex('var tumbalt.*=.*\[(.+?)\];')

####################################################################################################
def Start():

	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME
	DirectoryObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR * 4
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'

####################################################################################################
@handler('/video/beeg', NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer(view_group='List')

	oc.add(DirectoryObject(
		key = Callback(Videos, title='Browse All Videos', url=SECTION_URL % 'home'),
		title = 'Browse All Videos'
	))

	oc.add(DirectoryObject(
		key = Callback(Tags, title='Browse Videos by Tag'),
		title = 'Browse Videos by Tag'
	))

	return oc

####################################################################################################
@route('/video/beeg/videos', page=int)
def Videos(title, url, page=1):

	oc = ObjectContainer(title2=title, view_group='List')
	page = HTTP.Request(url % page).content

	ids = RE_VIDEO_IDS.search(page).group(1).split(",")[0:50]
	titles = RE_TITLES.search(page).group(1).strip("'").split("','")[0:50]

	for i, id in enumerate(ids):
		oc.add(VideoClipObject(
			url = '%s/%s' % (BASE_URL, id),
			title = titles[i].decode('string_escape'),
			thumb = Callback(GetThumb, url=THUMB_URL % id)
		))

	return oc

####################################################################################################
@route('/video/beeg/tags')
def Tags(title):

	oc = ObjectContainer(title2=title, view_group='List')

	for tag in HTML.ElementFromURL(BASE_URL).xpath('//a[contains(@href, "/tag/")]'):
		title = tag.xpath('./text()')[0]
		href = tag.xpath('./@href')[0].split('/')[-1].replace('%', '%%')

		oc.add(DirectoryObject(
			key = Callback(Videos, title=title, url=TAG_URL % href),
			title = title
		))

	oc.objects.sort(key=lambda obj: obj.title)

	return oc

####################################################################################################
def GetThumb(url):

	try:
		data = HTTP.Request(url, cacheTime=CACHE_1MONTH, sleep=0.5).content
		return DataObject(data, 'image/jpeg')
	except:
		pass

	return Redirect(R(ICON))
