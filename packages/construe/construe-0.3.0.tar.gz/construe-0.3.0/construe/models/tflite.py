"""
Utilities for model loading and conversion.
"""

import tensorflow as tf


class TFLiteGenerateModel(tf.Module):
    """
    Defines a model whose serving function is the generation call.
    """

    def __init__(self, model):
        super(TFLiteGenerateModel, self).__init__()
        self.model = model

    @tf.function(
        # shouldn't need static batch size, but throws exception without it (needs to be fixed)
        input_signature=[
            tf.TensorSpec((1, 80, 3000), tf.float32, name="input_features"),
        ],
    )
    def serving(self, input_features):
        outputs = self.model.generate(
            input_features,
            max_new_tokens=255,
            return_dict_in_generate=True,
        )
        return {"sequences": outputs["sequences"]}
