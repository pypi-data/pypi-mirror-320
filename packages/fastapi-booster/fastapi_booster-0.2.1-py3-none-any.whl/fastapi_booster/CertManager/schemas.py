from typing import List
from pydantic import BaseModel, Field


class CA(BaseModel):
    country_name: str = Field("AU", description="The country name of the CA", max_length=2)
    state_or_province_name: str = Field("WA", description="The state or province name of the CA")
    locality_name: str = Field("Perth", description="The locality name of the CA")
    organization_name: str = Field("MyOrg", description="The organization name of the CA")
    organization_unit_name: str = Field("MyOrgUnit", description="The organization unit name of the CA")
    common_name: str = Field("MyCommonName", description="The common name of the CA")
    subject_alt_names: List[str] = Field([], description="The subject alternative names of the CA")


class Server(BaseModel):
    name: str = Field("MyServer", description="The name of the server")
    country_name: str = Field("AU", description="The country name of the server", max_length=2)
    state_or_province_name: str = Field("WA", description="The state or province name of the server")
    locality_name: str = Field("Perth", description="The locality name of the server")
    organization_name: str = Field("MyOrg", description="The organization name of the server")
    organization_unit_name: str = Field("MyOrgUnit", description="The organization unit name of the server")
    common_name: str = Field("MyCommonName", description="The common name of the server")
    alt_names: List[str] = Field([], description="The subject alternative names of the server")


class Client(BaseModel):
    name: str = Field("MyClient", description="The name of the client")
    country_name: str = Field("AU", description="The country name of the client", max_length=2)
    state_or_province_name: str = Field("WA", description="The state or province name of the client")
    locality_name: str = Field("Perth", description="The locality name of the client")
    organization_name: str = Field("MyOrg", description="The organization name of the client")
    organization_unit_name: str = Field("MyOrgUnit", description="The organization unit name of the client")
    common_name: str = Field("MyCommonName", description="The common name of the client")
    alt_names: List[str] = Field([], description="The subject alternative names of the client")
