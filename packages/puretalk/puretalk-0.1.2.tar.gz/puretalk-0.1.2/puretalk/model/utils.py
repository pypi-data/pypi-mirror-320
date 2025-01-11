import numpy as np
import librosa
import soundfile as sf

def text_to_sequence(text):
    """
    Convert text to a sequence of integers.
    Args:
        text (str): Input text.
    Returns:
        list: Sequence of integers.
    """
    # Example: Convert each character to its ASCII value
    return [ord(char) for char in text]

def sequence_to_text(sequence):
    """
    Convert a sequence of integers back to text.
    Args:
        sequence (list): Sequence of integers.
    Returns:
        str: Converted text.
    """
    # Example: Convert each ASCII value back to a character
    return ''.join(chr(num) for num in sequence)

def normalize_audio(audio):
    """
    Normalize audio signal.
    Args:
        audio (np.ndarray): Input audio signal.
    Returns:
        np.ndarray: Normalized audio signal.
    """
    return audio / np.max(np.abs(audio))

def denormalize_audio(audio):
    """
    Denormalize audio signal.
    Args:
        audio (np.ndarray): Input audio signal.
    Returns:
        np.ndarray: Denormalized audio signal.
    """
    return audio * np.max(np.abs(audio))

def save_audio(audio, file_path):
    """
    Save audio to file.
    Args:
        audio (np.ndarray): Audio signal.
        file_path (str): Path to save the audio file.
    """
    sf.write(file_path, audio, samplerate=22050)

def load_audio(file_path):
    """
    Load audio from file.
    Args:
        file_path (str): Path to the audio file.
    Returns:
        np.ndarray: Loaded audio signal.
    """
    audio, _ = librosa.load(file_path, sr=22050)
    return audio