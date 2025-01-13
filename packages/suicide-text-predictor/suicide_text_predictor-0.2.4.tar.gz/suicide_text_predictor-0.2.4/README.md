# Suicide Text Predictor

This package predicts if a given text is a suicide post or not using a trained PyTorch model.

## Installation

```bash
pip install suicide_text_predictor
```
## Sample Usage
```python
import suicide_text_predictor
text = input("Input a text:\n")
result=suicide_text_predictor.predict_tweet(text)
print(result)
```