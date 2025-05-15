import rdflib
from rdflib.namespace import RDF, Namespace
import csv
import os

# Define Namespaces
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
CACAO_LICENSE = Namespace("http://w3id.org/cacao/vocab/license/")
CC = Namespace("http://creativecommons.org/ns#") # For terms like cc:ShareAlike

def get_relevant_actions_from_tsv(tsv_file_path):
    """
    Reads a TSV file and extracts URIs from the third column.
    Assumes the first row is a header and URIs are in the 3rd column (index 2).

    Args:
        tsv_file_path (str): Path to the TSV file.

    Returns:
        set: A set of relevant action URIs.
    """
    relevant_actions = set()
    try:
        with open(tsv_file_path, 'r', newline='', encoding='utf-8') as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            try:
                next(reader) # Skip header row
            except StopIteration:
                print(f"Warning: TSV file {tsv_file_path} is empty or has no header.")
                return relevant_actions # Return empty set if no header/data
                
            for i, row in enumerate(reader):
                if len(row) >= 2 and row[1].strip(): # Check if row has at least 3 columns and URI is not empty
                    uri = row[1].strip()
                    if uri.startswith("http://") or uri.startswith("https://"):
                        relevant_actions.add(uri)
                    else:
                        print(f"Warning: Invalid URI found in {tsv_file_path} at row {i+2}: '{uri}' - Skipping.")
                elif len(row) < 3:
                    print(f"Warning: Row {i+2} in {tsv_file_path} has fewer than 3 columns - Skipping.")

    except FileNotFoundError:
        print(f"Error: TSV file not found at {tsv_file_path}")
    except Exception as e:
        print(f"Error reading TSV file {tsv_file_path}: {e}")
    return relevant_actions

def transform_rdf_for_licenses(turtle_file_path, relevant_actions_uris, output_directory="output_tsvs"):
    """
    Transforms RDF Turtle data to multiple TSV files, one for each CACAO license.
    Each TSV file will list all relevant_actions_uris for PERMISSIONS, PROHIBITIONS, 
    and OBLIGATIONS, marking 'YES' or 'NO' in the RELEVANT column.

    Args:
        turtle_file_path (str): Path to the RDF Turtle file.
        relevant_actions_uris (set): A set of all action URIs from the rules.tsv.
        output_directory (str): Directory to save the output TSV files.
    """
    g = rdflib.Graph()
    try:
        g.parse(turtle_file_path, format="turtle")
        print(f"Successfully parsed Turtle file: {turtle_file_path}")
    except Exception as e:
        print(f"Error parsing Turtle file {turtle_file_path}: {e}")
        return

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
            print(f"Created output directory: {output_directory}")
        except OSError as e:
            print(f"Error creating output directory {output_directory}: {e}")
            return

    g.bind("odrl", ODRL)
    g.bind("cacao_license", CACAO_LICENSE)
    g.bind("cc", CC)

    query_licenses_str = f"""
        SELECT DISTINCT ?policy_uri WHERE {{
            ?policy_uri a odrl:Policy .
            FILTER(STRSTARTS(STR(?policy_uri), "{str(CACAO_LICENSE)}"))
        }}
    """
    
    licenses_results_check = list(g.query(query_licenses_str))
    if not licenses_results_check:
        print(f"No CACAO licenses (odrl:Policy starting with {str(CACAO_LICENSE)}) found in the Turtle data.")
        return
    
    found_licenses_count = 0
    for lic_row in licenses_results_check: # Iterate over the materialized list
        found_licenses_count += 1
        policy_uri = lic_row.policy_uri
        
        policy_local_name = str(policy_uri).replace(str(CACAO_LICENSE), "cacao_license_")
        policy_local_name = policy_local_name.replace(str(CC), "cc_")
        policy_local_name = policy_local_name.replace("http://", "").replace("https://", "")
        policy_local_name = "".join(c if c.isalnum() or c in ['_', '-'] else '_' for c in policy_local_name)
        output_tsv_path = os.path.join(output_directory, f"{policy_local_name}.tsv")
        
        print(f"\nProcessing license: {policy_uri}")

        # Sets to store actions found in RDF for *this specific policy*
        found_permissions_for_policy = set()
        found_prohibitions_for_policy = set()
        found_obligations_for_policy = set()

        # --- Populate found permissions for this policy ---
        query_permissions = rdflib.plugins.sparql.processor.prepareQuery(
            "SELECT DISTINCT ?action_uri WHERE { ?bound_policy odrl:permission ?perm_rule . ?perm_rule odrl:action ?action_uri . }",
            initNs={"odrl": ODRL}
        )
        for row in g.query(query_permissions, initBindings={'bound_policy': policy_uri}):
            action_uri_str = str(row.action_uri)
            if action_uri_str in relevant_actions_uris: # Only consider actions from rules.tsv
                found_permissions_for_policy.add(action_uri_str)

        # --- Populate found prohibitions for this policy ---
        query_prohibitions = rdflib.plugins.sparql.processor.prepareQuery(
            "SELECT DISTINCT ?action_uri WHERE { ?bound_policy odrl:prohibition ?pro_rule . ?pro_rule odrl:action ?action_uri . }",
            initNs={"odrl": ODRL}
        )
        for row in g.query(query_prohibitions, initBindings={'bound_policy': policy_uri}):
            action_uri_str = str(row.action_uri)
            if action_uri_str in relevant_actions_uris:
                found_prohibitions_for_policy.add(action_uri_str)
        
        # --- Populate found obligations for this policy ---
        query_obligations = rdflib.plugins.sparql.processor.prepareQuery(
            """SELECT DISTINCT ?action_uri WHERE {
                { ?bound_policy odrl:obligation ?duty_or_action . ?duty_or_action a odrl:Duty . ?duty_or_action odrl:action ?action_uri . }
                UNION
                { ?bound_policy odrl:obligation ?action_uri . FILTER(isIRI(?action_uri) && NOT EXISTS { ?action_uri a odrl:Duty . }) }
            }""",
            initNs={"odrl": ODRL}
        )
        for row in g.query(query_obligations, initBindings={'bound_policy': policy_uri}):
            action_uri_str = str(row.action_uri)
            if action_uri_str in relevant_actions_uris:
                found_obligations_for_policy.add(action_uri_str)

        # --- Prepare all output rows for this policy ---
        output_data_for_policy = []
        sorted_relevant_actions = sorted(list(relevant_actions_uris)) # Sort for consistent output

        for action_uri_str in sorted_relevant_actions:
            # Permissions entry for this action
            is_relevant_permission = "YES" if action_uri_str in found_permissions_for_policy else "NO"
            output_data_for_policy.append(["PERMISSIONS", action_uri_str, is_relevant_permission])
            
            # Prohibitions entry for this action
            is_relevant_prohibition = "YES" if action_uri_str in found_prohibitions_for_policy else "NO"
            output_data_for_policy.append(["PROHIBITIONS", action_uri_str, is_relevant_prohibition])
            
            # Obligations entry for this action
            is_relevant_obligation = "YES" if action_uri_str in found_obligations_for_policy else "NO"
            output_data_for_policy.append(["OBLIGATIONS", action_uri_str, is_relevant_obligation])
            
        # Write data to TSV file for this policy
        try:
            with open(output_tsv_path, 'w', newline='', encoding='utf-8') as tsvfile:
                writer = csv.writer(tsvfile, delimiter='\t')
                writer.writerow(["CATEGORY", "URI", "RELEVANT"]) # Header
                if output_data_for_policy: # Only write data rows if there are any (i.e., relevant_actions_uris was not empty)
                    for data_row in output_data_for_policy:
                        writer.writerow(data_row)
            print(f"Successfully generated TSV for {policy_uri} at {output_tsv_path} with {len(output_data_for_policy)} data rows.")
        except Exception as e:
            print(f"Error writing TSV file for {policy_uri} at {output_tsv_path}: {e}")
    
    if found_licenses_count == 0:
         print(f"No CACAO licenses (odrl:Policy starting with {str(CACAO_LICENSE)}) were processed (re-check after initial list).")


if __name__ == '__main__':
    # --- Configuration ---
    input_turtle_file = "archive/cacao-rs-vocab.ttl" 
    rules_tsv_file = "licenses/CC-BY 4.0/rules.tsv" 
    output_dir = "generated_tsvs"
    # --- End Configuration ---

    if not os.path.exists(input_turtle_file):
        print(f"CRITICAL: Input Turtle file '{input_turtle_file}' not found. Please create it or fix the path.")
        # Example: Create a dummy cacao-rs-vocab.ttl if it doesn't exist for testing
        # with open(input_turtle_file, "w") as f:
        #     f.write("@prefix cacao_license: <http://w3id.org/cacao/vocab/license/> .\n")
        #     f.write("@prefix odrl: <http://www.w3.org/ns/odrl/2/> .\n")
        #     f.write("cacao_license:TestPolicy a odrl:Policy .\n") # Minimal content
        # print(f"Created a dummy '{input_turtle_file}' for testing.")
        # For actual use, the user should provide their file.

    if not os.path.exists(rules_tsv_file):
        print(f"CRITICAL: Rules TSV file '{rules_tsv_file}' not found. Please create it or fix the path.")
        # Example: Create a dummy rules.tsv if it doesn't exist for testing
        # with open(rules_tsv_file, "w") as f:
        #     f.write("Section\tAction\tURI\tApplicable\tReasoning\n")
        #     f.write("Permissions\tdummy action\thttp://example.com/action1\tYES\tTest\n")
        # print(f"Created a dummy '{rules_tsv_file}' for testing.")
        # For actual use, the user should provide their file.


    print(f"Attempting to load relevant actions from: {rules_tsv_file}")
    relevant_actions = get_relevant_actions_from_tsv(rules_tsv_file)
    
    if not relevant_actions:
        print("Warning: No relevant actions loaded from rules.tsv. Output TSVs will only contain headers.")
        # The script will still run and create files with headers if policies are found.
    else:
        print(f"Successfully loaded {len(relevant_actions)} unique relevant actions from {rules_tsv_file}.")

    if os.path.exists(input_turtle_file):
        transform_rdf_for_licenses(input_turtle_file, relevant_actions, output_dir)
        print(f"\nProcessing complete. Check the '{output_dir}' directory for TSV files.")
    else:
        print(f"Cannot proceed with transformation as '{input_turtle_file}' was not found.")

