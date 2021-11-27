from bs4 import BeautifulSoup
from requests import get
from lxml import etree
import re
import csv
import pandas as pd
from numpy import NAN
URL = 'https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/lodz/'
OTO_URL = 'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/lodz?by=LATEST&direction=DESC&limit=72&page='

class Bot:


	def __init__(self, base_url_olx = URL, base_url_otodom  = OTO_URL):
		f = open('data.csv', 'w')
		f.close()
		self.base_url = base_url_olx  # URL for searching
		self.base_url_oto = base_url_otodom


	def search_olx(self):

		page = get(self.base_url)
		i = 1
		while page.status_code == 200:
			soup = BeautifulSoup(page.content, "html.parser")
			dom = etree.HTML(str(soup))


			olx = []

			for offer in dom.xpath('//*[@id="offers_table"]//h3/a/@href'):
				#check if offer is on the olx site or otodom
				if offer[13] != 't':
					olx.append(offer)


			with open('data.csv', 'a') as f:
				writer = csv.writer(f)


				for offer in olx:

					flat = self.flat_info_olx(offer)
					if flat:
						print(flat)
						try:
							writer.writerow(flat)
						except:
							print(f"Couldnt write {flat}")



			i += 1
			url = self.base_url + f'?page={i}'

			page = get(url, allow_redirects=False)
		colums = ['price', 'price_for_m2','floor','district', 'furniture','market',
			'building','area', 'num_of_rooms', 'num_of_photos', 'description']
		df = pd.read_csv('data.csv', header=None)
		df.to_csv('data.csv', header=colums, index=True)

	# TODO:
	# error in district


	def flat_info_olx(self, url):
		page = get(url)
		#print(page, url)
		soup = BeautifulSoup(page.content, "html.parser")
		#print('fds', len(re.findall('Ups! Coś poszło nie tak...', str(soup))))

		dom = etree.HTML(str(soup))

		flat = []

		offer = dom.xpath('//ul/li/p')


		try:
			price = dom.xpath("//div/h3[@class = 'css-okktvh-Text eu5v0x0']")[0].text
			flat.append(price)
		except IndexError:
			return



		flat.append(self.get_feature_olx('Cena za m²: (.*?) zł/m²',offer[1].text))


		floor  = re.match('Poziom: (.*?)$',offer[2].text)
		if floor:
			flat.append(floor.group(1))
			i = 0
		else:
			flat.append(NAN)
			i = 1
		district = dom.xpath('//title')[0].text
		try:
			district = re.match('(.*?) Łódź (.*?) • OLX.pl',district).group(2)
			flat.append(district)
		except AttributeError:
			return NAN

		flat.append(self.get_feature_olx('Umeblowane: (.*?)$',offer[3-i].text))

		#furniture = re.match('Umeblowane: (.*?)$',ootodomffer[3-i].text).group(1)

		#flat.append(furniture)

		flat.append(self.get_feature_olx('Rynek: (.*?)$',offer[4-i].text))

		flat.append(self.get_feature_olx('Rodzaj zabudowy: (.*?)$',offer[5-i].text))


		flat.append(self.get_feature_olx('Powierzchnia: (.*?) m²',offer[6-i].text))

		flat.append(self.get_feature_olx('Liczba pokoi: (.*?) (.*?)$',offer[7-i].text))

		_ = len(re.findall('<div class="swiper-zoom-container"><img alt=',str(soup)))
		if _ == 0:
			num_of_photos = 0
		else:
			num_of_photos = _ +1

		flat.append(num_of_photos)

		description = len(dom.xpath('//div[@class = "css-g5mtbi-Text"]')[0].text)
		flat.append(description)

		return flat

	def search_otodom(self):
		i = 1
		page = get(self.base_url_oto+'1')
		soup = BeautifulSoup(page.content, "html.parser")



		while page.status_code == 200 and i <=3:
			soup = BeautifulSoup(page.content, "html.parser")
			dom = etree.HTML(str(soup))

			# with open('file.html', 'w') as f:
			# 	f.write(soup.prettify())

			otodom = []



			pattern = re.compile(r'<a class="css-137nx56 es62z2j27" data-cy="listing-item-link" data-cy-viewed="false" href="(.*)">')
			for m in re.finditer(pattern, str(soup.prettify())):
				otodom.append('https://www.otodom.pl' + m.group(1))
			print(f'PAGE {i}  !!!!!!!!!')
			print(otodom)
			i = i+1
			url = self.base_url_oto + f'{i}'
			print(url)
			page = get(url, allow_redirects=False)



	def get_feature_olx(self, pattern:str ,offer: str):
		try:
			return re.match(pattern,offer).group(1)
		except AttributeError:
			return NAN





	def flat_info_otodom(self):
		pass




if '__main__' == __name__:

  bot = Bot()
  bot.search_otodom()
