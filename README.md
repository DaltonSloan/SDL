# SDL – Symbol Detection Lab

This repository houses a lightweight pipeline for training and evaluating a ResNet-18 classifier on a custom symbol dataset.  It includes utilities for organizing raw SVG/PNG assets into train/val/test splits, generating class metadata, training the model, and running evaluations or single-image predictions.

## Features
- Scripts to turn scraped symbol assets into clean ImageFolder splits (`make_splits.py`, `organize_classes.py`, `make_classes_json.py`).
- ResNet-18 training loop (`train_model.py`) that saves weights to `symbol_classifier.pth`.
- Evaluation helper (`eval.py`) with classification report + confusion matrix.
- Command-line prediction script (`predict.py`) for quick sanity checks on individual PNGs/SVG renders.

## Requirements
- Python 3.10+
- PyTorch with torchvision (Metal Performance Shaders are used automatically on macOS if available)
- See `requirements.txt` for the exact pip packages.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Preparing the dataset
1. Place your cleaned class folders (each subdirectory = class name) under `dataset/classes/`.
2. (Optional) Run `python make_classes_json.py` to regenerate `classes.json`, which maps numeric IDs to class names.
3. Create stratified train/val/test splits:
   ```bash
   python make_splits.py
   ```
   This populates `dataset/splits/{train,val,test}/<class>/image.png`, matching the layout expected by TorchVision's `ImageFolder`.

> **Note:** The raw dataset, intermediate SVG dumps, and trained weights are ignored via `.gitignore`.  Each collaborator should regenerate them locally.

## Step-by-step workflow
Follow this order if you want a verbose roadmap from a blank checkout to a trained model:

1. **Set up Python + packages**  
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   This ensures `torch`, `torchvision`, `pillow`, `numpy`, `scikit-learn`, and `tqdm` match the versions used during development.

2. **Organize/clean raw assets (optional)**  
   Use helper scripts (`classes_cleanup.py`, `organize_classes.py`, `svg_pipeline.sh`, etc.) to make sure every class lives under `dataset/classes/<class_name>/image.png`.  These scripts are optional but save time when wrangling scraped SVGs.

3. **Generate class metadata**  
   ```
   python make_classes_json.py
   ```
   This produces `classes.json`, a numeric ID → class name map consumed by `predict.py` and any downstream tooling.

4. **Build train/val/test splits**  
   ```
   python make_splits.py
   ```
   The script copies files from `dataset/classes` into `dataset/splits/{train,val,test}` with consistent ratios so that TorchVision's `ImageFolder` loaders work out of the box.

5. **Train the model**  
   ```
   python train_model.py
   ```
   Monitor the epoch logs for convergence. At the end you should see `Saved model → symbol_classifier.pth`.

6. **Evaluate on the held-out test set**  
   ```
   python eval.py
   ```
   Requires the weights from Step 5. Prints a detailed classification report plus confusion matrix to validate performance.

7. **Run ad-hoc predictions (optional sanity check)**  
   ```
   python predict.py path/to/image.png
   ```
   Confirms that the exported weights and `classes.json` load correctly and gives you top‑5 probabilities for any single symbol image.

## Training
`train_model.py` fine-tunes a pretrained ResNet-18 using the splits above.

```bash
python train_model.py
```

- Configurable constants live at the top of the script (`DATASET_DIR`, `BATCH`, `EPOCHS`, `LR`).
- The script automatically chooses `mps` on Apple Silicon, otherwise falls back to CPU.
- Model weights are saved to `symbol_classifier.pth` in the project root.

## Evaluation
Use `eval.py` to compute metrics on the held-out test split.

```bash
python eval.py
```

This will print a classification report and confusion matrix. Ensure `symbol_classifier.pth` exists (from training) before running.

## Single-image prediction
`predict.py` loads the trained weights plus `classes.json` and reports the top‑5 predictions for any PNG.

```bash
python predict.py path/to/image.png
```

## Repository structure
```
images/
├── dataset/                 # Ignored – expected structure: classes/ and splits/
├── train_model.py           # ResNet-18 fine-tuning script
├── eval.py                  # Test-set evaluation helper
├── predict.py               # CLI inference utility
├── make_splits.py           # Build train/val/test folders from dataset/classes
├── make_classes_json.py     # Export class index ↔ name mapping
├── requirements.txt         # Python dependencies
├── README.md                # Project overview & instructions
└── ...                      # Additional helpers for scraping/cleanup (see file headers)
```

## Next steps
- Double-check `.gitignore` before committing to avoid uploading large datasets or checkpoints.
- Document any additional preprocessing scripts directly in their headers for future contributors.
- Consider exporting example notebooks or unit tests if you expand the pipeline further.
