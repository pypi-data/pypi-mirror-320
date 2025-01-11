import argparse
import csv
from pathlib import Path
import logging
import requests
import string
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

# Base URLs for PubMed API endpoints
BASEURL_SRCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
BASEURL_FTCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'


def fetch_papers(query: str, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Fetches research papers from PubMed based on a query.

    Args:
        query (str): The search query for PubMed.
        max_results (int): Maximum number of results to fetch.

    Returns:
        List[Dict[str, Any]]: List of paper details.
    """
    search_params = {
        'db': 'pubmed',       
        'term': query,  # Search query    
        'retmax': max_results,  # Number of results to fetch
        'retmode': 'xml',  # Response format
        'usehistory': 'y',   
    }

    logging.debug("Fetching PubMed search results...")
    search_response = requests.get(BASEURL_SRCH, params=search_params)
    search_response.raise_for_status()  
    search_root = ET.fromstring(search_response.text) 

    count = int(search_root.find('Count').text)
    query_key = search_root.find('QueryKey').text
    web_env = search_root.find('WebEnv').text   

    logging.debug(f"Total papers found: {count}")

    fetch_params = {
        'db': 'pubmed',
        'query_key': query_key,
        'WebEnv': web_env,
        'retstart': 0,   # Starting index for results
        'retmax': max_results,  # Maximum results to fetch
        'retmode': 'xml'  # Response format      
    }

    fetch_response = requests.get(BASEURL_FTCH, params=fetch_params)
    fetch_response.raise_for_status()  # Raise exception for HTTP errors
    fetch_root = ET.fromstring(fetch_response.text)  # Parse XML response

    return parse_paper_details(fetch_root)


def parse_paper_details(root: ET.Element) -> List[Dict[str, Any]]:
    """
    Parses details of papers from PubMed XML response.

    Args:
        root (ET.Element): Root element of the XML response.

    Returns:
        List[Dict[str, Any]]: List of parsed paper details.
    """
    results = []
    academic_keywords = [
        "school", "university", "college", "institute", "research", "lab"
    ]

    for article in root.iter('PubmedArticle'):
        pmid = article.findtext("MedlineCitation/PMID", "N/A")  
        title = article.findtext("MedlineCitation/Article/ArticleTitle", "N/A")  
        pub_date = article.findtext("MedlineCitation/Article/Journal/JournalIssue/PubDate/Year", "N/A")  

        authors = article.findall("MedlineCitation/Article/AuthorList/Author")  # Authors
        non_academic_authors = []  
        company_affiliations = [] 

        for author in authors:
            affiliation = author.findtext("AffiliationInfo/Affiliation", "").lower().strip()
            affiliation = affiliation.translate(str.maketrans('', '', string.punctuation)) 
            if not any(keyword in affiliation for keyword in academic_keywords):  # Filter non-academic
                
                non_academic_authors.append(
                    f"{author.findtext('ForeName', '')} {author.findtext('LastName', '')}".strip()  # Author name
                )
                company_affiliations.append(affiliation)  

        results.append({
            "PubmedID": pmid,
            "Title": title,
            "Publication Date": pub_date,
            "Non-academic Author(s)": ", ".join(non_academic_authors),  
            "Company Affiliation(s)": ", ".join(company_affiliations), 
        })

    return results


def save_to_csv(data: List[Dict[str, Any]], filename: Path):
    """
    Saves paper details to a CSV file.

    Args:
        data (List[Dict[str, Any]]): List of paper details.
        filename (Path): Path to save the CSV file.
    """
    with filename.open(mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys()) 
        writer.writeheader()  
        writer.writerows(data)  


# Main function that integrates all functionalities
def main():
    """
    Main function to handle command-line arguments and execute the program.
    """
    parser = argparse.ArgumentParser(
        description="Fetch research papers based on a query."
    )
    
    parser.add_argument(
        "query", 
        type=str, 
        help="Query for fetching papers."
    )  
    parser.add_argument(
        "-f", 
        "--file", 
        type=str, 
        help="Filename to save results as CSV."
    )  
    parser.add_argument(
        "-d", 
        "--debug", 
        action="store_true", 
        help="Enable debug mode."
    ) 

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug("Starting the PubMed paper search...")

    try:
        papers = fetch_papers(args.query)
        if not papers:
            logging.warning("No results found for the given query.")
            return

        if args.file:
            save_to_csv(papers, Path(args.file))
            logging.info(f"Results saved to {args.file}")
        else:
            for row in papers:
                print(row)

    except Exception as e:
        logging.error(f"An error occurred: {e}")  
