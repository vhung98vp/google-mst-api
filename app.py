from flask import Flask, request, jsonify
from src.company_url import get_company_url_from_google
from src.company_data import get_company_info_from_site
import re

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_company_data():
    # Site and company for searching
    site_url = "masothue.com"
    company_name = request.args.get('company_name')
    if not company_name:
        return jsonify({"error": "Company name is required"}), 400

    quick_search = request.args.get('quick')
    quick_search = True if quick_search == None else quick_search.lower() in ['true', '1', 'yes', 'y']
    # Get company url site from google, then extract data

    company_url = get_company_url_from_google(company_name, site_url)
    
    if quick_search:
        return {'company_tax_id': re.search(r'\d+', company_url).group()}
    else:
        company_info = get_company_info_from_site(company_url)
        return jsonify(company_info)

if __name__ == "__main__":
    app.run(debug=True)