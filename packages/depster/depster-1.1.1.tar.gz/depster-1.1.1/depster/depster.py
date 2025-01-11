import pandas as pd
import requests
import warnings

def convert_package_lock_to_csv(input_file, output_file="dependencies.csv"):
    """
    Converts package-lock.json to CSV with detailed dependency information.
    
    Args:
        input_file (str): Path to the package-lock.json file.
        output_file (str): Path to save the CSV file (default: dependencies.csv).
    """
    warnings.filterwarnings('ignore') #suppress warnings
    
    with open(input_file) as package_lock_file:
        df = pd.read_json(package_lock_file)
    
    #change column names
    df = df.rename(columns={'name':'Project','version':'Current Version','dependencies':'dict'})
    df.index.name = "Packages"
    #add a few empties
    df['Latest Version'] = None
    df['Integrity'] = None
    df['Requires'] = None
    df['Dependencies'] = None
    df['hasDependencies'] = False
    df['Description'] = None
    df['License'] = None


    # make and fill new columns
    ## since the dict column contains type dicts we can use the key/value pairs for easy data manipulation
    for index,row in df.iterrows():
        df['Current Version'][index] = row['dict'].get('version')
        if row['dict'].get('integrity'):
            df['Integrity'][index] = row['dict'].get('integrity')
        if row['dict'].get('requires'):
            tempList = [key + ': ' +value for key,value in row['dict'].get('requires').items()].copy() ## turn dict into list
            df['Requires'][index] = tempList
            df['hasDependencies'][index] = True
        if row['dict'].get('dependencies'):
            tempList = [key + ': ' +row['dict'].get('dependencies')[key]['version'] for key in row['dict'].get('dependencies').keys()]
            df['Dependencies'][index] = tempList
            df['hasDependencies'][index] = True

    #drop columns
    df.drop(labels={'dict','lockfileVersion'},axis=1,inplace=True)

    # in order to populate the 'Newest Version', 'License', and 'Description' columns, 
    ## we'll need to do some querys... 
    ### https://registry.npmjs.org/:package will suffice
    #### we'll also be making a LOT of requests
    ##### response.json() turns the response into a dict for us to parse

    header = {'Accept' : 'application/vnd.npm.install-v1+json'} ##gets an abbreviated response

    for index, _ in df.iterrows():
        try:
            response = requests.get('https://registry.npmjs.org/'+index,headers=header).json()
            df['Latest Version'][index] = response['dist-tags']['latest']
            df['Description'][index] = response.get('description', 'No description available.')
            df['License'][index] = response.get('license', 'Unknown')
        except Exception as e:
            print(f"Warning: Could not fetch version for package '{index}': {e}")

    
    df.to_csv(output_file)
    print(f"Conversion complete. CSV saved to {output_file}")

def main():
    """
    Entry point for the Depster CLI tool.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Depster: Convert package-lock.json to CSV.")
    parser.add_argument("input_file", help="Path to the package-lock.json file.")
    parser.add_argument("-o", "--output", default="dependencies.csv", help="Path to the output CSV file.")
    args = parser.parse_args()
    
    convert_package_lock_to_csv(args.input_file, args.output)

if __name__ == "__main__":
    main()
