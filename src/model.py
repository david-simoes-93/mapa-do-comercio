
from pydantic import BaseModel

class FrontEndObj(BaseModel, frozen=True):
    lat: float
    lng: float
    popup: str

class Coordinates(BaseModel, frozen=True):
    lat: float
    lon: float

class CompanyPage(BaseModel, frozen=True):
    url: str
    src: CompanySource
    details: CompanyDetails|None = None
    coords: Coordinates|None = None

class CompanySource(BaseModel, frozen=True):
    base: str
    distrito: str|None = None
    concelho: str|None = None
    freguesia: str|None = None

class CompanyDetails(BaseModel, frozen=True):
    name: str
    activity: str
    address: str
    postalcode: str
    locality: str 
    telephone: str
    email: str
    site: str|None = None
    
