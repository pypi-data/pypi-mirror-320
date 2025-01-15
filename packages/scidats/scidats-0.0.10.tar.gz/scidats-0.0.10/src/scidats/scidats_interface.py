"""_____________________________________________________________________

:PROJECT: SciDatS

* Main module formal interface. *

:details: In larger projects, formal interfaces are helping to define a trustable contract.
          Currently there are two commonly used approaches: 
          [ABCMetadata](https://docs.python.org/3/library/abc.html) or [Python Protocols](https://peps.python.org/pep-0544/)

       see also:
       ABC metaclass
         - https://realpython.com/python-interface/
         - https://dev.to/meseta/factories-abstract-base-classes-and-python-s-new-protocols-structural-subtyping-20bm

.. note:: -
.. todo:: - 
________________________________________________________________________
"""

# here is a
from abc import ABCMeta, abstractmethod


class SciDatSInterface(metaclass=ABCMeta):
    """SciDatS formal Interface
    TODO: test, if ABC baseclass is wor
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "read_parquet")
            and callable(subclass.read_parquet)
            or (hasattr(subclass, "write_parquet") and callable(subclass.write_parquet))
            or NotImplemented
        )

    @abstractmethod
    def read_parquet(
        self,
        parquet_filename: str = None,
        input_stream: bytes = None,
        metadata_key: str = "scidats.org",
        base64encoding=False,
    ) -> None:
        """reading a parqet file

        :param parquet_filename: filename of the parquet file
        :type parquet_filename: str
        """

    @abstractmethod
    def write_parquet(
        self, parquet_filename: str = None, metadata_key: str = "scidats.org", base64encoding: bool = False
    ) -> None:
        """writing a parqet file

        :param parquet_filename: filename of the parquet file
        :type parquet_filename: str
        """

    # dataframe getter / setter (in pandas with pyarrow backend and metadata added to the pyarrow table)
    @property
    @abstractmethod
    def dataframe(self):
        """getter for dataframe"""
        pass

    @dataframe.setter
    @abstractmethod
    def dataframe(self, dataframe):
        """setter for dataframe"""
        pass

    # metadata getter / setter (in JSON-LD)

    @property
    @abstractmethod
    def metadata_core(self):
        """getter for metadata"""
        pass

    @metadata_core.setter
    @abstractmethod
    def metadata_core(self, metadata_core_dict: dict):
        """setter for metadata"""
        pass

    @property
    @abstractmethod
    def metadata_dcmi(self):
        """getter for DCMI metadata"""
        pass

    @metadata_core.setter
    @abstractmethod
    def metadata_dcmi(self, metadata_dcmi_dict: dict):
        """setter for DCMI metadata"""
        pass
