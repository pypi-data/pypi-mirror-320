# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import typing
import json

from typing import Any, List

from . import meta

from azure.functions import KafkaEvent


class KafkaConverter(meta.InConverter, meta.OutConverter, binding='kafka'):
    @classmethod
    def check_input_type_annotation(cls, pytype) -> bool:
        valid_types = (KafkaEvent)

        return (
            meta.is_iterable_type_annotation(pytype, valid_types)
            or (isinstance(pytype, type) and issubclass(pytype, valid_types))
        )

    @classmethod
    def check_output_type_annotation(cls, pytype) -> bool:
        valid_types = (str, bytes)
        return (
            meta.is_iterable_type_annotation(pytype, str)
            or (isinstance(pytype, type) and issubclass(pytype, valid_types))
        )

    @classmethod
    def decode(
        cls, data: meta.Datum, *, trigger_metadata
    ) -> typing.Union[KafkaEvent, typing.List[KafkaEvent]]:
        data_type = data.type

        if data_type in ['string', 'bytes', 'json']:
            return cls.decode_single_event(data, trigger_metadata)

        elif data_type in ['collection_bytes', 'collection_string']:
            return cls.decode_multiple_events(data, trigger_metadata)

        else:
            raise NotImplementedError(
                f'unsupported event data payload type: {data_type}')

    @classmethod
    def decode_single_event(cls, data: meta.Datum,
                            trigger_metadata) -> KafkaEvent:
        data_type = data.type

        if data_type in ['string', 'json']:
            body = data.value.encode('utf-8')

        elif data_type == 'bytes':
            body = data.value

        else:
            raise NotImplementedError(
                f'unsupported event data payload type: {data_type}')

        return KafkaEvent(body=body)

    @classmethod
    def decode_multiple_events(cls, data: meta.Datum,
                               trigger_metadata) -> typing.List[KafkaEvent]:
        parsed_data: List[bytes] = []

        if data.type == 'collection_bytes':
            parsed_data = data.value.bytes

        elif data.type == 'collection_string':
            parsed_data = [
                d.encode('utf-8') for d in data.value.string
            ]

        return [KafkaEvent(body=pd) for pd in parsed_data]

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        raise NotImplementedError('Output bindings are not '
                                  'supported for Kafka')


class KafkaTriggerConverter(KafkaConverter,
                            binding='kafkaTrigger', trigger=True):

    @classmethod
    def decode(
        cls, data: meta.Datum, *, trigger_metadata
    ) -> typing.Union[KafkaEvent, typing.List[KafkaEvent]]:
        data_type = data.type

        if data_type in ['string', 'bytes', 'json']:
            return cls.decode_single_event(data, trigger_metadata)
        elif data_type in ['collection_bytes', 'collection_string']:
            return cls.decode_multiple_events(data, trigger_metadata)
        else:
            raise NotImplementedError(
                f'unsupported event data payload type: {data_type}')

    @classmethod
    def decode_single_event(cls, data: meta.Datum,
                            trigger_metadata) -> KafkaEvent:
        data_type = data.type

        if data_type in ['string', 'json']:
            body = data.value.encode('utf-8')

        elif data_type == 'bytes':
            body = data.value

        else:
            raise NotImplementedError(
                f'unsupported event data payload type: {data_type}')

        return KafkaEvent(
            body=body,
            timestamp=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Timestamp', python_type=str),
            key=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Key', python_type=str),
            partition=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Partition', python_type=int),
            offset=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Offset', python_type=int),
            topic=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Topic', python_type=str),
            headers=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Headers', python_type=list),
            trigger_metadata=trigger_metadata
        )

    @classmethod
    def decode_multiple_events(cls, data: meta.Datum,
                               trigger_metadata) -> typing.List[KafkaEvent]:
        parsed_data: List[bytes] = []

        if data.type == 'collection_bytes':
            parsed_data = data.value.bytes

        elif data.type == 'collection_string':
            parsed_data = [
                d.encode('utf-8') for d in data.value.string
            ]

        timestamp_props = trigger_metadata.get('TimestampArray')
        key_props = trigger_metadata.get('KeyArray')
        partition_props = trigger_metadata.get('PartitionArray')
        offset_props = trigger_metadata.get('OffsetArray')
        topic_props = trigger_metadata.get('TopicArray')
        header_props = trigger_metadata.get('HeadersArray')

        parsed_timestamp_props: List[Any] = cls.get_parsed_props(
            timestamp_props, parsed_data)

        parsed_key_props = cls.get_parsed_props(
            key_props, parsed_data)

        parsed_partition_props = cls.get_parsed_props(
            partition_props, parsed_data)

        parsed_offset_props: List[Any] = []
        if offset_props is not None:
            parsed_offset_props = [v for v in offset_props.value.sint64]
            if len(parsed_offset_props) != len(parsed_data):
                raise AssertionError(
                    'Number of bodies and metadata mismatched')

        parsed_topic_props: List[Any]
        if topic_props is not None:
            parsed_topic_props = [v for v in topic_props.value.string]

        parsed_headers_props: List[Any]
        if header_props is not None:
            parsed_headers_list = cls.get_parsed_props(header_props,
                                                       parsed_data)
            parsed_headers_props = [v for v in parsed_headers_list]

        events = []

        for i in range(len(parsed_data)):
            event = KafkaEvent(
                body=parsed_data[i],
                timestamp=parsed_timestamp_props[i],
                key=parsed_key_props[i],
                partition=parsed_partition_props[i],
                offset=parsed_offset_props[i],
                topic=parsed_topic_props[i],
                headers=parsed_headers_props[i],
                trigger_metadata=trigger_metadata
            )
            events.append(event)

        return events

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        raise NotImplementedError('Output bindings are not '
                                  'supported for Kafka')

    @classmethod
    def get_parsed_props(
            cls, props: meta.Datum, parsed_data) -> List[Any]:
        parsed_props: List[Any] = []
        if props is not None:
            parsed_props = json.loads(props.value)
        if len(parsed_data) != len(parsed_props):
            raise AssertionError('Number of bodies and metadata mismatched')
        return parsed_props
