"""
Testing for serialize module.
"""

import json

from construe.metrics import dumps
from construe.metrics import Metric, Measurement


def test_serialize_string():
    measurement = Measurement(
        raw_metrics=[
            21.82307791099665,
            26.531772732839926,
            27.505767531015223,
            16.403111227499263,
            28.29817512637112,
            16.76156931690454,
            25.319997297409323,
        ],
        metric=Metric(
            label="Basic",
            sub_label="mul/sum",
            description="Basic benchmark for matrix operations",
            env="MediaTek Genio EVK 1200",
            device="TFLite APU",
        ),
        metadata={"testing": True},
    )

    out = dumps(measurement)
    assert len(out) > 20, "no data was output from the dump method"

    data = json.loads(out)
    assert "type" in data, "no type was in the data struct"
    assert data["type"] == Measurement.__name__, "incorrect type added to data"
