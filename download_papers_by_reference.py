from pathlib import Path
import argparse
import arxiv
import requests
from science_parse_api.api import parse_pdf


# Function to download and save a paper given its title, PDF URL, and download path
def download_paper(title, pdf_url, download_path):
    """
    Download and save a paper.

    Args:
        title (str): The title of the paper.
        pdf_url (str): The URL of the paper's PDF.
        download_path (str): The directory where the paper should be saved.

    Returns:
        None
    """
    if pdf_url:
        if download_path is None:
            download_path = Path(pdf_url).parent
        else:
            Path(download_path).mkdir(parents=True, exist_ok=True)
        response = requests.get(pdf_url)
        if response.status_code == 200:
            filename = f"{title.replace(' ', '_').replace(':', '_').replace('?', '_').lower()}.pdf"
            with open(Path(download_path, filename), 'wb') as file:
                file.write(response.content)
            print(f"Paper downloaded as {filename}")
        else:
            print(f"Failed to download the paper. Status code: {response.status_code}")
    else:
        print(f"No PDF link found for the paper")


# Main function to download papers based on reference IDs and PDF path
def main(reference_ids=None, path_to_pdf="literature/pdfs/survey.pdf", output_path=None):
    """
    Main function to download papers based on reference IDs and PDF path.

    Args:
        reference_ids (list of int): List of reference IDs of the papers to be downloaded.
        path_to_pdf (str): Path to the PDF file.

    Returns:
        None
    """
    host = 'http://127.0.0.1'
    port = '8080'

    pdf_file = Path(path_to_pdf)
    output_dict = parse_pdf(host, pdf_file, port=port)
    references = output_dict.get("references", [])

    # If reference_ids is not provided, download all references
    if reference_ids is None:
        reference_ids = range(1, len(references) + 1)

    for reference_id in reference_ids:
        # Check if the reference_id is within the valid range
        if 1 <= reference_id <= len(references):
            reference = references[reference_id - 1]
            title = reference.get("title", "")
            search = arxiv.Search(
                query=title,
                max_results=1,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending
            )
            for paper in search.results():
                title_suggested = paper.title
                pdf_url = paper.pdf_url
                download_paper(title_suggested, pdf_url, output_path)
        else:
            print(f"Invalid reference ID: {reference_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and save papers from ArXiv using reference IDs and PDF path from a paper.")
    parser.add_argument('--reference_ids', nargs='+', type=int, default=list(range(1, 10)),
                        help="List of reference IDs of the papers that have to be downloaded")
    parser.add_argument('--path_to_pdf', type=str, default="literature/rag/a_survey_on_retrieval-augmented_text_generation.pdf",
                        help="Path to the paper as PDF file")
    parser.add_argument('--output_path', type=str, default=None, help="Output path for saving downloaded papers. If no path given, the papers will be saved in the same directory as the origibnal paper")

    args = parser.parse_args()
    main(reference_ids=args.reference_ids, path_to_pdf=args.path_to_pdf, output_path=args.output_path)
