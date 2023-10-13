## Downloading, parsing and summarizing papers

You would need some libraries. You can install them with the following command:

```bash
pip install -r requirements.txt
```

The repository consists of the following files / building blocks:

### 1. Download papers from the [arXiv](https://arxiv.org/) using a text query
#### Script: `download_papers_by_keywords.py` 
#### Run the script 
You can run the script with the desired command-line arguments. The available arguments are:

 - `--query_text` (default: "retrieval augmented generation"): The query text for the ArXiv search.
 - `--max_results` (default: 20): The maximum number of results to retrieve.
 - `--sort_criterion` (default: "Relevance"): The sort criterion for the search results. Valid values are "Relevance," "LastUpdated," and "Submitted."
 - `--output_path` (default: "literature/rag"): The directory where downloaded papers should be saved. The script will create the specified output_path if it doesn't exist, perform the ArXiv search, and download the papers into the specified directory.


   **Example usage:**

   ```shell
   python download_papers_by_keywords.py --query_text "natural language processing" --max_results 10 --sort_criterion "Relevance" --output_path "downloads/nlp"
 ```

### 2. Download papers from the [arXiv](https://arxiv.org/) using references from another paper
#### Script: `download_papers_by_reference.py` 
#### Run the script 
You can run the script by executing the following command:

```bash
python download_papers_by_reference.py --reference_ids [list of reference IDs] --path_to_pdf [path to the PDF] --output_path [output directory]
```

- `--reference_ids`: A list of reference IDs of the papers that you want to download. If not provided, it will default to all references.

- `--path_to_pdf`: Path to the paper in PDF format from which you want to extract references from.

- `--output_path`: Path where the downloaded papers will be saved. If not provided, the papers will be saved in the same directory as the original paper.

The script will process the PDF and extract references. It will then search ArXiv for the papers based on the extracted titles and download them. The downloaded papers will be saved in the specified output directory.

Here's an example command to download papers with reference IDs 1 to 5 from a PDF file located at "sample.pdf":

```bash
python arxiv_paper_downloader.py --reference_ids 1 2 3 4 5 --path_to_pdf sample.pdf --output_path my_downloads/
```

### 3. Summarize PDF using langchain and gpt-3.5-turbo
#### Script: `main.py`

#### Prerequisites
Create a .env file in the project directory and set your OpenAI API key as follows:

```bash
OPENAI_API_KEY=[your API key]
```

#### Run the script

You can run the script by executing the following command:

```bash
python main.py --path_to_pdfs [PDF directory path] --output_path [output directory path]
```

- `--path_to_pdfs`: Path to the directory containing PDF files that you want to summarize. The default path is set to "literature/pdfs/other."

- `--output_path`: Output directory where the generated JSON files will be saved. The default path is set to "parsed_papers."

The script will process the PDF files, extract the sections, and generate summaries for each section. It also aggregates metrics and mitigation techniques for the entire document and saves the results in JSON files.

You can modify the templates for the summaries in the script `models_and_promts.py`.

Here's an example command to summarize PDFs in a directory and save the results in an "output" directory:

```bash
python main.py --path_to_pdfs my_pdfs/ --output_path output/
```

### 4. Display summaries
#### Script: `explore_parsed_papers.py`

#### Run the script
Run the script by executing the following command:
    
```bash
python explore_parsed_papers.py --dir_path [directory path]
```
- `--dir_path`: This is the path to the directory where the parsed papers are stored. The default directory is set to "parsed_papers."

The script will process the parsed papers in the specified directory and print the contents of each paper. At the moment the printed information includes:

- **Title**: The title of the paper.
- **Overall Summary**: A summary of the paper's overall content.
- **Contributions**: Contributions or findings highlighted in the paper.
- **Further Research**: Suggestions or areas for further research.
- **Metrics Aggregated**: Aggregated metrics, if available.
- **Mitigations Aggregated**: Aggregated mitigation techniques, if available.

For each section within the paper, the script will also print the following information, if present:

- **Metrics**: Metrics specific to that section.
- **Metrics Description**: A description of the metrics.
- **Mitigation**: Mitigation techniques related to that section.
- **Mitigation Description**: A description of the mitigation techniques.

The script separates each paper's content with a line of hyphens (`---`) to make it easy to distinguish between papers.

However, feel free to adjust to your needs.

Here's an example command to process and print the contents of parsed papers in a directory named "my_parsed_papers":

```bash
python explore_parsed_papers.py --dir_path my_parsed_papers
```