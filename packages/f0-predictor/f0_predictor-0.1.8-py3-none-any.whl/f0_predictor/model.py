# f0_predictor/model.py
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler

class F0PredictionModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, sequence_length):
        super(F0PredictionModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.sequence_length = sequence_length

        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                           batch_first=True, bidirectional=True)
        self.fc1 = nn.Linear(hidden_size * 2 * self.sequence_length, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        batch_size = x.size(0)
        h0 = torch.zeros(self.num_layers * 2, batch_size, self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers * 2, batch_size, self.hidden_size).to(x.device)

        out, _ = self.lstm(x, (h0, c0))
        out = out.reshape(batch_size, -1)
        out = self.fc1(out)
        out = self.fc2(out)
        return out

def load_or_create_model(model_path=None):
    """Load a trained model or create a new one."""
    sequence_length = 50
    model = F0PredictionModel(
        input_size=1,
        hidden_size=64,
        num_layers=2,
        output_size=1,
        sequence_length=sequence_length
    )

    scaler = StandardScaler()

    if model_path and torch.cuda.is_available():
        checkpoint = torch.load(model_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        scaler = checkpoint['scaler']
    elif model_path:
        checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
        model.load_state_dict(checkpoint['model_state_dict'])
        scaler = checkpoint['scaler']

    return model, scaler, sequence_length