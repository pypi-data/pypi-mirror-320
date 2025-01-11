#import puretalk-tts.config
class Config:
    def __init__(self):
        self.input_dim = 256
        self.hidden_dim = 512
        self.output_dim = 80
        self.num_layers = 3
        self.batch_size = 32
        self.num_epochs = 10
        self.learning_rate = 0.001
        self.model_save_path = 'model.pth'
        self.data_file_path = 'data.txt'

def get_config():
    return Config()

def update_config(config, **kwargs):
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

def save_config(config, file_path):
    with open(file_path, 'w') as f:
        for key, value in config.__dict__.items():
            f.write(f'{key}: {value}\n')

def load_config(file_path):
    config = Config()
    with open(file_path, 'r') as f:
        for line in f:
            key, value = line.strip().split(': ')
            if hasattr(config, key):
                setattr(config, key, type(getattr(config, key))(value))
    return config

def print_config(config):
    for key, value in config.__dict__.items():
        print(f'{key}: {value}')