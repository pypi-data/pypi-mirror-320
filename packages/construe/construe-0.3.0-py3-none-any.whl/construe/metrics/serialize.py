"""
Handles serialization and deserialization of metrics.
"""

import json
import dataclasses

from functools import partial

from .metrics import Metric, Measurement


class MetricsJSONEncoder(json.JSONEncoder):

    def default(self, o):
        """
        Encode first looks to see if there is a dump method and uses that, otherwise
        it attempts to serialize a dataclass; and the last step is perform the default
        JSON serialization of primitive types.
        """

        if hasattr(o, "dump"):
            data = o.dump()
            data["type"] = o.__class__.__name__
            return data

        if dataclasses.is_dataclass(o):
            data = dataclasses.asdict(o)
            data["type"] = o.__class__.__name__
            return data

        return super(MetricsJSONEncoder, self).default(o)


class MetricsJSONDecoder(json.JSONDecoder):

    classmap = {
        Metric.__name__: Metric,
        Measurement.__name__: Measurement,
    }

    def __init__(self, *args, **kwargs):
        if not kwargs.get("object_hook", None) is None:
            kwargs["object_hook"] = self.object_hook
        super(MetricsJSONDecoder, self).__init__(*args, **kwargs)

    def object_hook(self, data):
        if "type" in data and data["type"] in self.classmap:
            cls = self.classmap[data.pop("type")]
            if hasattr(cls, "load"):
                return cls.load(data)
            return cls(**data)

        return data


# JSON Serialization
dump = partial(json.dump, cls=MetricsJSONEncoder)
dumps = partial(json.dumps, cls=MetricsJSONEncoder)
load = partial(json.load, cls=MetricsJSONDecoder)
loads = partial(json.loads, cls=MetricsJSONDecoder)
