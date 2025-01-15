"""_____________________________________________________________________

:PROJECT: SciDat

* SciDat MetaData module implementation *

:details:  MetaData module implementation of SciDat.

.. note:: -
.. todo:: - 
________________________________________________________________________
"""

# version
from scidats import __version__


from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from scidats.metadata_model_scidat_core import SciDatMetaDataCore
from rdflib.namespace import DC, FOAF, DCTERMS, XSD, Namespace, RDF, URIRef, RDFS, SKOS, OWL

class SciDatMetadata(BaseModel):
    """Main class, describing the JSON-LD based SciDat object
       The metadata is based on the [JSON-LD](https://json-ld.org/) standard
       and uses the Dublin Core Metadata Initiative (DCMI) terms - DCTERMS.
    """
    # ld_version : str = Field(default="1.0", alias="@version",  description="JSON-LD version of the SciDat object") 
    # version_scidat : str = Field(default="0.1", description="Version of the SciDat object")

    core : SciDatMetaDataCore = Field(description="Core metadata of the SciDat object", type="object")
    
    # TODO: check, if required
    class Config:
        validate_assignment = True