from pydantic import BaseModel


class PackSchema(BaseModel):
    name: str
    description: str

class Pack:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def to_json(self) -> dict:
        return PackSchema(name=self.name, description=self.description).model_dump()



