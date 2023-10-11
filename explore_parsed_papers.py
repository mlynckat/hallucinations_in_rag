import json
import os
import argparse


def process_parsed_papers(dir_path):
    """
    Process parsed papers in the specified directory and print their contents.

    Args:
        dir_path (str): The directory path where parsed papers are stored.

    Returns:
        None
    """
    all_files = os.listdir(dir_path)

    for file in all_files:
        file_path = os.path.join(dir_path, file)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        try:
            print(data["title"])
        except KeyError:
            print(file)
        print(data["overall_summary"])
        print(data["contributions"])
        print(data["further_research"])
        print(data["metrics_aggregated"])
        print(data["mitigations_aggregated"])

        for section in data["sections"]:
            if section["metrics"]:
                print("Metrics: ", section["metrics"])
                print(section["metrics_description"])
            if section["mitigation"]:
                print("Mitigation:", section["mitigation"])
                print(section["mitigation_description"])
        print("-" * 100)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process parsed papers in a specified directory and print their contents.")
    parser.add_argument('--dir_path', type=str, default="parsed_papers", help="Path to the directory where parsed papers are stored")

    args = parser.parse_args()
    process_parsed_papers(args.dir_path)