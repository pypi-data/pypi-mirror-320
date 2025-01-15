from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "0.0.1"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'oso',
     'default_range': 'string',
     'description': 'SciDatS LinkML Core Metadata Model.',
     'id': 'https://w3id.org/SciDatS/core_metadata_model',
     'imports': ['linkml:types'],
     'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
     'name': 'SciDatS-Core-Metadata-Model',
     'prefixes': {'OM': {'prefix_prefix': 'OM',
                         'prefix_reference': 'http://www.ontology-of-units-of-measure.org/resource/om-2/'},
                  'UO': {'prefix_prefix': 'UO',
                         'prefix_reference': 'http://purl.obolibrary.org/obo/UO_'},
                  'dcat': {'prefix_prefix': 'dcat',
                           'prefix_reference': 'http://www.w3.org/ns/dcat#'},
                  'dcatap': {'prefix_prefix': 'dcatap',
                             'prefix_reference': 'http://data.europa.eu/m8g/'},
                  'dcmi': {'prefix_prefix': 'dcmi',
                           'prefix_reference': 'http://purl.org/dc/dcmitype/'},
                  'dct': {'prefix_prefix': 'dct',
                          'prefix_reference': 'http://purl.org/dc/terms/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'oso': {'prefix_prefix': 'oso',
                          'prefix_reference': 'http://w3id.org/oso/'},
                  'qudt': {'prefix_prefix': 'qudt',
                           'prefix_reference': 'http://qudt.org/schema/qudt/'},
                  'sh': {'prefix_prefix': 'sh',
                         'prefix_reference': 'https://w3id.org/shacl/'}},
     'source_file': 'metadata_model_scidats_core.yaml',
     'types': {'NaN': {'base': 'float',
                       'description': 'Not-A-Number (NaN) is a numeric data type '
                                      'value representing an undefined or '
                                      'un-representable value.',
                       'exact_mappings': ['schema:NaN', 'python:np.nan'],
                       'from_schema': 'https://w3id.org/SciDatS/core_metadata_model',
                       'name': 'NaN',
                       'notes': ['If you are authoring schemas in LinkML YAML, the '
                                 'type is referenced with the lower case '
                                 '"integer".'],
                       'repr': 'np.nan',
                       'uri': 'xsd:float'}}} )


class Person(ConfiguredBaseModel):
    """
    \"The User class represents a user of the SciDatS system.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'oso:entity',
         'from_schema': 'https://w3id.org/SciDatS/core_metadata_model'})

    name_last: str = Field(..., description="""\"The last name of the user.\"""", json_schema_extra = { "linkml_meta": {'alias': 'name_last',
         'domain_of': ['Person'],
         'slot_uri': 'oso:entity/lastName'} })
    name_first: str = Field(..., description="""\"The first name of the user.\"""", json_schema_extra = { "linkml_meta": {'alias': 'name_first',
         'domain_of': ['Person'],
         'slot_uri': 'oso:entity/firstName'} })
    orcid: str = Field(..., description="""\"The Open Researcher and Contributor ID [ORCID](https://orcid.org/) of a researcher.\"""", json_schema_extra = { "linkml_meta": {'alias': 'orcid', 'domain_of': ['Person'], 'slot_uri': 'oso:entity/ORCID'} })
    email: Optional[str] = Field(None, description="""\"The email address of the user.\"""", json_schema_extra = { "linkml_meta": {'alias': 'email', 'domain_of': ['Person'], 'slot_uri': 'oso:entity/email'} })


class SciDatSMetaDataCore(ConfiguredBaseModel):
    """
    \"The SciDatSMetaDataCore class represents the core metadata model for SciDatS serialised data.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'oso:metadata/SciDatSMetaDataCore',
         'from_schema': 'https://w3id.org/SciDatS/core_metadata_model'})

    id: str = Field(..., description="""\"The identifier of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'http://purl.org/dc/terms/identifier'} })
    timestamp: datetime  = Field(..., description="""\"The timestamp of the measurement in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).\"""", json_schema_extra = { "linkml_meta": {'alias': 'timestamp',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'http://purl.org/dc/terms/date'} })
    description: Optional[str] = Field(None, description="""\"A description of the calculation / measurement.\"""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'http://purl.org/dc/terms/description'} })
    contributors: Optional[List[Person]] = Field(None, description="""\"The people involved (or contributed) in the measurement. Structured as: \"Lastname, Firstname\"""", json_schema_extra = { "linkml_meta": {'alias': 'contributors',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'dct:contributor'} })
    checksum_previous: Optional[str] = Field(None, description="""\"The checksum (SHA256) of the previous dataset and corresponding metadata. This can be used for block-chaining data series.\"""", json_schema_extra = { "linkml_meta": {'alias': 'checksum_previous',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/sha256checksum'} })
    method: str = Field(..., description="""\"The name of the physical method.\"""", json_schema_extra = { "linkml_meta": {'alias': 'method',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'dcmi:method',
         'source': 'dcmi:method'} })
    procedure_name: str = Field(..., description="""\"The name of the measurement / simulation / calculation procedure.\"""", json_schema_extra = { "linkml_meta": {'alias': 'procedure_name',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/procedure',
         'source': 'oso:measurement/procedure'} })
    session_name: str = Field(..., description="""\"The name of the measurement session.\"""", json_schema_extra = { "linkml_meta": {'alias': 'session_name',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/session'} })
    software: str = Field(..., description="""\"The name of the software with which the measurement / simulation / calculation was made.\"""", json_schema_extra = { "linkml_meta": {'alias': 'software',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/software'} })
    software_version: str = Field(..., description="""\"The version of the software with which the measurement / simulation / calculation was made.\"""", json_schema_extra = { "linkml_meta": {'alias': 'software_version',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/softwareVersion'} })
    device_type: Optional[str] = Field(None, description="""\"The type / class of the device. E.g. Gas Chromatograph, NMR. Thermometer, etc.\"""", json_schema_extra = { "linkml_meta": {'alias': 'device_type',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/deviceType'} })
    device_manufacturer_name: Optional[str] = Field(None, description="""\"Manufacturer of the device.\"""", json_schema_extra = { "linkml_meta": {'alias': 'device_manufacturer_name',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/deviceManufacturerName'} })
    device_name: Optional[str] = Field(None, description="""\"The full name of the device.\"""", json_schema_extra = { "linkml_meta": {'alias': 'device_name',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/deviceName'} })
    device_model_name: Optional[str] = Field(None, description="""\"The model of the device.\"""", json_schema_extra = { "linkml_meta": {'alias': 'device_model_name',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/deviceModel'} })
    device_version: Optional[str] = Field(None, description="""\"The version of the device.\"""", json_schema_extra = { "linkml_meta": {'alias': 'device_version',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/deviceVersion'} })
    device_serial: Optional[str] = Field(None, description="""\"The serial number of the measurement device.\"""", json_schema_extra = { "linkml_meta": {'alias': 'device_serial',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/deviceSerial'} })
    device_pid: Optional[str] = Field(None, description="""\"The persistent identifier (PID) of the measurement device.\"""", json_schema_extra = { "linkml_meta": {'alias': 'device_pid',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:measurement/devicePID'} })
    geolocation: str = Field(..., description="""\"The geological location where the measurement was done.\"""", json_schema_extra = { "linkml_meta": {'alias': 'geolocation',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:environment/geolocation'} })
    altitude: float = Field(..., description="""\"The geological altitude of the location at which the measurement was done.\"""", json_schema_extra = { "linkml_meta": {'alias': 'altitude',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:environment/altitude',
         'unit': {'has_quantity_kind': 'OM:Length', 'ucum_code': 'm'}} })
    environment_temperature: float = Field(..., description="""\"The average temperature of the environment / laboratory during the time at which the measurement was done.\"""", json_schema_extra = { "linkml_meta": {'alias': 'environment_temperature',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:environment/environmentTemperature',
         'unit': {'has_quantity_kind': 'OM:Temperature', 'ucum_code': 'K'}} })
    environment_air_pressure: float = Field(..., description="""\"The average air pressure of the environment / laboratory during the time at which the measurement was done.\"""", json_schema_extra = { "linkml_meta": {'alias': 'environment_air_pressure',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:environment/environmentAirPressure',
         'unit': {'has_quantity_kind': 'OM:Pressure', 'ucum_code': 'N/m^2'}} })
    environment_air_humidity: float = Field(..., description="""\"The average air humidity of the environment / during the time at which the measurement was done.\"""", json_schema_extra = { "linkml_meta": {'alias': 'environment_air_humidity',
         'domain_of': ['SciDatSMetaDataCore'],
         'slot_uri': 'oso:environment/environmentAirHumidity'} })


class Visualisations2D(ConfiguredBaseModel):
    """
    \"recommendations for 2D visualisations of the data.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/SciDatS/core_metadata_model'})

    visualisation: Optional[List[str]] = Field(None, description="""\"A set of recommended 2D visualisations for the associated data.\"""", json_schema_extra = { "linkml_meta": {'alias': 'visualisation',
         'domain_of': ['Visualisations2D', 'Visualisation3D'],
         'slot_uri': 'oso:measurements/visualisations2D'} })
    defaultVisualisation: Optional[str] = Field(None, description="""\"The default (recommended) 2D visualisation for the associated data.\"""", json_schema_extra = { "linkml_meta": {'alias': 'defaultVisualisation',
         'domain_of': ['Visualisations2D', 'Visualisation3D']} })


class Visualisation3D(ConfiguredBaseModel):
    """
    \"recommendations for 3D visualisations of the data.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/SciDatS/core_metadata_model'})

    visualisation: Optional[List[str]] = Field(None, description="""\"A set of recommended 3D visualisations for the associated data.\"""", json_schema_extra = { "linkml_meta": {'alias': 'visualisation',
         'domain_of': ['Visualisations2D', 'Visualisation3D'],
         'slot_uri': 'oso:measurements/visualisations3D'} })
    defaultVisualisation: Optional[str] = Field(None, description="""\"The default (recommended) 3D visualisation for the associated data.\"""", json_schema_extra = { "linkml_meta": {'alias': 'defaultVisualisation',
         'domain_of': ['Visualisations2D', 'Visualisation3D']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Person.model_rebuild()
SciDatSMetaDataCore.model_rebuild()
Visualisations2D.model_rebuild()
Visualisation3D.model_rebuild()

