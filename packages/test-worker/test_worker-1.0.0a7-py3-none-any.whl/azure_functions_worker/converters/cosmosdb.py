# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections.abc
import json
import typing

from azure.functions import Document, DocumentList

from . import meta


class CosmosDBConverter(meta.InConverter, meta.OutConverter,
                        binding='cosmosDB'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, DocumentList)

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (DocumentList, Document))

    @classmethod
    def decode(cls,
               data: meta.Datum,
               *,
               trigger_metadata) -> typing.Optional[DocumentList]:
        if data is None or data.type is None:
            return None

        data_type = data.type

        if data_type in ['string', 'json']:
            body = data.value

        elif data_type == 'bytes':
            body = data.value.decode('utf-8')

        else:
            raise NotImplementedError(
                f'unsupported queue payload type: {data_type}')

        documents = json.loads(body)
        if not isinstance(documents, list):
            documents = [documents]

        return DocumentList(
            (None if doc is None else Document.from_dict(doc))
            for doc in documents)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        if isinstance(obj, Document):
            data = DocumentList([obj])

        elif isinstance(obj, DocumentList):
            data = obj

        elif isinstance(obj, collections.abc.Iterable):
            data = DocumentList()

            for doc in obj:
                if not isinstance(doc, Document):
                    raise NotImplementedError
                else:
                    data.append(doc)

        else:
            raise NotImplementedError

        return meta.Datum(
            type='json',
            value=json.dumps([dict(d) for d in data])
        )


class CosmosDBTriggerConverter(CosmosDBConverter,
                               binding='cosmosDBTrigger', trigger=True):
    pass
