import os
import torch
import torch.nn.functional as F
from torchtext.data.utils import get_tokenizer

# Paths to model and vocab
package_path = os.path.dirname(__file__)
model_path = os.path.join(package_path, "text_prediction.pt")
vocab_path = os.path.join(package_path, "vocab.pth")

class TextClassificationModel(torch.nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_classes):
        super(TextClassificationModel, self).__init__()
        self.embedding = torch.nn.Embedding(vocab_size, embed_dim, padding_idx=1)
        self.lstm = torch.nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = torch.nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, text):
        embedded = self.embedding(text)
        _, (hidden, _) = self.lstm(embedded)
        hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        return self.fc(hidden)


def predict_tweet(tweet, model_path=model_path, vocab=vocab_path, tokenizer=get_tokenizer('basic_english'), max_length=512):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

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

    return 'suicide' if prediction == 1 else 'non-suicide', confidence_rate