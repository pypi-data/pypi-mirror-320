import torch
import torch.nn as nn

class PuretalkTTS(nn.Module):
    # Define the model architecture
    # It will initialise the preprocessing
    # structure of the RUTH-tts
    # whre the text will be processoced into the meaninggfull embeddding
    def __init__(self, input_dim=256, hidden_dim=512, output_dim=80, num_layers=3):
        super(PuretalkTTS, self).__init__()
        
        # Text embedding layer
        self.text_embedding = nn.Linear(input_dim, hidden_dim)
        
        # Encoder with multi-layer BiLSTM
        self.encoder_lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            batch_first=True
        )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim * 2,
            num_heads=8,
            batch_first=True
        )
        
        # Decoder layers
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            nn.Linear(hidden_dim, output_dim),
            nn.Tanh()
        )
        
    def forward(self, text_features: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the model
        Args:
            text_features: Input tensor of shape [batch_size, sequence_length, input_dim]
        Returns:
            torch.Tensor: Output mel spectrogram of shape [batch_size, sequence_length, output_dim]
        """
        # Text embedding
        embedded = self.text_embedding(text_features)
        
        # Encoder LSTM
        encoded, _ = self.encoder_lstm(embedded)
        
        # Self-attention
        attn_output, _ = self.attention(encoded, encoded, encoded)
        
        # Decode to mel spectrogram
        mel_output = self.decoder(attn_output)
        
        return mel_output

    def generate_speech(self, text_features: torch.Tensor) -> torch.Tensor:
        """
        Generate speech from text features
        Args:
            text_features: Tensor of shape [batch_size, sequence_length, input_dim]
        Returns:
            torch.Tensor: Mel spectrogram of shape [batch_size, sequence_length, output_dim]
        """
        self.eval()
        with torch.no_grad():
            mel_output = self.forward(text_features)
        self.train()
        return mel_output