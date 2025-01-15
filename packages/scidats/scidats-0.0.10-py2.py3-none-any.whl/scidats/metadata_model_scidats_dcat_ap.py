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


linkml_meta = LinkMLMeta({'default_prefix': 'https://w3id.org/scidats/core_metadata_model/',
     'description': 'DCAT-AP-Metadata Model based on Dublin Core Terms (DCT) and '
                    'Data Catalog Vocabulary (DCAT) Application Profile (AP).  '
                    'Data Catalog Vocabulary (DCAT) is an RDF vocabulary designed '
                    'to facilitate interoperability between data catalogs '
                    'published on the Web.',
     'id': 'https://w3id.org/scidats/core_metadata_model',
     'imports': ['linkml:types'],
     'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
     'name': 'DCAT-AP-Metadata-Model',
     'prefixes': {'dcat': {'prefix_prefix': 'dcat',
                           'prefix_reference': 'http://www.w3.org/ns/dcat#'},
                  'dcatap': {'prefix_prefix': 'dcatap',
                             'prefix_reference': 'http://data.europa.eu/m8g/'},
                  'dct': {'prefix_prefix': 'dct',
                          'prefix_reference': 'http://purl.org/dc/terms/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'prov': {'prefix_prefix': 'prov',
                           'prefix_reference': 'http://www.w3.org/ns/prov#'},
                  'sh': {'prefix_prefix': 'sh',
                         'prefix_reference': 'https://w3id.org/shacl/'},
                  'xsd': {'prefix_prefix': 'xsd',
                          'prefix_reference': 'http://www.w3.org/2001/XMLSchema#'}},
     'source_file': 'metadata_model_scidats_dcat_ap.yaml'} )


class Activity(ConfiguredBaseModel):
    """
    \"An activity, e.g., a workflow or process.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'prov:Activity'})

    name: List[str] = Field(..., description="""\"The name of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Activity', 'Agent'],
         'slot_uri': 'http://xmlns.com/foaf/0.1/name'} })


class Agent(ConfiguredBaseModel):
    """
    \"A person, organization, or software agent.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'prov:Agent'})

    name: List[str] = Field(..., description="""\"The name of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Activity', 'Agent'],
         'slot_uri': 'http://xmlns.com/foaf/0.1/name'} })


class Attribution(ConfiguredBaseModel):
    """
    \"A statement of attribution for the resource.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'prov:Attribution'})

    pass


class Catalogue(ConfiguredBaseModel):
    """
    \"A collection of metadata records.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#Catalog',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'dcat:catalog'})

    catalogue: List[str] = Field(..., description="""\"The catalouge of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'catalogue',
         'domain_of': ['Catalogue'],
         'slot_uri': 'http://www.w3.org/ns/dcat#catalog'} })
    creator: str = Field(..., description="""\"The creator of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'creator',
         'domain_of': ['Catalogue', 'Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/creator'} })
    dataset: List[str] = Field(..., description="""\"The dataset of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'dataset',
         'domain_of': ['Catalogue'],
         'slot_uri': 'http://www.w3.org/ns/dcat#dataset'} })
    description: str = Field(..., description="""\"A description of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/description'} })
    geographicalCoverage: Optional[List[str]] = Field(None, description="""\"The geographical coverage of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'geographicalCoverage',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#geographicalCoverage'} })
    hasPart: Optional[List[str]] = Field(None, description="""\"The part of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'hasPart',
         'domain_of': ['Catalogue'],
         'slot_uri': 'http://purl.org/dc/terms/hasPart'} })
    homepage: str = Field(..., description="""\"The homepage of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'homepage',
         'domain_of': ['Catalogue'],
         'slot_uri': 'http://xmlns.com/foaf/0.1/homepage'} })
    isPartOf: Optional[str] = Field(None, description="""\"The part of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'isPartOf',
         'domain_of': ['Catalogue'],
         'slot_uri': 'http://purl.org/dc/terms/isPartOf'} })
    language: List[str] = Field(..., description="""\"The language of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'language',
         'domain_of': ['Catalogue', 'CatalogueRecord', 'Dataset', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/language'} })
    license: str = Field(..., description="""\"The license of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'license',
         'domain_of': ['Catalogue', 'DataService', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/license'} })
    modificationDate: str = Field(..., description="""\"The modification date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'modificationDate',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'Dataset',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/modified'} })
    publisher: str = Field(..., description="""\"The publisher of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'publisher',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries'],
         'slot_uri': 'http://purl.org/dc/terms/publisher'} })
    record: List[str] = Field(..., description="""\"The record of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'record',
         'domain_of': ['Catalogue'],
         'slot_uri': 'http://www.w3.org/ns/dcat#record'} })
    releaseDate: str = Field(..., description="""\"The release date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'releaseDate',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/issued'} })
    rights: str = Field(..., description="""\"The rights of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'rights',
         'domain_of': ['Catalogue', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/rights'} })
    service: Optional[List[str]] = Field(None, description="""\"The service of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'service',
         'domain_of': ['Catalogue'],
         'slot_uri': 'http://www.w3.org/ns/dcat#service'} })
    temporalCoverage: Optional[List[str]] = Field(None, description="""\"The temporal coverage of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'temporalCoverage',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#temporalCoverage'} })
    themes: Optional[List[str]] = Field(None, description="""\"The themes of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'themes',
         'domain_of': ['Catalogue'],
         'slot_uri': 'http://www.w3.org/ns/dcat#themeTaxonomy'} })
    title: str = Field(..., description="""\"The title of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'title',
         'domain_of': ['Catalogue',
                       'ConceptScheme',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/title'} })


class CatalogueRecord(ConfiguredBaseModel):
    """
    \"A record in a catalogue.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#CatalogRecord',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#record'})

    applicationProfile: Optional[str] = Field(None, description="""\"The application profile of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'applicationProfile',
         'domain_of': ['CatalogueRecord'],
         'slot_uri': 'http://purl.org/dc/terms/conformsTo'} })
    changeType: Optional[str] = Field(None, description="""\"The change type of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'changeType',
         'domain_of': ['CatalogueRecord'],
         'slot_uri': 'http://www.w3.org/ns/adms#status'} })
    description: str = Field(..., description="""\"A description of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/description'} })
    language: List[str] = Field(..., description="""\"The language of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'language',
         'domain_of': ['Catalogue', 'CatalogueRecord', 'Dataset', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/language'} })
    listingDate: Optional[str] = Field(None, description="""\"The listing date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'listingDate',
         'domain_of': ['CatalogueRecord'],
         'slot_uri': 'http://purl.org/dc/terms/issued'} })
    modificationDate: str = Field(..., description="""\"The modification date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'modificationDate',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'Dataset',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/modified'} })
    primaryTopic: Optional[str] = Field(None, description="""\"The primary topic of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'primaryTopic',
         'domain_of': ['CatalogueRecord'],
         'slot_uri': 'http://xmlns.com/foaf/0.1/primaryTopic'} })
    sourceMetadata: Optional[str] = Field(None, description="""\"The source metadata of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'sourceMetadata',
         'domain_of': ['CatalogueRecord'],
         'slot_uri': 'http://www.w3.org/ns/dcat#source'} })


class CataloguedResource(ConfiguredBaseModel):
    """
    \"A resource that is catalogued.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#Resource'})

    pass


class Checksum(ConfiguredBaseModel):
    """
    \"A checksum of the resource.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://spdx.org/rdf/terms#Checksum',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'https://www.w3.org/ns/prov#Checksum'})

    algorithm: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'algorithm',
         'domain_of': ['Checksum'],
         'slot_uri': 'http://spdx.org/rdf/terms#algorithm'} })
    checksumValue: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'checksumValue',
         'domain_of': ['Checksum'],
         'slot_uri': 'http://spdx.org/rdf/terms#checksumValue'} })


class ChecksumAlgorithm(ConfiguredBaseModel):
    """
    \"The algorithm used to compute the checksum.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://spdx.org/rdf/terms#ChecksumAlgorithm'})

    pass


class Concept(ConfiguredBaseModel):
    """
    \"An idea or notion; a unit of thought.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/2004/02/skos/core#Concept',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/2004/02/skos/core#Concept'})

    preferredLabel: Optional[str] = Field(None, description="""\"The preferred label of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'preferredLabel',
         'domain_of': ['Concept'],
         'slot_uri': 'http://www.w3.org/2004/02/skos/core#prefLabel'} })


class ConceptScheme(ConfiguredBaseModel):
    """
    \"A set of concepts.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/2004/02/skos/core#ConceptScheme',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model'})

    title: str = Field(..., description="""\"The title of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'title',
         'domain_of': ['Catalogue',
                       'ConceptScheme',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/title'} })


class DataService(ConfiguredBaseModel):
    """
    \"A service that provides access to data.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#DataService',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#service'})

    description: str = Field(..., description="""\"A description of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/description'} })
    license: str = Field(..., description="""\"The license of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'license',
         'domain_of': ['Catalogue', 'DataService', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/license'} })
    title: str = Field(..., description="""\"The title of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'title',
         'domain_of': ['Catalogue',
                       'ConceptScheme',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/title'} })
    accessRights: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'accessRights',
         'domain_of': ['DataService', 'Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/accessRights'} })
    endpointURL: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'endpointURL',
         'domain_of': ['DataService'],
         'slot_uri': 'http://www.w3.org/ns/dcat#endpointURL'} })
    servesDataset: Optional[str] = Field(None, json_schema_extra = { "linkml_meta": {'alias': 'servesDataset',
         'domain_of': ['DataService'],
         'slot_uri': 'http://www.w3.org/ns/dcat#servesDataset'} })


class Dataset(ConfiguredBaseModel):
    """
    \"A collection of data, published or curated by a single agent.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#Dataset',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#dataset'})

    accessRights: Optional[str] = Field(None, description="""\"The access rights of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'accessRights',
         'domain_of': ['DataService', 'Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/accessRights'} })
    conformsTo: Optional[List[str]] = Field(None, description="""\"The conforms to of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'conformsTo',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/conformsTo'} })
    contactPoint: Optional[List[str]] = Field(None, description="""\"The contact point of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'contactPoint',
         'domain_of': ['Dataset', 'DatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#contactPoint'} })
    creator: str = Field(..., description="""\"The creator of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'creator',
         'domain_of': ['Catalogue', 'Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/creator'} })
    datasetDistribution: Optional[List[str]] = Field(None, description="""\"The dataset distribution of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'datasetDistribution',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://www.w3.org/ns/dcat#distribution'} })
    description: str = Field(..., description="""\"A description of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/description'} })
    documentation: Optional[List[str]] = Field(None, description="""\"The documentation of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'documentation',
         'domain_of': ['Dataset', 'Distribution'],
         'slot_uri': 'http://xmlns.com/foaf/0.1/page'} })
    frequency: Optional[str] = Field(None, description="""\"The frequency of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'frequency',
         'domain_of': ['Dataset', 'DatasetMemberOfDatasetSeries', 'DatasetSeries'],
         'slot_uri': 'http://purl.org/dc/terms/accrualPeriodicity'} })
    geographicalCoverage: Optional[List[str]] = Field(None, description="""\"The geographical coverage of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'geographicalCoverage',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#geographicalCoverage'} })
    hasVersion: Optional[List[str]] = Field(None, description="""\"The has version of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'hasVersion',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/hasVersion'} })
    identifier: Optional[str] = Field(None, description="""\"The identifier of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'identifier',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/identifier'} })
    isReferencedBy: Optional[List[str]] = Field(None, description="""\"The is referenced by of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'isReferencedBy',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/isReferencedBy'} })
    isVersionOf: Optional[List[str]] = Field(None, description="""\"The is version of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'isVersionOf',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/isVersionOf'} })
    keyword: Optional[List[str]] = Field(None, description="""\"The keyword of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'keyword',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://www.w3.org/ns/dcat#keyword'} })
    landingPage: Optional[List[str]] = Field(None, description="""\"The landing page of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'landingPage',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://xmlns.com/foaf/0.1/page'} })
    language: List[str] = Field(..., description="""\"The language of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'language',
         'domain_of': ['Catalogue', 'CatalogueRecord', 'Dataset', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/language'} })
    modificationDate: str = Field(..., description="""\"The modification date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'modificationDate',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'Dataset',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/modified'} })
    otherIdentifier: Optional[List[str]] = Field(None, description="""\"The other identifier of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'otherIdentifier',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/identifier'} })
    provenance: Optional[List[str]] = Field(None, description="""\"The provenance of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'provenance',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://www.w3.org/ns/prov#wasDerivedFrom'} })
    publisher: str = Field(..., description="""\"The publisher of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'publisher',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries'],
         'slot_uri': 'http://purl.org/dc/terms/publisher'} })
    qualifiedAttribution: Optional[List[str]] = Field(None, description="""\"The qualified attribution of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'qualifiedAttribution',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://www.w3.org/ns/prov#qualifiedAttribution'} })
    qualifiedRelation: Optional[List[str]] = Field(None, description="""\"The qualified relation of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'qualifiedRelation',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://www.w3.org/ns/prov#qualifiedRelation'} })
    relatedResource: Optional[List[str]] = Field(None, description="""\"The related resource of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'relatedResource',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://www.w3.org/ns/dcat#relatedResource'} })
    releaseDate: str = Field(..., description="""\"The release date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'releaseDate',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/issued'} })
    sample: Optional[List[str]] = Field(None, description="""\"The sample of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'sample',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://www.w3.org/ns/dcat#sample'} })
    source: Optional[List[str]] = Field(None, description="""\"The source of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'source',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://www.w3.org/ns/dcat#source'} })
    spatialResolution: Optional[List[str]] = Field(None, description="""\"The spatial resolution of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'spatialResolution',
         'domain_of': ['Dataset', 'Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#spatialResolutionInMeters'} })
    temporalCoverage: Optional[List[str]] = Field(None, description="""\"The temporal coverage of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'temporalCoverage',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#temporalCoverage'} })
    temporalResolution: Optional[List[str]] = Field(None, description="""\"The temporal resolution of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'temporalResolution',
         'domain_of': ['Dataset', 'Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#temporalResolution'} })
    theme: Optional[List[str]] = Field(None, description="""\"The theme of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'theme',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://www.w3.org/ns/dcat#theme'} })
    title: str = Field(..., description="""\"The title of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'title',
         'domain_of': ['Catalogue',
                       'ConceptScheme',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/title'} })
    type: Optional[List[str]] = Field(None, description="""\"The type of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'type',
         'domain_of': ['Dataset', 'LicenseDocument'],
         'slot_uri': 'http://www.w3.org/ns/dcat#type'} })
    version: Optional[List[str]] = Field(None, description="""\"The version of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'version',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/hasVersion'} })
    versionNotes: Optional[List[str]] = Field(None, description="""\"The version notes of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'versionNotes',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://purl.org/dc/terms/replaces'} })
    wasGeneratedBy: Optional[List[str]] = Field(None, description="""\"The was generated by of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'wasGeneratedBy',
         'domain_of': ['Dataset'],
         'slot_uri': 'http://www.w3.org/ns/prov#wasGeneratedBy'} })


class DatasetMemberOfDatasetSeries(ConfiguredBaseModel):
    """
    \"A dataset that is a member of a dataset series.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#Dataset',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#Dataset'})

    description: str = Field(..., description="""\"A description of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/description'} })
    frequency: Optional[str] = Field(None, description="""\"The frequency of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'frequency',
         'domain_of': ['Dataset', 'DatasetMemberOfDatasetSeries', 'DatasetSeries'],
         'slot_uri': 'http://purl.org/dc/terms/accrualPeriodicity'} })
    inSeries: Optional[str] = Field(None, description="""\"The in series of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'inSeries',
         'domain_of': ['DatasetMemberOfDatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#inSeries'} })
    next: Optional[str] = Field(None, description="""\"The next of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'next',
         'domain_of': ['DatasetMemberOfDatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#next'} })
    previous: Optional[str] = Field(None, description="""\"The previous of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'previous',
         'domain_of': ['DatasetMemberOfDatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#prev'} })
    title: str = Field(..., description="""\"The title of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'title',
         'domain_of': ['Catalogue',
                       'ConceptScheme',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/title'} })


class DatasetSeries(ConfiguredBaseModel):
    """
    \"A series of datasets.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#DatasetSeries',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#DatasetSeries'})

    contactPoint: Optional[List[str]] = Field(None, description="""\"The contact point of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'contactPoint',
         'domain_of': ['Dataset', 'DatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#contactPoint'} })
    description: str = Field(..., description="""\"A description of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/description'} })
    frequency: Optional[str] = Field(None, description="""\"The frequency of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'frequency',
         'domain_of': ['Dataset', 'DatasetMemberOfDatasetSeries', 'DatasetSeries'],
         'slot_uri': 'http://purl.org/dc/terms/accrualPeriodicity'} })
    geographicalCoverage: Optional[List[str]] = Field(None, description="""\"The geographical coverage of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'geographicalCoverage',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#geographicalCoverage'} })
    last: Optional[str] = Field(None, description="""\"The last of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'last',
         'domain_of': ['DatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#last'} })
    modificationDate: str = Field(..., description="""\"The modification date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'modificationDate',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'Dataset',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/modified'} })
    publisher: str = Field(..., description="""\"The publisher of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'publisher',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries'],
         'slot_uri': 'http://purl.org/dc/terms/publisher'} })
    releaseDate: str = Field(..., description="""\"The release date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'releaseDate',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/issued'} })
    seriesMember: Optional[List[str]] = Field(None, description="""\"The series member of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'seriesMember',
         'domain_of': ['DatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#member'} })
    temporalCoverage: Optional[List[str]] = Field(None, description="""\"The temporal coverage of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'temporalCoverage',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries'],
         'slot_uri': 'http://www.w3.org/ns/dcat#temporalCoverage'} })
    title: str = Field(..., description="""\"The title of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'title',
         'domain_of': ['Catalogue',
                       'ConceptScheme',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/title'} })


class Distribution(ConfiguredBaseModel):
    """
    \"A specific representation of a dataset.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#Distribution',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#distribution'})

    accessService: Optional[List[str]] = Field(None, description="""\"The access service of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'accessService',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#accessService'} })
    accessURL: Optional[List[str]] = Field(None, description="""\"The access URL of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'accessURL',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#accessURL'} })
    availability: Optional[str] = Field(None, description="""\"The availability of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'availability',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#availability'} })
    byteSize: Optional[str] = Field(None, description="""\"The byte size of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'byteSize',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#byteSize'} })
    checksum: Optional[str] = Field(None, description="""\"The checksum of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'checksum',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#checksum'} })
    compressionFormat: Optional[str] = Field(None, description="""\"The compress format of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'compressionFormat',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#compressionFormat'} })
    downloadURL: Optional[str] = Field(None, description="""\"The download URL of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'downloadURL',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#downloadURL'} })
    description: str = Field(..., description="""\"A description of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/description'} })
    documentation: Optional[List[str]] = Field(None, description="""\"The documentation of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'documentation',
         'domain_of': ['Dataset', 'Distribution'],
         'slot_uri': 'http://xmlns.com/foaf/0.1/page'} })
    format: str = Field(..., description="""\"The format of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'format',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/format'} })
    hasPolicy: Optional[str] = Field(None, description="""\"The has policy of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'hasPolicy',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#hasPolicy'} })
    linkedSchemas: Optional[str] = Field(None, description="""\"The linked schemas of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'linkedSchemas',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#linkedSchemas'} })
    language: List[str] = Field(..., description="""\"The language of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'language',
         'domain_of': ['Catalogue', 'CatalogueRecord', 'Dataset', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/language'} })
    license: str = Field(..., description="""\"The license of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'license',
         'domain_of': ['Catalogue', 'DataService', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/license'} })
    mediaType: Optional[str] = Field(None, description="""\"The media type of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'mediaType',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#mediaType'} })
    modificationDate: str = Field(..., description="""\"The modification date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'modificationDate',
         'domain_of': ['Catalogue',
                       'CatalogueRecord',
                       'Dataset',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/modified'} })
    packagingFormat: Optional[str] = Field(None, description="""\"The packaging format of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'packagingFormat',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#packagingFormat'} })
    releaseDate: str = Field(..., description="""\"The release date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'releaseDate',
         'domain_of': ['Catalogue', 'Dataset', 'DatasetSeries', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/issued'} })
    rights: str = Field(..., description="""\"The rights of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'rights',
         'domain_of': ['Catalogue', 'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/rights'} })
    spatialResolution: Optional[List[str]] = Field(None, description="""\"The spatial resolution of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'spatialResolution',
         'domain_of': ['Dataset', 'Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#spatialResolutionInMeters'} })
    status: Optional[str] = Field(None, description="""\"The status of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#status'} })
    temporalResolution: Optional[List[str]] = Field(None, description="""\"The temporal resolution of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'temporalResolution',
         'domain_of': ['Dataset', 'Distribution'],
         'slot_uri': 'http://www.w3.org/ns/dcat#temporalResolution'} })
    title: str = Field(..., description="""\"The title of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'title',
         'domain_of': ['Catalogue',
                       'ConceptScheme',
                       'DataService',
                       'Dataset',
                       'DatasetMemberOfDatasetSeries',
                       'DatasetSeries',
                       'Distribution'],
         'slot_uri': 'http://purl.org/dc/terms/title'} })


class Document(ConfiguredBaseModel):
    """
    \"A document.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://xmlns.com/foaf/0.1/Document',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://xmlns.com/foaf/0.1/Document'})

    pass


class Frequency(ConfiguredBaseModel):
    """
    \"The frequency of the resource.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://purl.org/dc/terms/accrualPeriodicity',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://purl.org/dc/terms/accrualPeriodicity'})

    pass


class Geometry(ConfiguredBaseModel):
    """
    \"A geometric shape.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.opengis.net/ont/geosparql#Geometry',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.opengis.net/ont/geosparql#Geometry'})

    pass


class Indentifier(ConfiguredBaseModel):
    """
    \"An identifier for the resource.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/adms#Identifier',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/adms#Identifier'})

    notation: Optional[str] = Field(None, description="""\"The notation of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'notation',
         'domain_of': ['Indentifier'],
         'slot_uri': 'http://www.w3.org/ns/dcat#notation'} })


class Kind(ConfiguredBaseModel):
    """
    \"A kind of resource.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/2006/vcard/ns#Kind',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/2006/vcard/ns#Kind'})

    pass


class LicenseDocument(ConfiguredBaseModel):
    """
    \"A license document.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#LicenseDocument',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#LicenseDocument'})

    type: Optional[List[str]] = Field(None, description="""\"The type of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'type',
         'domain_of': ['Dataset', 'LicenseDocument'],
         'slot_uri': 'http://www.w3.org/ns/dcat#type'} })


class LinguisticSystem(ConfiguredBaseModel):
    """
    \"A linguistic system.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://purl.org/dc/terms/LinguisticSystem',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://purl.org/dc/terms/LinguisticSystem'})

    pass


class Literal(ConfiguredBaseModel):
    """
    \"A literal value.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/2000/01/rdf-schema#Literal',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/2000/01/rdf-schema#Literal'})

    pass


class Location(ConfiguredBaseModel):
    """
    \"A location.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/locn#Location',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/locn#Location'})

    bbox: Optional[str] = Field(None, description="""\"The bounding box of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'bbox',
         'domain_of': ['Location'],
         'slot_uri': 'http://www.w3.org/ns/dcat#bbox'} })
    centroid: Optional[str] = Field(None, description="""\"The centroid of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'centroid',
         'domain_of': ['Location'],
         'slot_uri': 'http://www.w3.org/ns/dcat#centroid'} })
    geometry: Optional[str] = Field(None, description="""\"The geometry of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'geometry',
         'domain_of': ['Location'],
         'slot_uri': 'http://www.w3.org/ns/locn#geometry'} })


class MediaType(ConfiguredBaseModel):
    """
    \"A media type.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#MediaType',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#MediaType'})

    pass


class MediaTypeOrExtent(ConfiguredBaseModel):
    """
    \"A media type or extent.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#MediaTypeOrExtent',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#MediaTypeOrExtent'})

    pass


class PeriodOfTime(ConfiguredBaseModel):
    """
    \"A period of time.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://purl.org/dc/terms/PeriodOfTime',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://purl.org/dc/terms/PeriodOfTime'})

    beginning: Optional[str] = Field(None, description="""\"The beginning of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'beginning',
         'domain_of': ['PeriodOfTime'],
         'slot_uri': 'http://www.w3.org/2006/time#hasBeginning'} })
    end: Optional[str] = Field(None, description="""\"The end of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'end',
         'domain_of': ['PeriodOfTime'],
         'slot_uri': 'http://www.w3.orgb/2006/time#hasEnd'} })
    endDate: Optional[str] = Field(None, description="""\"The end date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'endDate',
         'domain_of': ['PeriodOfTime'],
         'slot_uri': 'http://www.w3.org/ns/dcat#endDate'} })
    startDate: Optional[str] = Field(None, description="""\"The start date of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'startDate',
         'domain_of': ['PeriodOfTime'],
         'slot_uri': 'http://www.w3.org/ns/dcat#startDate'} })


class Policy(ConfiguredBaseModel):
    """
    \"A policy.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#Policy',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#Policy'})

    pass


class ProvenanceStatement(ConfiguredBaseModel):
    """
    \"A statement of provenance.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/prov#ProvenanceStatement',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/prov#ProvenanceStatement'})

    pass


class Relationship(ConfiguredBaseModel):
    """
    \"A relationship between resources.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/prov#Relationship',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/prov#Relationship'})

    hasRole: Optional[List[str]] = Field(None, description="""\"The role of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'hasRole',
         'domain_of': ['Relationship'],
         'slot_uri': 'http://www.w3.org/ns/prov#hasRole'} })
    relation: Optional[List[str]] = Field(None, description="""\"The relation of the resource.\"""", json_schema_extra = { "linkml_meta": {'alias': 'relation',
         'domain_of': ['Relationship'],
         'slot_uri': 'http://www.w3.org/ns/prov#relation'} })


class Resource(ConfiguredBaseModel):
    """
    \"A resource.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#Resource',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#Resource'})

    pass


class RightsStatement(ConfiguredBaseModel):
    """
    \"A statement of rights.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#RightsStatement',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#RightsStatement'})

    pass


class Role(ConfiguredBaseModel):
    """
    \"A role.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/prov#Role',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/prov#Role'})

    pass


class Standard(ConfiguredBaseModel):
    """
    \"A standard.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/ns/dcat#Standard',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/ns/dcat#Standard'})

    pass


class TemporalLiteral(ConfiguredBaseModel):
    """
    \"A temporal literal.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/2006/time#TemporalLiteral',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/2006/time#TemporalLiteral'})

    pass


class TimeInstant(ConfiguredBaseModel):
    """
    \"A time instant.\"
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'http://www.w3.org/2006/time#TimeInstant',
         'from_schema': 'https://w3id.org/scidats/core_metadata_model',
         'source': 'http://www.w3.org/2006/time#TimeInstant'})

    pass


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Activity.model_rebuild()
Agent.model_rebuild()
Attribution.model_rebuild()
Catalogue.model_rebuild()
CatalogueRecord.model_rebuild()
CataloguedResource.model_rebuild()
Checksum.model_rebuild()
ChecksumAlgorithm.model_rebuild()
Concept.model_rebuild()
ConceptScheme.model_rebuild()
DataService.model_rebuild()
Dataset.model_rebuild()
DatasetMemberOfDatasetSeries.model_rebuild()
DatasetSeries.model_rebuild()
Distribution.model_rebuild()
Document.model_rebuild()
Frequency.model_rebuild()
Geometry.model_rebuild()
Indentifier.model_rebuild()
Kind.model_rebuild()
LicenseDocument.model_rebuild()
LinguisticSystem.model_rebuild()
Literal.model_rebuild()
Location.model_rebuild()
MediaType.model_rebuild()
MediaTypeOrExtent.model_rebuild()
PeriodOfTime.model_rebuild()
Policy.model_rebuild()
ProvenanceStatement.model_rebuild()
Relationship.model_rebuild()
Resource.model_rebuild()
RightsStatement.model_rebuild()
Role.model_rebuild()
Standard.model_rebuild()
TemporalLiteral.model_rebuild()
TimeInstant.model_rebuild()

