from pydantic import BaseModel, Field
from typing import Any


class vectorFloat3d(BaseModel):
    x: float = Field(0,
                     title='X - Axis')

    y: float = Field(0,
                     title='Y - Axis')

    z: float = Field(0,
                     title='Z - Axis')

    @classmethod
    def from_list(cls, values: list):
        return cls(x=values[0], y=values[1], z=values[2])

    @property
    def values(self):
        return (self.x, self.y, self.z)

    @property
    def IsZero(self):
        return self.x + self.y + self.z == 0

    def to_list(self):
        return [self.x, self.y, self.z]

    class Config:
        schema_extra = {
            'examples': [
                {
                    'x': 2,
                    'y': 0,
                    'z': 1
                }
            ]
        }

    # implement __add__ method
    def __add__(self, other):
        return vectorFloat3d(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    # implement __sub__ method
    def __sub__(self, other):
        return vectorFloat3d(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)


class vectorInt3d(BaseModel):
    x: int = Field(0,
                   title='X - Axis')

    y: int = Field(0,
                   title='Y - Axis')

    z: int = Field(0,
                   title='Z - Axis')

    @classmethod
    def from_list(cls, values: list):
        return cls(x=values[0], y=values[1], z=values[2])

    @property
    def is_valid(self):
        return any(self.values)

    @property
    def values(self):
        return (self.x, self.y, self.z)

    def to_list(self):
        return [self.x, self.y, self.z]

    class Config:
        schema_extra = {
            'examples': [
                {
                    'x': 2,
                    'y': 0,
                    'z': 1
                }
            ]
        }

    # implement __add__ method
    def __add__(self, other):
        return vectorInt3d(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    # implement __sub__ method
    def __sub__(self, other):
        return vectorInt3d(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)
