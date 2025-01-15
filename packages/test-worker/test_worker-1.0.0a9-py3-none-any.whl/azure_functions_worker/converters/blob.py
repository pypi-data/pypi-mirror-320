# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Any, Optional

from azure.functions import InputStream
from . import meta


class BlobConverter(meta.InConverter,
                    meta.OutConverter,
                    binding='blob',
                    trigger='blobTrigger'):
    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (InputStream, bytes, str))

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return (
            issubclass(pytype, (str, bytes, bytearray, InputStream))
            or callable(getattr(pytype, 'read', None))
        )

    @classmethod
    def encode(cls, obj: Any, *,
               expected_type: Optional[type]) -> meta.Datum:
        if callable(getattr(obj, 'read', None)):
            # file-like object
            obj = obj.read()

        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))

        else:
            raise NotImplementedError

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> Any:
        if data is None or data.type is None:
            return None

        data_type = data.type

        if data_type == 'string':
            data = data.value.encode('utf-8')
        elif data_type == 'bytes':
            data = data.value
        else:
            raise ValueError(
                f'unexpected type of data received for the "blob" binding '
                f': {data_type!r}'
            )

        if not trigger_metadata:
            return InputStream(data=data)
        else:
            properties = cls._decode_trigger_metadata_field(
                trigger_metadata, 'Properties', python_type=dict)
            if properties:
                blob_properties = properties
                length = properties.get('ContentLength') or \
                    properties.get('Length')
                length = int(length) if length else None
            else:
                blob_properties = None
                length = None

            metadata = None
            try:
                metadata = cls._decode_trigger_metadata_field(trigger_metadata,
                                                              'Metadata',
                                                              python_type=dict)
            except (KeyError, ValueError):
                # avoiding any exceptions when fetching Metadata as the
                # metadata type is unclear.
                pass

            return InputStream(
                data=data,
                name=cls._decode_trigger_metadata_field(
                    trigger_metadata, 'BlobTrigger', python_type=str),
                length=length,
                uri=cls._decode_trigger_metadata_field(
                    trigger_metadata, 'Uri', python_type=str),
                blob_properties=blob_properties,
                metadata=metadata
            )
