from bs4 import BeautifulSoup


# Function to extract success percentage from HTML
def extract_success_percentage(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the element containing the success percentage
    percentage_element = soup.find('span', class_='pc_cov')
    if percentage_element:
        return percentage_element.text.strip()
    else:
        raise ValueError("Success percentage not found in the HTML content.")