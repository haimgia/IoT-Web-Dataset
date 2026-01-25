import pandas as pd
import ast

def upload_csv(input_file, output_file):

    # reads data from input file
    with open(input_file, "r", encoding="utf-8") as f:
        data_list = f.readlines()

    # converts each line to a dictionary and collects them in a list
    dict_list = []
    for data in data_list:
        data = data.strip()
        if data:
            try:
                data_dict = ast.literal_eval(data)
                data_dict["raw_text"] = str(data_dict)  # adds the string representation of the dictionary
                dict_list.append(data_dict)
            except Exception as e:
                print(f"Error evaluating data: {data}\nException: {e}")
                continue

    # creates a DataFrame and saves it as a CSV file
    df = pd.DataFrame(dict_list)
    
    df.to_csv(output_file, index=False)