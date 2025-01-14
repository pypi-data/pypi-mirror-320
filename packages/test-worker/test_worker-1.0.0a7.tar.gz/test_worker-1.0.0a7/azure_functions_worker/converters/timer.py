# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import typing

from azure.functions import _timer as timer
from . import meta


class TimerRequestConverter(meta.InConverter,
                            binding='timerTrigger', trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, timer.TimerRequest)

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> typing.Any:
        if data.type != 'json':
            raise NotImplementedError

        info = json.loads(data.value)

        return timer.TimerRequest(
            past_due=info.get('IsPastDue', False),
            schedule_status=info.get('ScheduleStatus', {}),
            schedule=info.get('Schedule', {}))
