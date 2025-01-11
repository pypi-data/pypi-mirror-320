import torch
from torch.utils.data import Dataset, DataLoader
import json

class TTSDataset(Dataset):
    def __init__(self, texts, targets):
        self.texts = texts
        self.targets = targets

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.texts[idx], self.targets[idx]

def collate_fn(batch):
    texts, targets = zip(*batch)
    return torch.tensor(texts), torch.tensor(targets)

def get_dataloader(texts, targets, batch_size=32, shuffle=True):
    dataset = TTSDataset(texts, targets)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=collate_fn)

def load_data(file_path):
    """
    Load data from a JSON file.
    Args:
        file_path (str): Path to the JSON file containing the data.
    Returns:
        list: List of texts.
        list: List of targets.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    texts = [item['text'] for item in data]
    targets = [item['target'] for item in data]
    return texts, targets

def preprocess_text(text):
    """
    Preprocess the input text.
    Args:
        text (str): Input text.
    Returns:
        str: Preprocessed text.
    """
    # Example preprocessing: lowercasing and removing punctuation
    text = text.lower()
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    return text

def preprocess_target(target):
    """
    Preprocess the target data.
    Args:
        target (str): Target data.
    Returns:
        str: Preprocessed target.
    """
    # Example preprocessing: lowercasing and removing punctuation
    target = target.lower()
    target = ''.join(char for char in target if char.isalnum() or char.isspace())
    return target