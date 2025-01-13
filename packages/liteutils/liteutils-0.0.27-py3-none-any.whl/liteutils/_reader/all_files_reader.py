from pathlib import Path
import pandas as pd
import configparser
import json
import yaml
import pickle
import numpy as np
from PIL import Image
import xml.etree.ElementTree as ET
import sqlite3
from abc import ABC, abstractmethod
from datasets import load_dataset, load_from_disk
import torch
import safetensors.torch
from huggingface_hub import hf_hub_download


class DataReader:
    """
    A unified interface for reading various file formats including AI/ML specific ones.
    Usage: data = DataReader.read('path/to/file')
    """

    def __init__(self):
        self._readers = {}
        self._register_default_readers()

    def _register_default_readers(self):
        """Register all supported file format readers."""
        # Previously supported formats
        self.register_reader(['.txt', '.log'], TextReader())
        self.register_reader(['.csv', '.tsv'], CSVReader())
        self.register_reader(['.json'], JSONReader())
        self.register_reader(['.yaml', '.yml'], YAMLReader())
        self.register_reader(['.ini', '.cfg'], INIReader())
        self.register_reader(['.xml'], XMLReader())
        self.register_reader(['.xlsx', '.xls'], ExcelReader())
        self.register_reader(['.png', '.jpg', '.jpeg', '.gif', '.bmp'], ImageReader())
        self.register_reader(['.npy', '.npz'], NumPyReader())
        self.register_reader(['.pkl', '.pickle'], PickleReader())
        self.register_reader(['.db', '.sqlite', '.sqlite3'], SQLiteReader())

        # New AI/ML formats
        self.register_reader(['.pt', '.pth'], PyTorchReader())
        self.register_reader(['.safetensors'], SafeTensorsReader())
        self.register_reader(['.jsonl'], JSONLinesReader())

    @classmethod
    def from_huggingface(cls, dataset_name, split="train", **kwargs):
        """Load a dataset directly from Hugging Face Hub."""
        return load_dataset(dataset_name, split=split, **kwargs)

    @classmethod
    def from_hub(cls, repo_id, filename, **kwargs):
        """Download and load a file from Hugging Face Hub."""
        filepath = hf_hub_download(repo_id=repo_id, filename=filename, **kwargs)
        return cls.read(filepath)


    def register_reader(self, extensions, reader):
        """Register a new reader for given file extensions."""
        for ext in extensions:
            self._readers[ext.lower()] = reader

    @classmethod
    def read(cls, filepath):
        """
        Read data from the given file path using appropriate reader.
        Returns the data in a format specific to the file type.
        """
        instance = cls()
        path = Path(filepath)
        extension = path.suffix.lower()

        if extension not in instance._readers:
            raise ValueError(f"Unsupported file format: {extension}")

        return instance._readers[extension].read(filepath)


class BaseReader(ABC):
    """Abstract base class for all readers."""

    @abstractmethod
    def read(self, filepath):
        """Read and return data from the file."""
        pass


class TextReader(BaseReader):
    def read(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()


class CSVReader(BaseReader):
    def read(self, filepath):
        return pd.read_csv(filepath)


class JSONReader(BaseReader):
    def read(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)


class YAMLReader(BaseReader):
    def read(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)


class INIReader(BaseReader):
    def read(self, filepath):
        config = configparser.ConfigParser()
        config.read(filepath)
        return {section: dict(config[section]) for section in config.sections()}


class ExcelReader(BaseReader):
    def read(self, filepath):
        return pd.read_excel(filepath)


class ImageReader(BaseReader):
    def read(self, filepath):
        return Image.open(filepath)


class NumPyReader(BaseReader):
    def read(self, filepath):
        try:
            return np.load(filepath)
        except:
            return np.load(filepath, allow_pickle=True)


class PickleReader(BaseReader):
    def read(self, filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)


class XMLReader(BaseReader):
    def read(self, filepath):
        tree = ET.parse(filepath)
        return tree.getroot()


class SQLiteReader(BaseReader):
    def read(self, filepath):
        conn = sqlite3.connect(filepath)
        cursor = conn.cursor()
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        # Read all tables into a dictionary
        data = {}
        for table in tables:
            table_name = table[0]
            data[table_name] = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return data


class PyTorchReader(BaseReader):
    def read(self, filepath):
        return torch.load(filepath)

class SafeTensorsReader(BaseReader):
    def read(self, filepath):
        return safetensors.torch.load_file(filepath)


class JSONLinesReader(BaseReader):
    def read(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f]

