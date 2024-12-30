from googlesearch import search


def get_company_url_from_google(company_name, site_url):
    try:
        # Use Google Search to find the site_url link for the company
        query = f"{company_name} site:{site_url}"
        search_results = search(query, num_results=1)

        # Extract the first search result
        company_url = next(search_results, None)
        if not company_url:
            return f"No results found for {company_name} on {site_url}"
        return company_url
        
    except Exception as e:
        return f"An error occurred: {e}"