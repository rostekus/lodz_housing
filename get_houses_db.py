from bs4 import BeautifulSoup
from requests import get
from lxml import etree


URL = 'https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/lodz/'

class FLat():
	pass


class OlxBot:


	def __init__(self, base_url = URL):
		self.base_url = base_url  # URL for searching
		#self.curr, self.conn = self.connect_db()

	def search(self):
		page = get(self.base_url)
		soup = BeautifulSoup(page.content, "html.parser")
		dom = etree.HTML(str(soup))
		otodom = []
		olx = []
		for offer in dom.xpath('//*[@id="offers_table"]//h3/a/@href'):
			if offer[13] == 't':
				otodom.append(offer)
			else:
				olx.append(offer)

		
			


	def connect_db(self):
		conn = sqlite3.connect("houses.db")
		curr = conn.cursor()
		#privite,price for m2, floor,furniture, aftermarket, Type of building, 
		#flat area, # of rooms, lenght, olx vs otodom
		curr.execute()
	
		return curr, conn



if '__main__' == __name__:

  bot = OlxBot()
  bot.search()