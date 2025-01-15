# SciDatS

SciDatS is a python package for storing and retrieving scientific data stored in JSON-LD (semantically annotated JSON - Linked Data).

This *Scientific Data Standard*  is designed as a data exchange standard to enable exchange/synchronisation of Scientific Data, maintaining all metadata between 
different laboratories.


This project is very much inspired by Stuart Chalk's [SciDatSa](https://github.com/stuchalk/scidata/tree/main) and 
the tools of his lab [https://github.com/chalklab](https://github.com/chalklab).


## Features

Compared to SciDatSa it is aiming at

* a wide community support, independent of a certain lab 
* a simpler JSON-LD structure
* convenient functions for retrieving data and metadata
* improved tooling based on pydantic and rdflib
* **reading and writing** for *SciDatS* files
* coupling to the [LabDataReader framework](https://gitlab/opensourcelab/ScientificData/LabDataReader) - for transforming proppriatory lab data into a semantically annotated SciDatSa format.

## Design criteria


Here are some of the criteria the data / metadata standard has to fulfil (and in brackets the selected technology) :


- data and metadata storage for scientific / machine learning needs (semantic annotation, based on ontologies, derivatives of owlready2)

  - proper nullable data / missing data handling (pyarrow / parquet)

  - data modalities, like range / limits, type / continuos / categorial / variable treatment in case of range violation (parquet metadta)

  - cardinality (parquet metadata)

- efficient storage (parquet)

- metadata and data stored at one place (parquet)

- metadata conservation when saving / loading / processing (parquet -> arrow)

- fast data exchange (arrow flight, MinIO active replication)

- fast loading (fastparquet, pyarrow)

- fast data processing without in-memory re-writing after loading ( pandas with pyarrow backend, arrow flight, polars)

- "modalities" for the machine learning models

- semantic annotations / metadata in RDF compliant format - for creating instances of ontology classes and SPARQL reasoning (JSON-LD, rdflib, owlready2)

- fast data processing (direct loading into pyarrow driven dataframe )

- programming language agnostic / independent (parquet)

- easy to use (SciDatS / labDataReader framework, currently in implementation by me)

- commonly used in ETL pipelines (Apache Spark, prefect, ... )

- suitable for S3 file storage systems (MinIO)


## Installation

    pip install scidats --index-url https://gitlab.com/api/v4/projects/<gitlab-project-id>/packages/pypi/simple

## Usage

    scidats --help 

## Development

    git clone gitlab.com/opensourcelab/scidats

    # create a virtual environment and activate it then run

    pip install -e .[dev]

    # run unittests

    invoke test   # use the invoke environment to manage development
    

## Documentation

The Documentation can be found here: [https://opensourcelab.gitlab.io/scidats](https://opensourcelab.gitlab.io/scidats) or [scidats.gitlab.io](scidats.gitlab.io/)


## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter)
 and the [gitlab.com/opensourcelab/software-dev/cookiecutter-pypackage](https://gitlab.com/opensourcelab/software-dev/cookiecutter-pypackage) project template.



