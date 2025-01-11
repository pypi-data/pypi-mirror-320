import torch
from utils import text_to_sequence, sequence_to_text, save_audio

def infer(model, text):
    model.eval()
    with torch.no_grad():
        sequence = text_to_sequence(text)
        sequence = torch.tensor(sequence).unsqueeze(0)
        output = model(sequence)
        audio = output.squeeze().cpu().numpy()
        return audio

def text_to_sequence(text):
    """Convert text to a sequence of integers."""
    # Simple example: convert each character to its ASCII value
    return [ord(char) for char in text]

def sequence_to_text(sequence):
    """Convert a sequence of integers back to text."""
    # Simple example: convert each ASCII value back to its character
    return ''.join([chr(num) for num in sequence])

def save_inference(audio, file_path):
    """Save inference audio to file."""
    save_audio(audio, file_path)

def load_model(model, file_path):
    """Load model weights from file."""
    model.load_state_dict(torch.load(file_path))

def prepare_model(model_class, model_path):
    """Prepare the model by loading weights."""
    model = model_class()
    load_model(model, model_path)
    return model