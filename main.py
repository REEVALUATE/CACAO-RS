import os
import rdflib
import pandas as pd
from rdflib.namespace import RDF, RDFS, OWL, XSD

def check_path(parent_directory):
    """
    Check if the given path is a file or directory.
    """
    if not os.path.exists(parent_directory):
        print(f"Directory '{parent_directory}' does not exist.")
        
    if not os.path.isdir(parent_directory):
        print(f"'{parent_directory}' is not a directory.")
        return

if __name__ == "__main__":

    # using os, loop over all the files in the directory licenses and its subdirectories
    # and create a DataFrame with the data
    parent_directory = "licenses"
    check_path(parent_directory)

    for item_name in os.listdir(parent_directory):
        item_path = os.path.join(parent_directory, item_name)
        if os.path.isdir(item_path):
            description_file = os.path.join(item_path, "description.tsv")
            rules_file = os.path.join(item_path, "rules.tsv")
            if os.path.isfile(description_file) and os.path.isfile(rules_file):
                description_df = pd.read_csv(description_file, sep="\t")
                rules_df = pd.read_csv(rules_file, sep="\t")
                
                # Process the DataFrames as needed
                print(f"Description DataFrame for {item_name}:")
                print(description_df)
                print(f"Rules DataFrame for {item_name}:")
                print(rules_df)
            else:
                print(f"Missing description or rules file in {item_path}.")