import os
import rdflib
import pandas as pd
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Define a base namespace and specific namespaces for rules and descriptions
CACAO_BASE_NS = rdflib.Namespace("http://w3id.org/cacao/")
CACAO_RULE_NS = rdflib.Namespace(str(CACAO_BASE_NS) + "vocab/license/")
ODRL = rdflib.Namespace("http://www.w3.org/ns/odrl/2/")
CC = rdflib.Namespace("http://creativecommons.org/ns#")

def check_path(parent_directory):
    """
    Check if the given path is a file or directory.
    """
    if not os.path.exists(parent_directory):
        print(f"Directory '{parent_directory}' does not exist.")
        
    if not os.path.isdir(parent_directory):
        print(f"'{parent_directory}' is not a directory.")
        return
    
def handle_rules_row(g: rdflib.Graph, row: pd.Series, permission_bnode: rdflib.BNode, obligation_bnode: rdflib.BNode, prohibition_bnode: rdflib.BNode):
    """
    Transforms a row from the rules DataFrame into an RDF graph entity.
    """

    predicate_uri = ODRL.action
    if row["RELEVANT"] == "YES":
        uri = row["URI"]
        if "http://www.w3.org/ns/odrl/2/" in uri:
            object_literal = ODRL[uri.split("/")[-1]]
        if "http://creativecommons.org/ns#" in uri:
            object_literal = CC[uri.split("#")[-1]]
        section = row["CATEGORY"].lower()
        if "permission" in section:
            g.add((permission_bnode, predicate_uri, object_literal))
        elif "obligation" in section:
            g.add((obligation_bnode, predicate_uri, object_literal))
        elif "prohibition" in section:
            g.add((prohibition_bnode, predicate_uri, object_literal))
        
            
                
            
    
def handle_description_row(row: pd.Series):
    pass
    


if __name__ == "__main__":
   

    main_graph = rdflib.Graph()

    # Bind namespaces to the main graph for cleaner output
    main_graph.bind("cacao", CACAO_BASE_NS)
    main_graph.bind("cacao_license", CACAO_RULE_NS)
    main_graph.bind("odrl", ODRL)
    main_graph.bind("cc", CC)
    
    parent_directory = "licenses"
    check_path(parent_directory)

    for item_name in os.listdir(parent_directory):
        # Create graph
        g = rdflib.Graph()
        
    
        safe_license_folder = "".join(c if c.isalnum() or c in ['-', '_', '.'] else '_' for c in item_name.replace(" ", "_"))
        
        # create URI for the license
        subject_uri = CACAO_RULE_NS[safe_license_folder]
        g.add((subject_uri, RDF.type, ODRL.Policy))
        
        # create blankenodes for permission, obligation, and prohibition
        permission_bnode = rdflib.BNode()
        obligation_bnode = rdflib.BNode()
        prohibition_bnode = rdflib.BNode()



        item_path = os.path.join(parent_directory, item_name)
        
        if os.path.isdir(item_path):
            description_file = os.path.join(item_path, "description.tsv")
            rules_file = os.path.join(item_path, "rules.tsv")
            if os.path.isfile(description_file) and os.path.isfile(rules_file):
                description_df = pd.read_csv(description_file, sep="\t")
                rules_df = pd.read_csv(rules_file, sep="\t")
                # Process the DataFrames as needed
                for index, row_series in rules_df.iterrows():
                    handle_rules_row(g, row_series, permission_bnode, obligation_bnode, prohibition_bnode)
            else:
                print(f"Missing description or rules file in {item_path}.")
            # for row_tup in description_df.iterrows():
            #     g = handle_description_row(row_tup[1])
                
        g.add((subject_uri, ODRL.permission, permission_bnode))
        g.add((subject_uri, ODRL.obligation, obligation_bnode))
        g.add((subject_uri, ODRL.prohibition, prohibition_bnode))
        main_graph += g     
        # After processing all files, serialize the main graph to a file
    output_file = "cacao-rs-vocab.ttl" # Turtle format
    try:
        main_graph.serialize(destination=output_file, format="turtle")
        print(f"Successfully wrote combined graph to {output_file}")
    except Exception as e:
        print(f"Error serializing graph: {e}")
