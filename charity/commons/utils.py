class DictObjectWrapper(object):
    def __init__(self, dict):
        self.dict = dict

    def __getattr__(self, name):
        return self.dict.get(name)