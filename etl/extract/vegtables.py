import pandas as pd
import os

#colour maping dict created to be used in app.py script
VEG_COLOUR = {
    "blackberries":"purple",
    "lettuce":"green",
    "tomatoes":"red"
}
def get_veg_data():
    
    # traverse up to the project root folder
    print(os.path.dirname(__file__))
    root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
    root_folder = os.path.join(root_folder,"etl/data")
    
    file_names = [f for f in os.listdir(root_folder)]
    data_dict = {}
    for filename in file_names:
        datatype = filename.split(".")[0]
        data = pd.read_csv(os.path.join(root_folder,filename))
        data_dict[datatype] = data
    print(data_dict)

    return data_dict

get_veg_data()