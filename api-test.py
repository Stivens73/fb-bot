# from geopy.geocoders import Nominatim
import requests
import json
from lxml import html
import re
import zipcode

# search = ZipcodeSearchEngine()


url = 'https://www.neighborhoodscout.com/{}/{}/crime'

state = ''
city = ''

address = '123 Main St, 94720 USA'
postal_code = re.search('(\\d{5})', address).group(0)

myzip = zipcode.isequal(postal_code)
state = myzip.state  
try:
	city = myzip.city.replace(" ", "-")
except Exception as e:
	print(e)

# zipcode = search.by_zipcode(postal_code)
# state = zipcode.State
# city = zipcode.City#.replace(" ", "-")


url = url.format(state, city)




page = requests.get(url)

tree = html.fromstring(page.content)


crime_list = {
	'Crime index:':							'//*[@class="score mountain-meadow"]',
	'Number of violent cases:': 			'//*[@id="data"]/section[1]/div[2]/div[2]/div/div/table/tbody/tr[1]/td[2]/p/strong',
	'Number of property-related cases:':	'//*[@id="data"]/section[1]/div[2]/div[2]/div/div/table/tbody/tr[1]/td[3]/p/strong',
	'Murder:':								'//*[@id="data"]/section[2]/div[5]/div/div/table/tbody/tr[1]/td[2]',
	'Rape:':								'//*[@id="data"]/section[2]/div[5]/div/div/table/tbody/tr[1]/td[3]',
	'Robbery:':								'//*[@id="data"]/section[2]/div[5]/div/div/table/tbody/tr[1]/td[4]',
	'Assault:':								'//*[@id="data"]/section[2]/div[5]/div/div/table/tbody/tr[1]/td[5]'
	
}

other_crimes = {
	'Your chances of becoming a victim of a violent crime:': '//*[@id="data"]/section[2]/div[3]/div/div/div[2]/h3/div',
	'Your chances of becoming a victim of a property crime:': '//*[@id="data"]/section[4]/div[3]/div/div/div[2]/h3/div',
}

full_list_of_crimes = []

full_list_of_crimes.append('{} report'.format(city))

for c in crime_list:
	full_list_of_crimes.append(c + " " + tree.xpath(crime_list[c])[0].text.split()[0])

for d in other_crimes:
	full_list_of_crimes.append(d + " " + tree.xpath(other_crimes[d])[0].text.replace('\n', " "))


for k in full_list_of_crimes:
	print (k)


