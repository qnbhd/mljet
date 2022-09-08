class BasePreprocessor:
    def __init__(self, *args):
        self.transformers = [x for x in args]

    def transform(self, input_data):
        for preprocessor in self.transformers:
            input_data = preprocessor.transform(input_data)
        return input_data
