from dataclasses import dataclass, field
import json


@dataclass
class HouseWOZ:
    house_name: str
    WOZ: field(default_factory=dict)

    def to_json(self):
        result = {"house_name": self.house_name}
        for year in self.WOZ:
            result[year] = self.WOZ[year]
        return json.dumps(result)