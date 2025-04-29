import pandas as pd

def create_json(points:pd.dataframe, path: str):
    ''''
    create json annotation file from a pandas dataframe
    '''
    new_dict=dict()
    new_dict['annotation'] = dict()
    new_dict['annotation']["elements"]=[]
    for index, point in points.iterrows():
        x = point["X"]
        y = point["Y"]
        temp_dict = dict()
        temp_dict["label"] = {'value':str(index)}
        temp_dict['center'] = [x,y,0]
        new_dict['annotation']["elements"].append(temp_dict)
    with open(path, 'w') as fp:
        json.dump(new_dict, fp)