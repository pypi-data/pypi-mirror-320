from __future__ import annotations 
from datetime import (
    datetime,
    date
)
from decimal import Decimal 
from enum import Enum 
import re
import sys
from typing import (
    Any,
    ClassVar,
    List,
    Literal,
    Dict,
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


linkml_meta = LinkMLMeta({'default_prefix': 'dct',
     'default_range': 'string',
     'description': 'SciDatS LinkML Metadata Model, based on the Dublin Core '
                    'Metadata Terms  of the Dublin Core Metadata Initiative '
                    '(DCMI).',
     'id': 'https://w3id.org/scidats/core_metadata_model',
     'imports': ['linkml:types'],
     'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
     'name': 'SciDatS-DCMI-Metadata-Model',
     'prefixes': {'dcat': {'prefix_prefix': 'dcat',
                           'prefix_reference': 'http://www.w3.org/ns/dcat#'},
                  'dct': {'prefix_prefix': 'dct',
                          'prefix_reference': 'http://purl.org/dc/terms/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'sh': {'prefix_prefix': 'sh',
                         'prefix_reference': 'https://w3id.org/shacl/'}},
     'source_file': 'metadata_model_scidats_dcmi.yaml'} )


class DCMIMetaData(ConfiguredBaseModel):
    """
    Metadata Terms of the Dublin Core Metadata Initiative (DCMI).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/scidats/core_metadata_model'})

    id: str = Field(..., description="""\"The identifier of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'http://purl.org/dc/terms/identifier'} })
    abstract: Optional[str] = Field(None, description="""\"A summary of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'abstract', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:abstract'} })
    accessRights: Optional[str] = Field(None, description="""\"Information about who can access the resource or an indication of its security status.
 Comment: Access Rights may include information regarding access or restrictions based on privacy, security, or other policies.\"""", json_schema_extra = { "linkml_meta": {'alias': 'accessRights',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:accessRights'} })
    accrualMethod: Optional[str] = Field(None, description="""\"The method by which items are added to a collection. 
 Comment: Recommended best practice is to use a controlled vocabulary such as the DCMI Collection Method Encoding Scheme [DC-COLLECTIONMETHOD].\"""", json_schema_extra = { "linkml_meta": {'alias': 'accrualMethod',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:accrualMethod'} })
    accrualPeriodicity: Optional[str] = Field(None, description="""\"The frequency with which items are added to a collection. 
 Comment: Recommended best practice is to use a controlled vocabulary such as the DCMI Collection Periodicity Encoding Scheme [DC-COLLECTIONPERIODICITY].\"""", json_schema_extra = { "linkml_meta": {'alias': 'accrualPeriodicity',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:accrualPeriodicity'} })
    accrualPolicy: Optional[str] = Field(None, description="""\"The policy governing the addition of items to a collection. 
 Comment: Recommended best practice is to use a controlled vocabulary such as the DCMI Collection Policy Statement Vocabulary [DC-COLLECTIONPOLICY].\"""", json_schema_extra = { "linkml_meta": {'alias': 'accrualPolicy',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:accrualPolicy'} })
    alternative: Optional[str] = Field(None, description="""\"An alternative name for the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'alternative',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:alternative'} })
    audience: Optional[str] = Field(None, description="""\"A class of entity for whom the resource is intended or useful.\"""", json_schema_extra = { "linkml_meta": {'alias': 'audience', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:audience'} })
    available: Optional[str] = Field(None, description="""\"Date (often a range) that the resource became or will become available.\"""", json_schema_extra = { "linkml_meta": {'alias': 'available',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:available'} })
    bibliographicCitation: Optional[str] = Field(None, description="""\"A bibliographic reference for the resource. 
 Comment: Recommended practice is to include sufficient bibliographic detail to identify the resource as unambiguously as possible.\"""", json_schema_extra = { "linkml_meta": {'alias': 'bibliographicCitation',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:bibliographicCitation'} })
    conformsTo: Optional[str] = Field(None, description="""\"An established standard to which the described resource conforms.\"""", json_schema_extra = { "linkml_meta": {'alias': 'conformsTo',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:conformsTo'} })
    contributor: Optional[str] = Field(None, description="""\"An entity responsible for making contributions to the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'contributor',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:contributor'} })
    coverage: Optional[str] = Field(None, description="""\"The spatial or temporal topic of the resource, the spatial applicability of the resource, or the jurisdiction under which the resource is relevant.\"""", json_schema_extra = { "linkml_meta": {'alias': 'coverage', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:coverage'} })
    created: Optional[str] = Field(None, description="""\"Date of creation of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'created', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:created'} })
    creator: Optional[str] = Field(None, description="""\"An entity primarily responsible for making the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'creator', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:creator'} })
    date: Optional[str] = Field(None, description="""\"A point or period of time associated with an event in the lifecycle of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'date', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:date'} })
    dateAccepted: Optional[str] = Field(None, description="""\"Date of acceptance of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'dateAccepted',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:dateAccepted'} })
    dateAvailable: Optional[str] = Field(None, description="""\"Date (often a range) of availability of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'dateAvailable',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:dateAvailable'} })
    dateCopyrighted: Optional[str] = Field(None, description="""\"Date of copyright.
 Comment: Typically a year. Recommended practice is to describe the date, date/time, or period of time 
 as recommended for the property Date, of which this is a subproperty.\"""", json_schema_extra = { "linkml_meta": {'alias': 'dateCopyrighted',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:dateCopyrighted'} })
    dateSubmitted: Optional[str] = Field(None, description="""\"Date of submission of the resource.
 Comment:Recommended practice is to describe the date, date/time, or period of time as recommended for the property Date, 
 of which this is a subproperty. Examples of resources to which a 'Date Submitted' may be relevant include a thesis 
 (submitted to a university department) or an article (submitted to a journal).\"""", json_schema_extra = { "linkml_meta": {'alias': 'dateSubmitted',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:dateSubmitted'} })
    description: Optional[str] = Field(None, description="""\"An account of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:description'} })
    educationLevel: Optional[str] = Field(None, description="""\"A class of entity, defined in terms of progression through an educational or training context,  for which the described resource is intended.\"""", json_schema_extra = { "linkml_meta": {'alias': 'educationLevel',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:educationLevel'} })
    extent: Optional[str] = Field(None, description="""\"The size or duration of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'extent', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:extent'} })
    format: Optional[str] = Field(None, description="""\"The file format, physical medium, or dimensions of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'format', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:format'} })
    hasFormat: Optional[str] = Field(None, description="""\"A related resource that is substantially the same as the pre-existing described resource, but in another format.\"""", json_schema_extra = { "linkml_meta": {'alias': 'hasFormat',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:hasFormat'} })
    hasPart: Optional[str] = Field(None, description="""\"A related resource that is included either physically or logically in the described resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'hasPart', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:hasPart'} })
    hasVersion: Optional[str] = Field(None, description="""\"A related resource that is a version, edition, or adaptation of the described resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'hasVersion',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:hasVersion'} })
    identifier: Optional[str] = Field(None, description="""\"An unambiguous reference to the resource within a given context.\"""", json_schema_extra = { "linkml_meta": {'alias': 'identifier',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:identifier'} })
    instructionalMethod: Optional[str] = Field(None, description="""\"A process, used to engender knowledge, attitudes and skills, that the described resource is designed to support.\"""", json_schema_extra = { "linkml_meta": {'alias': 'instructionalMethod',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:instructionalMethod'} })
    isFormatOf: Optional[str] = Field(None, description="""\"A pre-existing related resource that is substantially the same as the described resource, but in another format.\"""", json_schema_extra = { "linkml_meta": {'alias': 'isFormatOf',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:isFormatOf'} })
    isPartOf: Optional[str] = Field(None, description="""\"A related resource in which the described resource is physically or logically included.\"""", json_schema_extra = { "linkml_meta": {'alias': 'isPartOf', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:isPartOf'} })
    isReferencedBy: Optional[str] = Field(None, description="""\"A related resource that references, cites, or otherwise points to the described resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'isReferencedBy',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:isReferencedBy'} })
    isReplacedBy: Optional[str] = Field(None, description="""\"A related resource that supplants, displaces, or supersedes the described resource.
 Comment: This property is intended to be used with non-literal values. This property is an inverse property of Replaces.\"""", json_schema_extra = { "linkml_meta": {'alias': 'isReplacedBy',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:isReplacedBy'} })
    isRequiredBy: Optional[str] = Field(None, description="""\"A related resource that requires the described resource to support its function, delivery, or coherence.
 Comment: This property is intended to be used with non-literal values. This property is an inverse property of Requires.\"""", json_schema_extra = { "linkml_meta": {'alias': 'isRequiredBy',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:isRequiredBy'} })
    issued: Optional[str] = Field(None, description="""\"Date of formal issuance (e.g., publication) of the resource.
 Comment: Recommended practice is to describe the date, date/time, or period of time as recommended for the property Date, of which this is a subproperty.\"""", json_schema_extra = { "linkml_meta": {'alias': 'issued', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:issued'} })
    isVersionOf: Optional[str] = Field(None, description="""\"A related resource of which the described resource is a version, edition, or adaptation.\"""", json_schema_extra = { "linkml_meta": {'alias': 'isVersionOf',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:isVersionOf'} })
    language: Optional[str] = Field(None, description="""\"A language of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'language', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:language'} })
    license: Optional[str] = Field(None, description="""\"A legal document giving official permission to do something with the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'license', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:license'} })
    mediator: Optional[str] = Field(None, description="""\"An entity that mediates access to the resource and for whom the resource is intended or useful.\"""", json_schema_extra = { "linkml_meta": {'alias': 'mediator', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:mediator'} })
    medium: Optional[str] = Field(None, description="""\"The material or physical carrier of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'medium', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:medium'} })
    modified: Optional[str] = Field(None, description="""\"Date on which the resource was changed.
 Comment: Recommended practice is to describe the date, date/time, or period of time as recommended for the property Date, of which this is a subproperty.\"""", json_schema_extra = { "linkml_meta": {'alias': 'modified', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:modified'} })
    provenance: Optional[str] = Field(None, description="""\"A statement of any changes in ownership and custody of the resource since its creation that are significant for its authenticity, integrity, and interpretation.\"""", json_schema_extra = { "linkml_meta": {'alias': 'provenance',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:provenance'} })
    publisher: Optional[str] = Field(None, description="""\"An entity responsible for making the resource available.\"""", json_schema_extra = { "linkml_meta": {'alias': 'publisher',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:publisher'} })
    references: Optional[str] = Field(None, description="""\"A related resource that is referenced, cited, or otherwise pointed to by the described resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'references',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:references'} })
    relation: Optional[str] = Field(None, description="""\"A related resource.
 Comment: Recommended practice is to identify the related resource by means of a string conforming to a formal identification system.\"""", json_schema_extra = { "linkml_meta": {'alias': 'relation', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:relation'} })
    replaces: Optional[str] = Field(None, description="""\"A related resource that supplants, displaces, or supersedes the described resource.
 Comment: This property is intended to be used with non-literal values. This property is an inverse property of Is Replaced By.\"""", json_schema_extra = { "linkml_meta": {'alias': 'replaces', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:replaces'} })
    requires: Optional[str] = Field(None, description="""\"A related resource that is required by the described resource to support its function, delivery, or coherence.
 Comment: This property is intended to be used with non-literal values. This property is an inverse property of Is Required By.\"""", json_schema_extra = { "linkml_meta": {'alias': 'requires', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:requires'} })
    rights: Optional[str] = Field(None, description="""\"Information about rights held in and over the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'rights', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:rights'} })
    rightsHolder: Optional[str] = Field(None, description="""\"A person or organization owning or managing rights over the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'rightsHolder',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:rightsHolder'} })
    source: Optional[str] = Field(None, description="""\"A related resource from which the described resource is derived.\"""", json_schema_extra = { "linkml_meta": {'alias': 'source', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:source'} })
    spatial: Optional[str] = Field(None, description="""\"Spatial characteristics of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'spatial', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:spatial'} })
    subject: Optional[str] = Field(None, description="""\"The topic of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'subject', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:subject'} })
    tableOfContents: Optional[str] = Field(None, description="""\"A list of subunits of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'tableOfContents',
         'domain_of': ['DCMIMetaData'],
         'slot_uri': 'dct:tableOfContents'} })
    temporal: Optional[str] = Field(None, description="""\"Temporal characteristics of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'temporal', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:temporal'} })
    title: Optional[str] = Field(None, description="""\"A name given to the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'title', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:title'} })
    type: Optional[str] = Field(None, description="""\"The nature or genre of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'type', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:type'} })
    valid: Optional[str] = Field(None, description="""\"Date (often a range) of validity of a resource.
 Comment: Recommended practice is to describe the date, date/time, or period of time as recommended for the property Date, of which this is a subproperty.\"""", json_schema_extra = { "linkml_meta": {'alias': 'valid', 'domain_of': ['DCMIMetaData'], 'slot_uri': 'dct:valid'} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
DCMIMetaData.model_rebuild()

