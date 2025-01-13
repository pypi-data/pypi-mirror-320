import os
import torch
import torch.nn.functional as F
from torchtext.data.utils import get_tokenizer
import sys
import re
import torch.nn as nn
# Paths to model and vocab
package_path = os.path.dirname(__file__)
__MODEL_PATH__ = os.path.join(package_path, "text_prediction.pt")
vocab_path = os.path.join(package_path, "vocab.pth")
__VOCAB__ = torch.load(vocab_path)
class TextClassificationModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_classes, num_layers=2, dropout=0.5):
        super(TextClassificationModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=1)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=num_layers,
                           batch_first=True, bidirectional=True, dropout=dropout if num_layers > 1 else 0)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, text):
        embedded = self.embedding(text)
        output, (hidden, cell) = self.lstm(embedded)
        hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        hidden = self.dropout(hidden)
        return self.fc(hidden)


def predict_tweet(tweet, model_path=__MODEL_PATH__, vocab=__VOCAB__, tokenizer=get_tokenizer('basic_english'), max_length=512):
    device = torch.device('cpu')
    model = TextClassificationModel(vocab_size=len(vocab), embed_dim=256, hidden_dim=128, num_classes=2)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    tweet = re.sub(r"http\S+|www.\S+", "", tweet.lower())
    tweet = re.sub(r"@\w+", "@user", tweet)
    tweet = re.sub(r"[^\w\s]", "", tweet)
    tokens = tokenizer(tweet)
    indices = [vocab[token] for token in tokens]

    if len(indices) < max_length:
        indices += [vocab['<pad>']] * (max_length - len(indices))
    else:
        indices = indices[:max_length]

    input_tensor = torch.tensor([indices], dtype=torch.long).to(device)
    with torch.no_grad():
        output = model(input_tensor)
        prediction = torch.argmax(output, dim=1).item()
        probabilities = torch.nn.functional.softmax(output, dim=1)
        confidence_rate = probabilities[0, prediction].item()
    pred_res = 'SUICIDE' if prediction == 1 else 'NON-SUICIDE'
    res=f"Your Tweet: {tweet}\nPrediction: {pred_res} with confidence rate: {confidence_rate*100:.4}%"
    # return 'suicide' if prediction == 1 else 'non-suicide', confidence_rate
    return res