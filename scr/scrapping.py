from bs4 import BeautifulSoup
from requests import get
from lxml import etree
import re
import csv
import pandas as pd
from numpy import NAN
from datetime import date
URL = 'https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/lodz/'
#TODO:
# find all features in otodom form 




class Bot:


	def __init__(self, base_url_olx = URL, base_url_otodom  = OTO_URL):
		f = open('data.csv', 'w')
		f.close()
		self.base_url = base_url_olx  # URL for searching
		self.base_url_oto = base_url_otodom

		today = date.today()
		self.olx_filename = f'olx_{today}'
		self.otodom_filename = f'otodom_{today}'



	def search_olx(self):

		page = get(self.base_url)
		i = 1
		while page.status_code == 200:
			soup = BeautifulSoup(page.content, "html.parser")
			dom = etree.HTML(str(soup))


			flat_list = []

			for offer in dom.xpath('//*[@id="offers_table"]//h3/a/@href'):
				#check if offer is on the olx site or otodom
				if offer[13] != 't':
					flat_list.append(offer)

			self.write_flat_to_csv(flat_list, self.flat_info_olx, self.olx_filename)
			i += 1
			url = self.base_url + f'?page={i}'

			page = get(url, allow_redirects=False)
			colums = ['price', 'price_for_m2','floor','district', 'furniture','market',
			'building','area', 'num_of_rooms', 'num_of_photos', 'description']
			df = pd.read_csv('data.csv', header=None)
			df.to_csv('data.csv', header=colums, index=True)



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
			flat.append(NAN)
        
		flat.append(self.get_feature_olx('Umeblowane: (.*?)$',offer[3-i].text))

		try:
            furniture = re.match('Umeblowane: (.*?)$',ootodomffer[3-i].text).group(1)
            flat.append(furniture)
        except AttributeError:
            flat.append(NAN)
		    
        try:
            flat.append(self.get_feature_olx('Rynek: (.*?)$',offer[4-i].text))
        except AttributeError:
			flat.append(NAN)
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

	


	def get_feature_olx(self,pattern,offer):
		try:
			return re.match(pattern,offer).group(1)
		except AttributeError:
			return NAN





	def flat_info_otodom(self):

		pass


	def write_flat_to_csv(self, flats, flat_info, filename):
		with open(filename, 'a') as f:
			writer = csv.writer(f)

			for flat in flats:
				flat = flat_info(flat)
				if flat:
					print(flat)
					try:
						writer.writerow(flat)
					except:
						print(f"Couldnt write {flat}")



if '__main__' == __name__:

  bot = Bot()
  bot.search_olx()