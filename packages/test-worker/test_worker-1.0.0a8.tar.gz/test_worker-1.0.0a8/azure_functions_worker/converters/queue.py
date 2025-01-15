# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections.abc
import datetime
import json
from typing import List, Dict, Any, Union, Optional

from azure.functions import QueueMessage

from . import meta


class QueueMessageInConverter(meta.InConverter,
                              binding='queueTrigger', trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, QueueMessage)

    @classmethod
    def decode(cls, data: meta.Datum, *,
               trigger_metadata) -> Any:
        data_type = data.type

        if data_type in ['string', 'bytes']:
            body = data.value

        else:
            raise NotImplementedError(
                f'unsupported queue payload type: {data_type}')

        if trigger_metadata is None:
            raise NotImplementedError(
                'missing trigger metadata for queue input')

        return QueueMessage(
            id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Id', python_type=str),
            body=body,
            dequeue_count=cls._decode_trigger_metadata_field(
                trigger_metadata, 'DequeueCount', python_type=int),
            expiration_time=cls._parse_datetime_metadata(
                trigger_metadata, 'ExpirationTime'),
            insertion_time=cls._parse_datetime_metadata(
                trigger_metadata, 'InsertionTime'),
            time_next_visible=cls._parse_datetime_metadata(
                trigger_metadata, 'NextVisibleTime'),
            pop_receipt=cls._decode_trigger_metadata_field(
                trigger_metadata, 'PopReceipt', python_type=str)
        )


class QueueMessageOutConverter(meta.OutConverter, binding='queue'):

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        valid_types = (QueueMessage, str, bytes)
        return (
            meta.is_iterable_type_annotation(pytype, valid_types)
            or (isinstance(pytype, type) and issubclass(pytype, valid_types))
        )

    @classmethod
    def encode(cls, obj: Any, *,
               expected_type: Optional[type]) -> meta.Datum:
        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, bytes):
            return meta.Datum(type='bytes', value=obj)

        elif isinstance(obj, QueueMessage):
            return meta.Datum(
                type='json',
                value=json.dumps({
                    'id': obj.id,
                    'body': obj.get_body().decode('utf-8'),
                })
            )

        elif isinstance(obj, collections.abc.Iterable):
            msgs: List[Union[str, Dict]] = []
            for item in obj:
                if isinstance(item, str):
                    msgs.append(item)
                elif isinstance(item, QueueMessage):
                    msgs.append({
                        'id': item.id,
                        'body': item.get_body().decode('utf-8')
                    })
                else:
                    raise NotImplementedError(
                        'invalid data type in output '
                        'queue message list: {}'.format(type(item)))

            return meta.Datum(
                type='json',
                value=json.dumps(msgs)
            )

        raise NotImplementedError

    @classmethod
    def _format_datetime(cls, dt: Optional[datetime.datetime]):
        if dt is None:
            return None
        else:
            return dt.isoformat()
