# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime
import json
from typing import Dict, Any, List, Union, Optional, Mapping, cast

from azure.functions import ServiceBusMessage

from . import meta


class ServiceBusMessageInConverter(meta.InConverter,
                                   binding='serviceBusTrigger', trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        valid_types = (ServiceBusMessage)
        return (
            meta.is_iterable_type_annotation(pytype, valid_types)
            or (isinstance(pytype, type) and issubclass(pytype, valid_types))
        )

    @classmethod
    def decode(
        cls, data: meta.Datum, *, trigger_metadata: Mapping[str, meta.Datum]
    ) -> Union[ServiceBusMessage, List[ServiceBusMessage]]:
        """Returns the application setting from environment variable.

        Parameters
        ----------
        data: meta.Datum
            The datum from GRPC message

        trigger_metadata: Mapping[str, meta.Datum]
            The metadata of the Service Bus trigger, usually populated by
            function host

        Returns
        -------
        Union[ServiceBusMessage, List[ServiceBusMessage]]
            When 'cardinality' is set to 'one', this method returns a single
            ServiceBusMessage. When 'cardinality' is set to 'many' this method
            returns a list of ServiceBusMessage.
        """
        if cls._is_cardinality_one(trigger_metadata):
            return cls.decode_single_message(
                data, trigger_metadata=trigger_metadata)
        elif cls._is_cardinality_many(trigger_metadata):
            return cls.decode_multiple_messages(
                data, trigger_metadata=trigger_metadata)
        else:
            raise NotImplementedError(
                f'unsupported service bus data type: {data.type} or '
                'UserProperties does not exist')

    @classmethod
    def decode_single_message(
        cls, data: meta.Datum, *,
        trigger_metadata: Mapping[str, meta.Datum]
    ) -> ServiceBusMessage:
        if data is None:
            # ServiceBus message with no payload are possible.
            # See Azure/azure-functions-python-worker#330
            body = b''

        elif data.type in ['string', 'json']:
            body = data.value.encode('utf-8')

        elif data.type == 'bytes':
            body = data.value

        else:
            raise NotImplementedError(
                f'unsupported queue payload type: {data.type}')

        if trigger_metadata is None:
            raise NotImplementedError(
                'missing trigger metadata for ServiceBus message input')

        return ServiceBusMessage(
            body=body,
            trigger_metadata=trigger_metadata,
            application_properties=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ApplicationProperties', python_type=dict),
            content_type=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ContentType', python_type=str),
            correlation_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'CorrelationId', python_type=str),
            dead_letter_error_description=cls._decode_trigger_metadata_field(
                trigger_metadata, 'DeadLetterErrorDescription',
                python_type=str),
            dead_letter_reason=cls._decode_trigger_metadata_field(
                trigger_metadata, 'DeadLetterReason', python_type=str),
            dead_letter_source=cls._decode_trigger_metadata_field(
                trigger_metadata, 'DeadLetterSource', python_type=str),
            delivery_count=cls._decode_trigger_metadata_field(
                trigger_metadata, 'DeliveryCount', python_type=int),
            enqueued_sequence_number=cls._decode_trigger_metadata_field(
                trigger_metadata, 'EnqueuedSequenceNumber', python_type=int),
            enqueued_time_utc=cls._parse_datetime_metadata(
                trigger_metadata, 'EnqueuedTimeUtc'),
            expires_at_utc=cls._parse_datetime_metadata(
                trigger_metadata, 'ExpiresAtUtc'),
            label=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Label', python_type=str),
            locked_until=cls._parse_datetime_metadata(
                trigger_metadata, 'LockedUntil'),
            lock_token=cls._decode_trigger_metadata_field(
                trigger_metadata, 'LockToken', python_type=str),
            message_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'MessageId', python_type=str),
            partition_key=cls._decode_trigger_metadata_field(
                trigger_metadata, 'PartitionKey', python_type=str),
            reply_to=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ReplyTo', python_type=str),
            reply_to_session_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ReplyToSessionId', python_type=str),
            scheduled_enqueue_time_utc=cls._parse_datetime_metadata(
                trigger_metadata, 'ScheduledEnqueueTimeUtc'),
            sequence_number=cls._decode_trigger_metadata_field(
                trigger_metadata, 'SequenceNumber', python_type=int),
            session_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'SessionId', python_type=str),
            state=cls._decode_trigger_metadata_field(
                trigger_metadata, 'State', python_type=int),
            subject=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Subject', python_type=str),
            time_to_live=cls._parse_timedelta_metadata(
                trigger_metadata, 'TimeToLive'),
            to=cls._decode_trigger_metadata_field(
                trigger_metadata, 'To', python_type=str),
            transaction_partition_key=cls._decode_trigger_metadata_field(
                trigger_metadata, 'TransactionPartitionKey', python_type=str),
            user_properties=cls._decode_trigger_metadata_field(
                trigger_metadata, 'UserProperties', python_type=dict),
        )

    @classmethod
    def decode_multiple_messages(
        cls, data: meta.Datum, *,
        trigger_metadata: Mapping[str, meta.Datum]
    ) -> List[ServiceBusMessage]:
        """Unlike EventHub, the trigger_metadata already contains a set of
        arrays (e.g. 'ContentTypeArray', 'CorrelationidArray'...). We can
        retrieve message properties directly from those array.
        """
        if data.type == 'collection_bytes':
            parsed_data = data.value.bytes

        elif data.type == 'collection_string':
            parsed_data = data.value.string

        # Input Trigger IotHub Event
        elif data.type == 'json':
            parsed_data = json.loads(data.value)

        else:
            raise NotImplementedError('unable to decode multiple messages '
                                      f'with data type {data.type}')

        return cls._extract_messages(parsed_data, data.type, trigger_metadata)

    @classmethod
    def _is_cardinality_many(
        cls,
        trigger_metadata: Mapping[str, meta.Datum]
    ) -> bool:
        return 'UserPropertiesArray' in trigger_metadata

    @classmethod
    def _is_cardinality_one(
        cls,
        trigger_metadata: Mapping[str, meta.Datum]
    ) -> bool:
        return 'UserProperties' in trigger_metadata

    @classmethod
    def _get_event_count(
        cls,
        trigger_metadata: Mapping[str, meta.Datum]
    ) -> int:
        datum = trigger_metadata['UserPropertiesArray']
        user_props = json.loads(datum.value)
        return len(user_props)

    @classmethod
    def _marshall_message_body(
        cls,
        body: Union[bytes, str, Dict[str, Any]],
        data_type: str
    ) -> bytes:
        if data_type == 'bytes' and isinstance(body, bytes):
            return body
        elif data_type == 'str' and isinstance(body, str):
            return body.encode('utf-8')
        elif data_type == 'json' and isinstance(body, dict):
            return json.dumps(body).encode('utf-8')
        else:
            raise NotImplementedError('unable to marshall message body with '
                                      f'data_type {data_type}')

    @classmethod
    def _marshall_message_bodies(
        cls,
        bodies: Union[List[str], List[bytes]],
        data_type: str
    ) -> List[bytes]:
        # The typing library cast() method is used as mypy type helper
        # Currently, mypy does not provide List[type] checking for now
        # Thus, forcefully casting is required
        if data_type == 'collection_bytes':
            return cast(List[bytes], bodies)
        elif data_type == 'collection_string':
            strings: List[str] = cast(List[str], bodies)
            return cast(List[bytes], [b.encode('utf-8') for b in strings])
        elif data_type == 'json':
            return cast(List[bytes],
                        [json.dumps(b).encode('utf-8') for b in bodies])
        else:
            raise NotImplementedError('unable to marshall message bodies with '
                                      f'data_type {data_type}')

    @classmethod
    def _extract_messages(
        cls, parsed_data: Union[List[bytes], List[str]], data_type: str,
        trigger_metadata: Mapping[str, meta.Datum]
    ) -> List[ServiceBusMessage]:
        messages: List[ServiceBusMessage] = []
        num_messages: int = cls._get_event_count(trigger_metadata)
        message_bodies: List[bytes] = cls._marshall_message_bodies(
            bodies=parsed_data, data_type=data_type
        )
        for i in range(num_messages):
            messages.append(ServiceBusMessage(
                body=message_bodies[i],
                trigger_metadata=trigger_metadata,
                application_properties=cls._get_from_metadata_array(
                    trigger_metadata, 'ApplicationPropertiesArray', i),
                content_type=cls._get_from_metadata_array(
                    trigger_metadata, 'ContentTypeArray', i),
                correlation_id=cls._get_from_metadata_array(
                    trigger_metadata, 'CorrelationIdArray', i),
                dead_letter_error_description=cls._get_from_metadata_array(
                    trigger_metadata, 'DeadLetterErrorDescriptionArray', i),
                dead_letter_reason=cls._get_from_metadata_array(
                    trigger_metadata, 'DeadLetterReasonArray', i),
                dead_letter_source=cls._get_from_metadata_array(
                    trigger_metadata, 'DeadLetterSourceArray', i),
                delivery_count=cls._get_from_metadata_array(
                    trigger_metadata, 'DeliveryCountArray', i),
                enqueued_sequence_number=cls._get_from_metadata_array(
                    trigger_metadata, 'EnqueuedSequenceNumberArray', i),
                enqueued_time_utc=cls._parse_datetime(
                    cls._get_from_metadata_array(
                        trigger_metadata, 'EnqueuedTimeUtcArray', i)),
                expires_at_utc=cls._parse_datetime(
                    cls._get_from_metadata_array(
                        trigger_metadata, 'ExpiresAtUtcArray', i)),
                label=cls._get_from_metadata_array(
                    trigger_metadata, 'LabelArray', i),
                locked_until=cls._parse_datetime(cls._get_from_metadata_array(
                    trigger_metadata, 'LockedUntilArray', i)),
                lock_token=cls._get_from_metadata_array(
                    trigger_metadata, 'LockTokenArray', i),
                message_id=cls._get_from_metadata_array(
                    trigger_metadata, 'MessageIdArray', i),
                partition_key=cls._get_from_metadata_array(
                    trigger_metadata, 'PartitionKeyArray', i),
                reply_to_session_id=cls._get_from_metadata_array(
                    trigger_metadata, 'ReplyToSessionIdArray', i),
                scheduled_enqueue_time_utc=cls._parse_datetime(
                    cls._get_from_metadata_array(
                        trigger_metadata, 'ScheduledEnqueueTimeUtcArray', i)),
                sequence_number=cls._get_from_metadata_array(
                    trigger_metadata, 'SequenceNumberArray', i),
                session_id=cls._get_from_metadata_array(
                    trigger_metadata, 'SessionIdArray', i),
                state=cls._get_from_metadata_array(
                    trigger_metadata, 'StateArray', i),
                subject=cls._get_from_metadata_array(
                    trigger_metadata, 'SubjectArray', i),
                time_to_live=cls._parse_timedelta(
                    cls._get_from_metadata_array(
                        trigger_metadata, 'TimeToLiveArray', i)),
                to=cls._get_from_metadata_array(
                    trigger_metadata, 'ToArray', i),
                transaction_partition_key=cls._get_from_metadata_array(
                    trigger_metadata, 'TransactionPartitionKeyArray', i),
                reply_to=cls._get_from_metadata_array(
                    trigger_metadata, 'ReplyToArray', i),
                user_properties=cls._get_from_metadata_array(
                    trigger_metadata, 'UserPropertiesArray', i)
            ))
        return messages

    @classmethod
    def _get_from_metadata_array(
        cls,
        trigger_metadata: Mapping[str, meta.Datum],
        array_name: str,
        index: int
    ) -> Any:
        """This method is to safe-guard when retrieve data from arrays.

        Some array may be missing in metadata. Others may not contain certain
        values (e.g. correlation_ids array may be empty [] when there's
        multiple messages).

        Parameters
        ----------
        trigger_metadata: Mapping[str, meta.Datum]
            The trigger metadata that contains multiple ServiceBus messages
        array_name: str
            The name of the array needs to be extracted
        index: int
            The element index wants to be extracted

        Returns
        -------
        Optional[Any]
            If the array name does not exist in trigger_metadata, returns None.
            If the array does not contains certain element, or index out of
            bound, returns None.
            Otherwise, return the element.
        """

        # Check if array name does exist (e.g. ContentTypeArray)
        datum: Optional[meta.Datum] = trigger_metadata.get(array_name)
        if datum is None:
            return None

        # Check if datum is an iterable element (e.g. collection_string)
        data_array: Optional[Union[List[str], List[int], List[bytes]]] = None
        if datum.type == 'collection_string':
            data_array = datum.value.string
        elif datum.type == 'collection_bytes':
            data_array = datum.value.bytes
        elif datum.type == 'collection_sint64':
            data_array = datum.value.sint64
        elif datum.type == 'json':
            data_array = json.loads(datum.value)

        # Check if the index is inbound
        if data_array is None or index >= len(data_array):
            return None

        return data_array[index]


class ServiceBusMessageOutConverter(meta.OutConverter, binding='serviceBus'):

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, bytes))

    @classmethod
    def encode(cls, obj: Any, *,
               expected_type: Optional[type]) -> meta.Datum:
        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, bytes):
            return meta.Datum(type='bytes', value=obj)

        raise NotImplementedError
