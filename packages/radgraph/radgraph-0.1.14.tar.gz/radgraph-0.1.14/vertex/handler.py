import json
import torch
from ts.torch_handler.base_handler import BaseHandler
from radgraph import RadGraph  # import your RadGraph class


class RadGraphHandler(BaseHandler):
    def initialize(self, context):
        """TorchServe calls this once during model load."""
        properties = context.system_properties
        model_dir = properties.get("model_dir")
        # Load the model
        # For example, if you kept the same structure:
        self.model = RadGraph(
            model_type="radgraph-xl",
            model_cache_dir=model_dir,
            tokenizer_cache_dir=model_dir,
        )
        self.initialized = True

    def preprocess(self, data):
        """TorchServe calls this before predict(). 
           `data` will contain the request input.
        """
        # data is usually a list of records.
        # Example input: {"data": "some text"}
        # or if you specify "text" field in JSON
        text_inputs = []
        for row in data:
            # If content is in "data" field or "body", adjust accordingly:
            text_inputs.append(row.get("data") or row.get("body"))

        return text_inputs

    def inference(self, inputs):
        """TorchServe calls this to run the model forward."""
        # inputs is what you returned from preprocess
        with torch.no_grad():
            output = self.model(inputs)
        return output

    def postprocess(self, inference_output):
        """TorchServe calls this after predict()."""
        # Convert `inference_output` (a Python dict or list) into 
        # a JSON-serializable format
        return [inference_output]
