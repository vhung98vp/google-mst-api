import requests
import random
from bs4 import BeautifulSoup

USER_AGENT_LIST = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0.1 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edge/94.0.992.47",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; AS; .NET CLR 4.0.30319; InfoPath.3; .NET4.0C; .NET4.0E) like Gecko",
                ]
KEYS_TO_EXTRACT = ["Tên đầy đủ", "Tên quốc tế", "Tên viết tắt", "Mã số thuế", "Địa chỉ", "Người đại diện", "Điện thoại"]
KEYS_DICT = {
    "Tên đầy đủ": "full_name", 
    "Tên quốc tế": "int_name", 
    "Tên viết tắt": "short_name",
    "Mã số thuế": "comapny_tax_id",
    "Địa chỉ": "address", 
    "Người đại diện": "representative", 
    "Điện thoại": "tel" 
}

def extract_soup_from_table(soup):
    # Init fields
    company_info = {}
    data_fields = soup.find_all('table', class_='table-taxinfo')

    # Get company name from header of table
    full_name = soup.find('th', itemprop='name').find('span', class_='copy').text.strip()
    company_info['Tên đầy đủ'] = full_name

    # Get data from table
    for field in data_fields:
        rows = field.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if row.get('itemprop') == 'alumni':  # Special handling for 'alumni' row
                key = cols[0].text.strip()
                representative = cols[1].find('span', itemprop='name').text.strip()
                company_info[key] = representative
            elif len(cols) >= 2:
                key = cols[0].text.strip()
                if cols[1].get('itemprop') == 'telephone': # Special handling for 'telephone' row
                    tel = cols[1].find('span', class_='copy')
                    value = tel.text.strip() if tel else cols[1].text.strip()
                else:
                    value = cols[1].text.strip()
                company_info[key] = value
    
    # Filter only identity data
    filtered_data = {KEYS_DICT[key]: company_info[key] 
                     for key in KEYS_TO_EXTRACT if key in company_info}
    return filtered_data


def get_company_info_from_site(company_url):
    try:
        # Get page source from company_url
        user_agent = random.choice(USER_AGENT_LIST)
        headers = {'User-Agent': user_agent}
        response = requests.get(company_url, headers=headers)
        if response.status_code != 200:
            return f"Failed to retrieve data from {company_url}. Status code: {response.status_code}"

        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract company data (assumes specific HTML structure, adjust selectors as needed)
        company_info = extract_soup_from_table(soup)

        if company_info:
            # Get associated company urls
            company_info['associated'] = []
            alumni_section = soup.find('tr', itemprop="alumni")
            associated_companies_links = alumni_section.find_all('a')

            # Get associated company data
            for link in associated_companies_links[1:]:
                asc_url = "https://masothue.com" + link.get('href')
                asc_response = requests.get(asc_url, headers=headers)
                asc_soup = BeautifulSoup(asc_response.text, 'html.parser')
                asc_data = extract_soup_from_table(asc_soup)
                company_info['associated'].append(asc_data)
            
            return company_info 
        
        else:
            return "No detailed data found on the page."

    except Exception as e:
        return f"An error occurred: {e}"