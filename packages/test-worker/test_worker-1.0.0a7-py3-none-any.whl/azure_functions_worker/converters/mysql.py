# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections.abc
import json
import typing

from azure.functions import MySqlRow, MySqlRowList

from . import meta


class MySqlConverter(meta.InConverter, meta.OutConverter,
                     binding='mysql'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, MySqlRowList)

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (MySqlRowList, MySqlRow))

    @classmethod
    def decode(cls,
               data: meta.Datum,
               *,
               trigger_metadata) -> typing.Optional[MySqlRowList]:
        if data is None or data.type is None:
            return None

        data_type = data.type

        if data_type in ['string', 'json']:
            body = data.value

        elif data_type == 'bytes':
            body = data.value.decode('utf-8')

        else:
            raise NotImplementedError(
                f'Unsupported payload type: {data_type}')

        rows = json.loads(body)
        if not isinstance(rows, list):
            rows = [rows]

        return MySqlRowList(
            (None if row is None else MySqlRow.from_dict(row))
            for row in rows)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        if isinstance(obj, MySqlRow):
            data = MySqlRowList([obj])

        elif isinstance(obj, MySqlRowList):
            data = obj

        elif isinstance(obj, collections.abc.Iterable):
            data = MySqlRowList()

            for row in obj:
                if not isinstance(row, MySqlRow):
                    raise NotImplementedError(
                        f'Unsupported list type: {type(obj)}, \
                            lists must contain MySqlRow objects')
                else:
                    data.append(row)

        else:
            raise NotImplementedError(f'Unsupported type: {type(obj)}')

        return meta.Datum(
            type='json',
            value=json.dumps([dict(d) for d in data])
        )
