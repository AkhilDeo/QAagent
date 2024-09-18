from bs4 import BeautifulSoup
import re


# Function to extract success percentage from HTML
def extract_success_percentage(html_content, target_function_name):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all table rows with class 'region'
    rows = soup.find_all('tr', class_='region')

    for row in rows:
        # Find the function name
        function_name_element = row.find('data', {'value': True})
        if function_name_element and function_name_element['value'] == target_function_name:
            # If the function name matches, extract the coverage percentage
            coverage_element = row.find('td', class_='right')
            if coverage_element:
                coverage_text = coverage_element.text.strip()
                coverage_match = re.search(r'(\d+)%', coverage_text)
                if coverage_match:
                    return coverage_match.group(1)

    # If the function name is not found or coverage can't be extracted
    return "0.0%"

    # # Find the element containing the success percentage
    # percentage_element = soup.find('span', class_='pc_cov')
    # if percentage_element:
    #     return percentage_element.text.strip()
    # else:
    #     raise ValueError("Success percentage not found in the HTML content.")