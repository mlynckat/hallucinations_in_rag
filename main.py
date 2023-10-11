import argparse
import json
import os
from pathlib import Path

import langchain
import openai
from dotenv import load_dotenv  # Add this import
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser
from science_parse_api.api import parse_pdf

# debug langchain
langchain.debug = True

# Load environment variables from a .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is provided
if openai_api_key is None:
    raise ValueError("OpenAI API key is not provided in the environment variable OPENAI_API_KEY")

from models_and_prompts import SETTINGS


def initialize_chain(template_settings, llm_openai):
    """
    Initialize an LLMChain and its corresponding output parser.

    Args:
        template_settings (dict): Template settings for initializing the chain.
        llm_openai (ChatOpenAI): An instance of the ChatOpenAI class for the language model.

    Returns:
        Tuple: Initialized LLMChain and output parser.
    """
    output_parser = StructuredOutputParser.from_response_schemas(template_settings["response_schemas"])

    prompt = PromptTemplate(
        input_variables=template_settings["input_variables"],
        template=template_settings["template"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()}
    )

    return LLMChain(llm=llm_openai, prompt=prompt), output_parser


def process_section(section, chain, output_parser, prev_summary=""):
    """
        Process a section of text using the provided LLMChain and output parser.

        Args:
            section (dict): The section of text to process.
            chain (LLMChain): The LLMChain for generating responses.
            output_parser (StructuredOutputParser): The output parser for parsing generated responses.
            prev_summary (str): The summary of previous section.

        Returns:
            None
        """

    section["summary"] = ""
    section["metrics"] = ""
    section["metrics_description"] = ""
    section["mitigation"] = ""
    section["mitigation_description"] = ""
    if section["text"]:
        try:
            query = chain.run(section=section["text"], prev_summary=prev_summary)
        except openai.error.InvalidRequestError as e:
            print(e)
            print("Trying again without previous section summary...")
            try:
                query = chain.run(section=section["text"], prev_summary="")
            except openai.error.InvalidRequestError as e:
                print(e)
                print("Skipping...")
                print(section)
                return

        try:
            output_chain = output_parser.parse(query)
        except langchain.schema.output_parser.OutputParserException:
            try:
                output_chain = output_parser.parse(query + "```")
            except langchain.schema.output_parser.OutputParserException as e:
                print(e)
                print("Skipping...")
                print(query)
                return

        section["summary"] = output_chain["summary"]
        section["metrics"] = output_chain["metrics"]
        section["metrics_description"] = output_chain["metrics_description"]
        section["mitigation"] = output_chain["mitigation"]
        section["mitigation_description"] = output_chain["mitigation_description"]


def summarize_for_paper(output_dict, input_key, output_keys, chain_type, output_parser_type):
    """
        Generate diverse summaries for a paper using the corresponding LLMChain and output parser.

        Args:
            output_dict (dict): The dictionary containing paper sections and summary information.
            input_key (str): The key for the input text in each section.
            output_keys (list): The keys for the output summary information.
            chain_type (LLMChain): The LLMChain for generating corresponding responses. E.g., chain for summarizing the paper itself, metrics or mitigation techniques
            output_parser_type (StructuredOutputParser): The output parser for parsing generated responses.

        Returns:
            None
        """
    for output_key in output_keys:
        output_dict[output_key] = ""

    summaries = [section[input_key] for section in output_dict["sections"]]

    if all(not sub_item for sub_item in summaries):
        return
    query = chain_type.run(summaries)

    try:
        output = output_parser_type.parse(query)
    except langchain.schema.output_parser.OutputParserException:
        try:
            output = output_parser_type.parse(query + "```")
        except langchain.schema.output_parser.OutputParserException:
            return
    for output_key in output_keys:
        output_dict[output_key] = output[output_key]


def main(path_to_pdfs, output_path):
    """
        Main function to process PDF files and generate summaries.

        Args:
            path_to_pdfs (str): Path to the directory containing PDF files.
            output_path (str): Output directory for JSON files.

        Returns:
            None
        """
    host = 'http://127.0.0.1'
    port = '8080'

    llm_openai = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        openai_api_key=openai_api_key,  # Use the API key from the environment variable
        temperature=0.3
    )

    chain, output_parser = initialize_chain(SETTINGS["summarize_section"], llm_openai)
    chain_overall, output_parser_overall = initialize_chain(SETTINGS["summarize_paper"], llm_openai)
    chain_metrics, output_parser_metrics = initialize_chain(SETTINGS["aggregate_metrics"], llm_openai)
    chain_mitigation, output_parser_mitigation = initialize_chain(SETTINGS["aggregate_mitigation"], llm_openai)

    for file in Path(path_to_pdfs).glob("*.pdf"):
        output_dict = parse_pdf(host, file, port=port)

        prev_summary = ""
        for section in output_dict["sections"]:
            process_section(section, chain, output_parser, prev_summary)
            prev_summary = section.get("summary", "")

        summarize_for_paper(output_dict, "summary", ["overall_summary", "contributions", "further_research"],
                            chain_overall, output_parser_overall)
        summarize_for_paper(output_dict, "metrics_description", ["metrics_aggregated"], chain_metrics, output_parser_metrics)
        summarize_for_paper(output_dict, "mitigation_description", ["mitigations_aggregated"], chain_mitigation,
                            output_parser_mitigation)

        output_file_name = str(os.path.basename(file)).split(".pdf")[0] + ".json"
        output_file_path = os.path.join(output_path, output_file_name)
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(output_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize PDFs using LangChain")
    parser.add_argument('--path_to_pdfs', type=str, default="literature/pdfs/other", help="Path to the directory containing PDF files")
    parser.add_argument('--output_path', type=str, default="parsed_papers", help="Output directory for JSON files")

    args = parser.parse_args()
    main(args.path_to_pdfs, args.output_path)
