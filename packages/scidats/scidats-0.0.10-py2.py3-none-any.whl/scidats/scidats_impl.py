"""_____________________________________________________________________

:PROJECT: SciDatS

* SciDatS Main module implementation *

:details:  Main module implementation of SciDatS.
              This module contains the implementation of the SciDatS Interface with 
               convience methods for reading and writing.
                For metata storage, a SciDatS object is used.
                The metadata is based on the [JSON-LD](https://json-ld.org/) standard
                and uses the Dublin Core Metadata Initiative (DCMI) terms - DCTERMS.

.. note:: -
.. todo:: - 
________________________________________________________________________
"""

# version
from scidats import __version__

import logging
import json
from pyld import jsonld
import io
from datetime import datetime
from pydantic import BaseModel, Field
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import fastparquet as fp


from rdflib import Graph

from rdflib import DC, FOAF, DCTERMS, XSD, Literal, Graph, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF, DCTERMS, XSD, Namespace, RDF, URIRef, RDFS, SKOS, OWL

from scidats.scidats_interface import SciDatSInterface
from scidats.metadata_model_scidats_core import SciDatSMetaDataCore
from scidats.metadata_model_scidats_core_context import metadata_model_context as mm_core_context
from scidats.metadata_model_scidats_dcmi import DCMIMetaData
from scidats.metadata_model_scidats_dcmi_context import metadata_model_context as mm_dcmi_context
# from scidats.metadata_model_scidats_dcat_ap import DCATAPMetadata
# from scidats.metadata_model_scidats_dcmi_context import metadata_model_context as mm_dcmi_context

class SciDatS(SciDatSInterface):
    def __init__(self, 
                 dataframe : pd.DataFrame = None,
                 metadata_core : dict = None,
                 metadata_dataseries : json = None,
                 metadata_dcmi=None,
                 metadata_jsonld=None,
                 ):
        self.logger = logging.getLogger(__name__)
        self.logger.info("SciDatS object created")

        if metadata_dataseries is not None:

            # validate the metadata, if it is a valid JSON-LD
            self.metadata_dataseries = metadata_dataseries

        if dataframe is not None:
            self._dataframe = dataframe
        else:
            self._dataframe = None

        if metadata_core is not None:
            if isinstance(metadata_core, dict):
                self._metadata_core = SciDatSMetaDataCore( **metadata_core)
            elif isinstance(metadata_core, SciDatSMetaDataCore):
                self._metadata_core = metadata_core
        else:
            self._metadata_core = None

        if metadata_dcmi is not None:
            if isinstance(metadata_dcmi, dict):
                self._metadata_core = DCMIMetaData( **metadata_core)
            elif isinstance(metadata_dcmi, DCMIMetaData):
                self._metadata_dcmi = metadata_dcmi
        else:
            self._metadata_dcmi = None
        
        self._metadata_jsonld = metadata_jsonld
         
    # getter / setter for dataframe (in pandas with pyarrow backend and metadata added to the pyarrow table)
    @property
    def dataframe(self):
        """getter for dataframe """
        return self._dataframe
    
    @dataframe.setter
    def dataframe(self, dataframe: pd.DataFrame):
        """setter for dataframe """
        self._dataframe = dataframe

    # getter / setter for metadata (in JSON-LD)
    @property
    def metadata_dataseries(self) -> str:
        """getter for dataseries metadata, returns the metadata as JSON-LD """
        try:
            return json.loads(self._metadata_ds_jsonld)
        except Exception as err:
            self.logger.error(f"ERROR: {err} ")

    @metadata_dataseries.setter
    def metadata_dataseries(self, metadata_dataseries: json):
        """setter for dataseries metadata """
        # TODO: validate the metadata, if it is a valid JSON-LD
        try:
            self._metadata_ds_jsonld = metadata_dataseries # self.validate_JSONLD(metadata_dataseries)
        except Exception as err:
            self.logger.error(f"ERROR: {err} ")

    @property
    def metadata_core(self):
        """getter for metadata """
        return self._metadata_core
    
    @metadata_core.setter
    def metadata_core(self, metadata_core_dict : dict):
        """setter for SciDatS core metadata """
        self._metadata_core = SciDatSMetaDataCore( **metadata_core_dict)

    @property
    def metadata_dcmi(self):
        """getter for DCMI metadata """
        return self._metadata_dcmi
    
    @metadata_dcmi.setter
    def metadata_dcmi(self, metadata_dcmi_dict : dict):
        """setter for DCMI metadata """
        self._metadata_dcmi = DCMIMetaData( **metadata_dcmi_dict)

    @property
    def metadata_jsonld(self):
        """getter for metadata as JSON-LD """
        if self._metadata_core is None:
            return self._metadata_jsonld
        metadata_json_dict = json.loads(self._metadata_core.model_dump_json())
        merged_dict = {**mm_core_context, **metadata_json_dict}
        if self._metadata_dcmi is not None:
            metadata_dcmi_dict = json.loads(self._metadata_dcmi.model_dump_json())
            merged_dict = {**merged_dict, **metadata_dcmi_dict
            }
        return jsonld.compact(merged_dict,  mm_core_context)
    
    @metadata_jsonld.setter
    def metadata_jsonld(self, metadata_jsonld: str):
        """setter for metadata as JSON-LD """
        self._metadata_jsonld = metadata_jsonld

    @property
    def metadata_rdf(self, format="turtle"):
        g = Graph()

        g.parse(data=self.metadata_jsonld, format="json-ld")

        return g.serialize(format=format)
    
    def validate_JSONLD(self, jsonld: json) -> json:
        """validate a JSON-LD object

        :param jsonld: JSON-LD object
        :type jsonld: json
        :return: validated JSON-LD object
        :rtype: json
        """
        try:
            return jsonld.compact(jsonld, mm_core_context)
        except Exception as err:
            self.logger.error(f"ERROR: {err} ")
            return None

    def write_parquet(self, parquet_filename: str = None, 
                      metadata_core_key: str = "org.scidats.metadata.core",
                      metadata_dataseries_key: str = "org.scidats.metadata.dataseries",
                      base64encoding: bool = True) -> None:
        """writing a parqet file
            add metadata to a pandas dataframe 

        :param parquet_filename: filename of the parquet file
        :type parquet_filename: str
        """
        self.logger.info("writing parquet file")

        table = pa.Table.from_pandas(self._dataframe)

        try:
            new_meta_jsonld =  self.metadata_jsonld # self._metadata_jsonld if self._metadata_jsonld is not None else self.metadata_jsonld
            
            existing_meta = table.schema.metadata
            combined_meta = {
                metadata_core_key.encode() : json.dumps(new_meta_jsonld).encode(),
                #metadata_dataseries_key.encode() : self.metadata_dataseries.encode(),
                **existing_meta
            }
            table = table.replace_schema_metadata(combined_meta)
        except Exception as err:
            self.logger.error(f"ERROR (no metadata available): {err} ")

        if parquet_filename is None:
            output_stream = io.BytesIO()
            #df.to_parquet(output, index=False, engine='pyarrow')
            pq.write_table(table, where=output_stream, compression='GZIP')
            output_stream.seek(0)

            if base64encoding:
                import base64
                return base64.b64encode(output_stream.read()).decode("utf-8")
            else:
                return output_stream.read()

        elif parquet_filename.endswith(".parquet") or parquet_filename.endswith(".parq"):
            pq.write_table(table, parquet_filename, compression='GZIP')     
        

    def read_parquet(self, parquet_filename: str = None, input_stream: bytes = None,  metadata_key: str = "org.scidats.metadata.core", base64encoding=False) -> None:
        """reading a parqet file

        :param parquet_filename: filename of the parquet file
        :type parquet_filename: str
        """
        self.logger.info("reading parquet file")

        if parquet_filename is None and input_stream is not None:
            import io

            if base64encoding:
                import base64
                input_stream = base64.b64decode(input_stream)

            with io.BytesIO() as f:
                f.write(input_stream)
                f.seek(0)

                table = pa.parquet.read_table(f)
        
        elif parquet_filename.endswith(".parquet") or parquet_filename.endswith(".parq"):
            table = pa.parquet.read_table(parquet_filename)
        
        if self._dataframe is not None:
            raise Exception("Dataframe already set")
        self._dataframe = table.to_pandas()
        
        if self._metadata_core is not None:
            raise Exception("Metadata already set")
        restored_meta_json_raw = json.loads(table.schema.metadata[metadata_key.encode()])
        if restored_meta_json_raw is None:
            raise Exception("No metadata found in parquet file")
        self._metadata_jsonld = restored_meta_json_raw

        # restore metadata core
        # first extract a subset of the metadata jsonld, that corresponds to the core metadata

        metadata_core = {k: restored_meta_json_raw[k] for k in SciDatSMetaDataCore.model_fields.keys() if k in restored_meta_json_raw}

        self._metadata_core = SciDatSMetaDataCore( **metadata_core)
    
    


