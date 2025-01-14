import pandas as pd

class DataFilter:
    def __init__(self):
        pass

    def filter_data(self, data: list[dict[str, any]], filter_conditions: list[dict[str, any]]) -> dict[str, any]:
        ''' filter_conditions = [{'name': name, 'tags': {tag_name1: tag_value1, 'tag_name2': 'tag_value2'}},
                                 {...}] 
                                 
            'tags' is optional '''
        filtered_dict = {}
        df = pd.DataFrame(data)
        filtered_df = pd.DataFrame()
        for condition in filter_conditions:
            name = condition.get('name')
            tags = condition.get('tags', {})
            temp_df = df[df['name'] == name]
            for key, value in tags.items():
                temp_df = temp_df[temp_df[key] == value]
            filtered_df = pd.concat([filtered_df, temp_df])
            if not temp_df.empty:
                value = temp_df.iloc[0]['value']
                filtered_dict[name] = value
        return filtered_dict