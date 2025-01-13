import os
import torch
import torch.nn.functional as F

# Paths to model and vocab
package_path = os.path.dirname(__file__)
model_path = os.path.join(package_path, "text_prediction.pt")
vocab_path = os.path.join(package_path, "vocab.pth")

# Load the model
model = torch.load(model_path, map_location=torch.device("cpu"))
model.eval()

# Load the vocab
vocab = torch.load(vocab_path)

def predict(text: str) -> dict:
    """
    Predict if a text is a suicide post or not and return confidence rate.

    Args:
        text (str): Input text.

    Returns:
        dict: A dictionary with prediction and confidence.
    """
    # Tokenize and preprocess text
    tokens = text.split()  # Replace with your tokenizer logic
    indices = [vocab.stoi.get(token, vocab.stoi["<unk>"]) for token in tokens]
    input_tensor = torch.tensor(indices).unsqueeze(0)

    # Get model output
    output = model(input_tensor)
    probabilities = F.softmax(output, dim=1).squeeze()

    # Get prediction and confidence
    prediction_idx = torch.argmax(probabilities).item()
    confidence = probabilities[prediction_idx].item()

    result = {
        "prediction": "Potential Suicide Post" if prediction_idx == 1 else "Not Suicide Post",
        "confidence": confidence
    }
    return result

# Expose the predict function
__all__ = ["predict"]
