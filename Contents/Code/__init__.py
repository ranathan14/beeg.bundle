NAME = 'beeg'
BASE_URL = 'http://beeg.com'
SECTION_URL = 'http://beeg.com/section/%s/%%d/'
TAG_URL = 'http://beeg.com/tag/%s/%%d/'
THUMB_URL = 'http://cdn.anythumb.com/640x360/%s.jpg'
THUMB_URL_ORIG = 'http://cdn.anythumb.com/236x177/%s.jpg'

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

RE_VIDEO_IDS = Regex('var tumb_id.*=.*\[(.+?)\];')
RE_TITLES = Regex('var tumb_alt.*=.*\[(.+?)\];')

####################################################################################################
def Start():

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME
	DirectoryObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR * 4
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.2.3 (KHTML, like Gecko) Version/8.0.1 Safari/600.2.3'

####################################################################################################
@handler('/video/beeg', NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer()

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

	oc = ObjectContainer(title2=title)
	page = HTTP.Request(url % page).content

	ids = RE_VIDEO_IDS.search(page).group(1).split(",")
	titles = RE_TITLES.search(page).group(1).strip("'").split("','")

	for i, id in enumerate(ids):
		oc.add(VideoClipObject(
			url = '%s/%s' % (BASE_URL, id),
			title = titles[i].decode('string_escape'),
			thumb = Resource.ContentsOfURLWithFallback([THUMB_URL % (id), THUMB_URL_ORIG % (id)], fallback='icon-default.jpg')
		))

	return oc

####################################################################################################
@route('/video/beeg/tags')
def Tags(title):

	oc = ObjectContainer(title2=title)

	for tag in HTML.ElementFromURL(BASE_URL).xpath('//a[contains(@href, "/tag/")]'):
		title = tag.xpath('./text()')[0]
		href = tag.xpath('./@href')[0].split('/')[-1].replace('%', '%%')

		oc.add(DirectoryObject(
			key = Callback(Videos, title=title, url=TAG_URL % href),
			title = title
		))

	oc.objects.sort(key=lambda obj: obj.title)

	return oc
