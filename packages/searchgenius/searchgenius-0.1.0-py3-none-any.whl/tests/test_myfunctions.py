import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import accuracy_score

# Assuming your classes and functions are imported, e.g.:
# from your_module import FullyConnected, MLPsoftmax, ESCIDataset, generate_embeddings

def test_fully_connected():
    print("Testing FullyConnected...")
    model = FullyConnected(input_dim=100, hidden_dim=50, output_dim=10)
    dummy_input = torch.rand(5, 100)  # Batch size 5, input_dim 100
    output = model(dummy_input)
    assert output.shape == (5, 10), f"Expected output shape (5, 10), got {output.shape}"
    print("FullyConnected passed.")

def test_mlp_softmax():
    print("Testing MLPsoftmax...")
    model = MLPsoftmax(input_dim=100, hidden_dim=50, output_dim=10)
    dummy_input = torch.rand(5, 100)
    output = model(dummy_input)
    assert output.shape == (5, 10), f"Expected output shape (5, 10), got {output.shape}"
    assert torch.allclose(output.sum(dim=1), torch.tensor([1.0]*5), atol=1e-6), "Softmax outputs do not sum to 1."
    print("MLPsoftmax passed.")

def test_escidataset():
    print("Testing ESCIDataset...")
    dummy_data = {
        "text_a": ["sample text 1", "sample text 2"],
        "text_b": ["sample pair 1", "sample pair 2"],
        "label": [0, 1]
    }
    dataset = ESCIDataset(dummy_data, tokenizer=lambda x: torch.tensor([1, 2, 3]), max_length=5)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=False)
    batch = next(iter(dataloader))
    assert batch["text_a"].shape == (2, 5), "Unexpected shape for text_a"
    assert batch["label"].shape == (2,), "Unexpected shape for label"
    print("ESCIDataset passed.")

def test_generate_embeddings():
    print("Testing generate_embeddings...")
    vocab = ["word1", "word2", "word3"]
    embedding_dim = 5
    embeddings = generate_embeddings(vocab, embedding_dim)
    assert embeddings.shape == (len(vocab), embedding_dim), "Embeddings shape mismatch"
    print("generate_embeddings passed.")

def test_training_loop():
    print("Testing training loop...")
    # Mock data
    dummy_data = {
        "text_a": ["sample text 1", "sample text 2", "sample text 3", "sample text 4"],
        "text_b": ["sample pair 1", "sample pair 2", "sample pair 3", "sample pair 4"],
        "label": [0, 1, 0, 1]
    }
    dataset = ESCIDataset(dummy_data, tokenizer=lambda x: torch.tensor([1, 2, 3]), max_length=5)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

    model = FullyConnected(input_dim=5, hidden_dim=10, output_dim=2)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    for epoch in range(1):  # One epoch for testing
        model.train()
        for batch in dataloader:
            optimizer.zero_grad()
            outputs = model(batch["text_a"].float())
            loss = criterion(outputs, batch["label"])
            loss.backward()
            optimizer.step()

    print("Training loop passed.")

def test_evaluation_loop():
    print("Testing evaluation loop...")
    # Mock data
    dummy_data = {
        "text_a": ["sample text 1", "sample text 2"],
        "text_b": ["sample pair 1", "sample pair 2"],
        "label": [0, 1]
    }
    dataset = ESCIDataset(dummy_data, tokenizer=lambda x: torch.tensor([1, 2, 3]), max_length=5)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=False)

    model = MLPsoftmax(input_dim=5, hidden_dim=10, output_dim=2)
    predictions, labels = [], []

    model.eval()
    with torch.no_grad():
        for batch in dataloader:
            outputs = model(batch["text_a"].float())
            preds = torch.argmax(outputs, dim=1).numpy()
            predictions.extend(preds)
            labels.extend(batch["label"].numpy())

    acc = accuracy_score(labels, predictions)
    print(f"Accuracy: {acc}")
    assert 0 <= acc <= 1, "Accuracy out of bounds"
    print("Evaluation loop passed.")

if __name__ == "__main__":
    test_fully_connected()
    test_mlp_softmax()
    test_escidataset()
    test_generate_embeddings()
    test_training_loop()
    test_evaluation_loop()
