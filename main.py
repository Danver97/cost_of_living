from bs4 import BeautifulSoup
from dataclasses import dataclass
import re
from urllib.request import urlopen

url = "https://www.numbeo.com/cost-of-living/in/Copenhagen?displayCurrency=EUR"
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")


def is_city_found(soup: BeautifulSoup) -> bool:
    return soup.find(lambda tag: 'Our system cannot find city with named with' in tag.text) is None

def euro_str_to_float(euro: str) -> float:
    return float(euro.replace(',', '').replace('€', ''))

def has_too_little_contributions(soup) -> bool:
    match_str = 'Some data are estimated due to a low number of contributors.'
    li_found = soup.find(lambda tag: tag.name=="div" and match_str in tag.text)
    return li_found is not None

def has_single_person_living_without_rent(soup: BeautifulSoup) -> bool:
    match_str = "A single person estimated monthly costs are "
    li_found = soup.find(lambda tag: tag.name=="li" and match_str in tag.text)
    return li_found is not None

def extract_single_person_living_without_rent(soup: BeautifulSoup) -> float:
    match_str = "A single person estimated monthly costs are "
    li_found = soup.find(lambda tag: tag.name=="li" and match_str in tag.text)
    prices: list[str] = li_found.contents[1].find_all(string=True, recursive=True)
    if '€' in prices[0]:
        return euro_str_to_float(prices[0].strip())
    else:
        return euro_str_to_float(prices[1].replace('(', '').replace(')', '').strip())

def extract_number_of_entries(soup: BeautifulSoup) -> int:
    match_str = r'This city had (\d+) entries'
    match_regexp = re.compile(match_str)
    div_found = soup.find(lambda tag: tag.name=="div" and len(match_regexp.findall(tag.text)) != 0)
    return int(match_regexp.findall(div_found.text)[0])

def extract_entry_from_table(soup: BeautifulSoup, entry_name: str) -> str:
    tr_found = soup.find(lambda tag: tag.name=="tr" and entry_name in tag.text)
    return tr_found.find_all('td')[1].find('span').text

def extract_avg_net_salary(soup: BeautifulSoup) -> float:
    txt = 'Average Monthly Net Salary (After Tax)'
    return euro_str_to_float(extract_entry_from_table(soup, txt))
def extract_one_bedroom_rent_centre(soup: BeautifulSoup) -> float:
    txt = 'Apartment (1 bedroom) in City Centre'
    return euro_str_to_float(extract_entry_from_table(soup, txt))
def extract_one_bedroom_rent_outside_centre(soup: BeautifulSoup) -> float:
    txt = 'Apartment (1 bedroom) Outside of Centre'
    return euro_str_to_float(extract_entry_from_table(soup, txt))
def extract_three_bedroom_rent_centre(soup: BeautifulSoup) -> float:
    txt = 'Apartment (3 bedrooms) in City Centre'
    return euro_str_to_float(extract_entry_from_table(soup, txt))
def extract_three_bedroom_rent_outside_centre(soup: BeautifulSoup) -> float:
    txt = 'Apartment (3 bedrooms) Outside of Centre'
    return euro_str_to_float(extract_entry_from_table(soup, txt))
def extract_price_per_squared_meter_centre(soup: BeautifulSoup) -> float:
    txt = 'Price per Square Meter to Buy Apartment in City Centre'
    return euro_str_to_float(extract_entry_from_table(soup, txt))
def extract_price_per_squared_meter_outside_centre(soup: BeautifulSoup) -> float:
    txt = 'Price per Square Meter to Buy Apartment Outside of Centre'
    return euro_str_to_float(extract_entry_from_table(soup, txt))

@dataclass
class City:
    """Class for keeping track of an city."""
    country: str
    name: str
    base_cost_of_living: float
    one_bedroom_rent_centre: float
    one_bedroom_rent_outside_centre: float
    three_bedroom_rent_centre: float
    three_bedroom_rent_outside_centre: float
    price_per_squared_meter_centre: float
    price_per_squared_meter_outside_centre: float
    avg_net_salary: float
    entries: int

    def to_csv(self) -> str:
        csv_str = f'{self.country},'
        csv_str += f'{self.name},'
        csv_str += f'{self.base_cost_of_living},'
        csv_str += f'{self.one_bedroom_rent_centre},'
        csv_str += f'{self.one_bedroom_rent_outside_centre},'
        csv_str += f'{self.three_bedroom_rent_centre},'
        csv_str += f'{self.three_bedroom_rent_outside_centre},'
        csv_str += f'{self.price_per_squared_meter_centre},'
        csv_str += f'{self.price_per_squared_meter_outside_centre},'
        csv_str += f'{self.avg_net_salary},'
        csv_str += f'{self.entries}'
        return csv_str
    
def extract_city_record(soup: BeautifulSoup, country: str, name: str) -> City:
    return City(country,
                name,
                extract_single_person_living_without_rent(soup),
                extract_one_bedroom_rent_centre(soup),
                extract_one_bedroom_rent_outside_centre(soup),
                extract_three_bedroom_rent_centre(soup),
                extract_three_bedroom_rent_outside_centre(soup),
                extract_price_per_squared_meter_centre(soup),
                extract_price_per_squared_meter_outside_centre(soup),
                extract_avg_net_salary(soup),
                extract_number_of_entries(soup))

countries_and_cities = {
    'DK': ['Copenhagen', 'Aarhus-Denmark', 'Odense', 'Aalborg', 'Esbjerg'],
    'ES': ["Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza-Saragossa", "Malaga", "Murcia", "Palma-De-Mallorca", "Las-Palmas", "Bilbao"],
    'FR': ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice', 'Nantes', 'Montpellier', 'Strasbourg', 'Bordeaux', 'Lille'],
    'DE': ['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt', 'Stuttgart', 'Dusseldorf', 'Leipzig', 'Dortmund', 'Essen'],
    'UK': ["London", "Birmingham", "Leeds", "Glasgow", "Sheffield", "Bradford", "Manchester", "Liverpool", "Edinburgh", "Bristol"],
    'IT': ["Rome", "Milan", "Naples", "Turin", "Palermo", "Genoa", "Bologna", "Florence", "Bari", "Catania", "Venice", "Verona", "Messina-Italy", "Padova", "Trieste", "Brescia", "Taranto", "Parma", "Prato", "Modena"],
    'PT': ["Lisbon", "Porto", "Vila-Nova-De-Gaia-Portugal", "Amadora-Portugal", "Braga"],
    'CH': ["Zurich", "Geneva", "Basel", "Lausanne", "Bern"],
    'PL': ["Warsaw", "Krakow-Cracow", "Lodz", "Wroclaw", "Poznan", "Gdansk", "Szczecin", "Bydgoszcz", "Lublin", "Katowice"],
    'NO': ["Oslo", "Bergen", "Stavanger", "Trondheim", "Drammen"],
    'SE': ["Stockholm", "Gothenburg", "Malmo", "Uppsala", "Vasteras"],
    'FI': ["Helsinki", "Espoo", "Tampere", "Vantaa", "Oulu"],
    'AT': ["Vienna", "Graz", "Linz", "Salzburg", "Innsbruck"],
    'HU': ["Budapest", "Debrecen", "Szeged", "Miskolc", "Pecs"],
    'IE': ["Dublin", "Cork", "Limerick", "Galway", "Waterford"],
    'BE': ["Brussels", "Antwerp", "Charleroi-Belgium", "Liege"],
    'NL': ["Amsterdam", "Rotterdam", "The-Hague-Den-Haag-Netherlands", "Utrecht", "Eindhoven"],
    'LU': ["Luxembourg"],

    'RO': ["Bucharest", "Timisoara", "Iasi", "Constanta"],
    'CZ': ["Prague", "Brno", "Ostrava", "Plzen", "Liberec"],
    'SK': ["Bratislava", "Kosice", "Presov", "Zilina", "Nitra"],
    'IS': ["Reykjavik", "Hafnarfjorour-Iceland", "Akureyri"],

    'US': ["New-York", "Los-Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San-Antonio", "San-Diego", "Dallas", "San-Jose", "Austin", "Jacksonville", "Fort-Worth", "Columbus", "San-Francisco"],
    'CA': ["Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", "Ottawa", "Mississauga", "Winnipeg", "Quebec-City", "Hamilton"],
    'AU': ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Gold-Coast", "Newcastle", "Canberra", "Sunshine-Coast", "Wollongong"],
}

cities_not_found: list[str] = []
cities_too_little_entries: list[str] = []
cities_incomplete: list[str] = []
city_entries: list[City] = []
for country, cities in countries_and_cities.items():
    for city in cities:
        url = f"https://www.numbeo.com/cost-of-living/in/{city}?displayCurrency=EUR"
        try:
            page = urlopen(url)
            html = page.read().decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")
            if not is_city_found(soup):
                cities_not_found.append(f'{city} ({country})')
                continue
            if has_too_little_contributions(soup) or extract_number_of_entries(soup) < 200:
                cities_too_little_entries.append(f'{city} ({country})')
                continue
            if not has_single_person_living_without_rent(soup):
                cities_incomplete.append(f'{city} ({country})')
                continue
            city_entries.append(extract_city_record(soup, country, city))
        except:
            print(f'Failed processing city: {city} ({country})')
            raise

print('Cities not found:')
for city in cities_not_found:
    print(city)
print()
print('Cities with too little entries:')
for city in cities_too_little_entries:
    print(city)
print()
print('Cities with incomplete data:')
for city in cities_incomplete:
    print(city)
print()
print('Cities found:')
for city in city_entries:
    print(city.to_csv())


header = 'country,city,base_cost_of_living,one_bedroom_rent_centre,one_bedroom_rent_outside_centre,three_bedroom_rent_centre,three_bedroom_rent_outside_centre,price_per_squared_meter_centre,price_per_squared_meter_outside_centre,avg_net_salary,entries'
with open('cities.csv', 'w') as fp:
    fp.write(header + '\n')
    for city in city_entries:
        fp.write(city.to_csv() + '\n')
