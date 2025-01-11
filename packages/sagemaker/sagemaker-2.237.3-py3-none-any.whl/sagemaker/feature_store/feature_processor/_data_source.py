# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""Contains classes to define input data sources."""
from __future__ import absolute_import

from typing import Optional, Dict, Union, TypeVar, Generic
from abc import ABC, abstractmethod
from pyspark.sql import DataFrame, SparkSession


import attr

T = TypeVar("T")


@attr.s
class BaseDataSource(Generic[T], ABC):
    """Abstract base class for feature processor data sources.

    Provides a skeleton for customization requiring the overriding of the method to read data from
    data source and return the specified type.
    """

    @abstractmethod
    def read_data(self, *args, **kwargs) -> T:
        """Read data from data source and return the specified type.

        Args:
            args: Arguments for reading the data.
            kwargs: Keyword argument for reading the data.
        Returns:
            T: The specified abstraction of data source.
        """

    @property
    @abstractmethod
    def data_source_unique_id(self) -> str:
        """The identifier for the customized feature processor data source.

        Returns:
            str: The data source unique id.
        """

    @property
    @abstractmethod
    def data_source_name(self) -> str:
        """The name for the customized feature processor data source.

        Returns:
            str: The data source name.
        """


@attr.s
class PySparkDataSource(BaseDataSource[DataFrame], ABC):
    """Abstract base class for feature processor data sources.

    Provides a skeleton for customization requiring the overriding of the method to read data from
    data source and return the Spark DataFrame.
    """

    @abstractmethod
    def read_data(
        self, spark: SparkSession, params: Optional[Dict[str, Union[str, Dict]]] = None
    ) -> DataFrame:
        """Read data from data source and convert the data to Spark DataFrame.

        Args:
            spark (SparkSession): The Spark session to read the data.
            params (Optional[Dict[str, Union[str, Dict]]]): Parameters provided to the
                feature_processor decorator.
        Returns:
            DataFrame: The Spark DataFrame as an abstraction on the data source.
        """


@attr.s
class FeatureGroupDataSource:
    """A Feature Group data source definition for a FeatureProcessor.

    Attributes:
        name (str): The name or ARN of the Feature Group.
        input_start_offset (Optional[str], optional): A duration specified as a string in the
            format '<no> <unit>' where 'no' is a number and 'unit' is a unit of time in ['hours',
            'days', 'weeks', 'months', 'years'] (plural and singular forms). Inputs contain data
            with event times no earlier than input_start_offset in the past. Offsets are relative
            to the function execution time. If the function is executed by a Schedule, then the
            offset is relative to the scheduled start time. Defaults to None.
        input_end_offset (Optional[str], optional): The 'end' (as opposed to start) counterpart for
            the 'input_start_offset'. Inputs will contain records with event times no later than
            'input_end_offset' in the past. Defaults to None.
    """

    name: str = attr.ib()
    input_start_offset: Optional[str] = attr.ib(default=None)
    input_end_offset: Optional[str] = attr.ib(default=None)


@attr.s
class CSVDataSource:
    """An CSV data source definition for a FeatureProcessor.

    Attributes:
        s3_uri (str): S3 URI of the data source.
        csv_header (bool): Whether to read the first line of the CSV file as column names. This
            option is only valid when file_format is set to csv. By default the value of this
            option is true, and all column types are assumed to be a string.
        infer_schema (bool): Whether to infer the schema of the CSV data source. This option is only
            valid when file_format is set to csv. If set to true, two passes of the data is required
            to load and infer the schema.
    """

    s3_uri: str = attr.ib()
    csv_header: bool = attr.ib(default=True)
    csv_infer_schema: bool = attr.ib(default=False)


@attr.s
class ParquetDataSource:
    """An parquet data source definition for a FeatureProcessor.

    Attributes:
        s3_uri (str): S3 URI of the data source.
    """

    s3_uri: str = attr.ib()


@attr.s
class IcebergTableDataSource:
    """An iceberg table data source definition for FeatureProcessor

    Attributes:
        warehouse_s3_uri (str): S3 URI of data warehouse. The value is usually
            the URI where data is stored.
        catalog (str): Name of the catalog.
        database (str): Name of the database.
        table (str): Name of the table.
    """

    warehouse_s3_uri: str = attr.ib()
    catalog: str = attr.ib()
    database: str = attr.ib()
    table: str = attr.ib()
