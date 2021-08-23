from bs4 import BeautifulSoup
from requests import get
from lxml import etree
import re
import csv
import pandas as pd
URL = 'https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/lodz/'


class OlxBot:


	def __init__(self, base_url = URL):
		self.base_url = base_url  # URL for searching

		
		

		
	def search(self):
		page = get(self.base_url)
		soup = BeautifulSoup(page.content, "html.parser")
		dom = etree.HTML(str(soup))

		otodom = []
		olx = []

		for offer in dom.xpath('//*[@id="offers_table"]//h3/a/@href'):
			#check if offer is on the olx site or otodom
			if offer[13] == 't':
				otodom.append(offer)
			else:
				olx.append(offer)

		print(len(olx))
		with open('data.csv', 'w') as f:
			writer = csv.writer(f)
			

			for offer in olx:
			
				flat = self.flat_info(offer)
				writer.writerow(flat)

		
	
		colums = ['price','seller', 'price_for_m2','floor','district', 'furniture','market',
			'building','area', 'num_of_rooms', 'num_of_photos', 'description']
		df = pd.read_csv('data.csv', header=None)
		df.to_csv('data.csv', header=colums, index=True)

	
	def flat_info(self, url):
		page = get(url)
		soup = BeautifulSoup(page.content, "html.parser")
		dom = etree.HTML(str(soup))

		flat = []
		offer = dom.xpath('//ul/li/p')
		
		

		price = dom.xpath("//div/h3[@class = 'css-okktvh-Text eu5v0x0']")[0].text
		flat.append(price)

		seller =offer[0].text
		flat.append(seller)
		
		price_for_m2 = float(re.match('Cena za m²: (.*?) zł/m²',offer[1].text).group(1))
		flat.append(price_for_m2)

		floor  = re.match('Poziom: (.*?)$',offer[2].text).group(1)
		flat.append(floor)

		district = dom.xpath('//title')[0].text
		district = re.match('(.*?) Łódź (.*?) • OLX.pl',district).group(2)
		flat.append(district)

		furniture = re.match('Umeblowane: (.*?)$',offer[3].text).group(1)
		flat.append(furniture)

		market = re.match('Rynek: (.*?)$',offer[4].text).group(1)
		flat.append(market)

		building = re.match('Rodzaj zabudowy: (.*?)$',offer[5].text).group(1)
		flat.append(building)

		area = re.match('Powierzchnia: (.*?) m²',offer[6].text).group(1)
		flat.append(area)

		num_of_rooms =  re.match('Liczba pokoi: (.*?) (.*?)$',offer[7].text).group(1)
		flat.append(num_of_rooms)

		_ = len(re.findall('<div class="swiper-zoom-container"><img alt=',str(soup)))
		if _ == 0:
			num_of_photos = 0
		else:
			num_of_photos = _ +1
		
		flat.append(num_of_photos)

		description = len(dom.xpath('//div[@class = "css-g5mtbi-Text"]')[0].text)
		flat.append(description)
		
		return flat
		
		

		





if '__main__' == __name__:

  bot = OlxBot()
  bot.search()