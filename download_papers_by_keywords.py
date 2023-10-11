from pathlib import Path
import argparse
import arxiv
import requests

# Mapping of human-readable sort criterion names to arxiv.SortCriterion values
sort_criterions_arxiv = {
    "Relevance": arxiv.SortCriterion.Relevance,
    "LastUpdated": arxiv.SortCriterion.LastUpdatedDate,
    "Submitted": arxiv.SortCriterion.SubmittedDate
}


def download_paper(title, pdf_url, download_path):
    """
    Download and save a paper given its title, PDF URL, and download path.

    Args:
        title (str): The title of the paper.
        pdf_url (str): The URL of the paper's PDF.
        download_path (str): The directory where the paper should be saved.

    Returns:
        None
    """
    if pdf_url:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            # Generate a filename based on the paper's title
            filename = f"{title.replace(' ', '_').replace(':', '_').lower()}.pdf"
            with open(Path(download_path, filename), 'wb') as file:
                file.write(response.content)
            print(f"Paper downloaded as {filename}")
        else:
            print(f"Failed to download the paper. Status code: {response.status_code}")
    else:
        print(f"No PDF link found for the paper")


def main(query_text, max_results, sort_criterion, output_path):
    """
    Perform an ArXiv search based on the provided parameters and download the search results.

    Args:
        query_text (str): The query text for the ArXiv search.
        max_results (int): The maximum number of results to retrieve.
        sort_criterion (str): The sort criterion for the search results.
        output_path (str): The directory where downloaded papers should be saved.

    Returns:
        None
    """
    # create output directory if it doesn't exist
    Path(output_path).mkdir(parents=True, exist_ok=True)

    try:
        # Convert the provided sort criterion name to its corresponding arxiv.SortCriterion value
        sort_criterion_arxiv = sort_criterions_arxiv[sort_criterion]
    except KeyError:
        # Handle the case where an invalid sort criterion is provided
        print(f"Invalid sort criterion. Valid values are: {list(sort_criterions_arxiv.keys())}")
        return

    # Perform the ArXiv search based on the specified query, max_results, and sort criterion
    search = arxiv.Search(
        query=query_text,
        max_results=max_results,
        sort_by=sort_criterion_arxiv,
        sort_order=arxiv.SortOrder.Descending
    )

    # Iterate through the search results and download each paper
    for paper in search.results():
        title_suggested = paper.title
        pdf_url = paper.pdf_url
        download_paper(title_suggested, pdf_url, output_path)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Download and save papers from ArXiv based on a text query.")
    parser.add_argument('--query_text', type=str, default="retrieval augmented generation", help="Query text for ArXiv search")
    parser.add_argument('--max_results', type=int, default=20, help="Maximum number of results to retrieve")
    parser.add_argument('--sort_criterion', type=str, default="Relevance", help="Sort criterion for results")
    parser.add_argument('--output_path', type=str, default="literature/rag", help="Output path for saving downloaded papers")

    args = parser.parse_args()

    # Call the main function with parsed command-line arguments
    main(args.query_text, args.max_results, args.sort_criterion, args.output_path)
