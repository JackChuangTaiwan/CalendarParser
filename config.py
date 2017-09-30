from __future__ import absolute_import
import json

__all__ = []

DEFAULT_CONFIG_PATH = r'converter_config.json'

class ConfigBase(object):
    def __init__(self, **kwargs):
        dv = kwargs.pop('default_values')
        self.header = self._get_header(dv)
        self.default_values = self._get_default_values(dv)
        self.misc = kwargs

    def load(self, fpath):
        with open(fpath, 'r') as ifile:
            self.__dict__ = json.load(ifile)

    def _get_header(self, dv):
        if dv is not None:
            return [val.keys()[0] for val in dv]

    def _get_default_values(self, dv):
        if dv is not None:
            return {k: val[k] for val in dv for k in val}


class CalendarConfig(ConfigBase):
    def __init__(self, **kwargs):
        super(CalendarConfig, self).__init__(**kwargs)
        self.km = self.misc.pop('key_map')
        self.ko = None
        self.ho = None      # header order

    def set_header_order(self, col_src):
        self.ho = {v: i for i, v in enumerate(col_src)}


class CsvWriterConfig(ConfigBase):
    def __init__(self, **kwargs):
        super(CsvWriterConfig, self).__init__(**kwargs)
        self.km = self.misc.pop('key_map')
        self.km_content = self.misc.pop('key_map_content')
        self.ko = None
        self.ho = None

    def set_header_order(self, col_src):
        self.ho = {v: i for i, v in enumerate(col_src)}


class ConverterConfig(object):
    __single = None
    __initialized = False

    def __new__(clz):
        if ConverterConfig.__single is None:
            ConverterConfig.__single = object.__new__(clz)
        return ConverterConfig.__single

    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        if ConverterConfig.__initialized: return
        ConverterConfig.__initialized = True
        self.CalendarConfig = None
        self.CsvWriterConfig = None
        if config_path is not None:
            self.load(config_path)

    def load(self, fpath):
        with open(fpath, 'r') as ifile:
            parsed = json.load(ifile)
            self.CalendarConfig = CalendarConfig(**parsed['calendar'])
            self.CsvWriterConfig = CsvWriterConfig(**parsed['writer'])

