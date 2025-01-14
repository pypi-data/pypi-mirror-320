from abc import ABC, abstractmethod

class BaseModel(ABC):
    def __init__(self):
        pass
    
    def run(self) -> list[dict[str, any]]:
        try:
            points = []
            points.append({'action': 'update_data', 'data': self.get_data()})
            return points
        except Exception as e:
            print('An error occurred during model run: ', e)