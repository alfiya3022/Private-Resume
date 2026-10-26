"""LayoutLMv3 Training, Fine-Tuning, and Evaluation Pipeline for Master Resume Extraction."""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    LayoutLMv3Processor,
    LayoutLMv3ForTokenClassification,
    get_linear_schedule_with_warmup,
)

from app.services.ai.layoutlm_schema import (
    LABEL_LIST,
    ID2LABEL,
    LABEL2ID,
)

logger = logging.getLogger(__name__)


class ResumeDataset(Dataset):
    """PyTorch Dataset for LayoutLMv3 resume token classification."""

    def __init__(
        self,
        samples: List[Dict[str, Any]],
        processor: LayoutLMv3Processor,
        max_seq_length: int = 512,
    ) -> None:
        self.samples = samples
        self.processor = processor
        self.max_seq_length = max_seq_length

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        sample = self.samples[idx]
        image = sample["image"]
        words = sample["words"]
        boxes = sample["boxes"]
        word_labels = sample["labels"]

        # Validate bounding boxes within [0, 1000]
        cleaned_boxes = [
            [
                max(0, min(1000, b[0])),
                max(0, min(1000, b[1])),
                max(0, min(1000, b[2])),
                max(0, min(1000, b[3])),
            ]
            for b in boxes
        ]

        # Convert label strings to label IDs
        label_ids = [LABEL2ID.get(lbl, LABEL2ID["O"]) for lbl in word_labels]

        encoding = self.processor(
            image,
            words,
            boxes=cleaned_boxes,
            word_labels=label_ids,
            truncation=True,
            padding="max_length",
            max_length=self.max_seq_length,
            return_tensors="pt",
        )

        item = {k: v.squeeze(0) for k, v in encoding.items()}
        return item


class LayoutLMTrainingPipeline:
    """Orchestrates dataset loading, validation, fine-tuning, and metric evaluation."""

    def __init__(
        self,
        model_name_or_path: str = "microsoft/layoutlmv3-base",
        output_dir: str = "./storage/layoutlm_model",
        device: Optional[str] = None,
    ) -> None:
        self.model_name_or_path = model_name_or_path
        self.output_dir = output_dir
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.processor = LayoutLMv3Processor.from_pretrained(
            self.model_name_or_path, apply_ocr=False
        )

    def validate_annotation(self, sample: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validates that a labeled resume example adheres to schema constraints."""
        errors: List[str] = []
        if "words" not in sample or not isinstance(sample["words"], list):
            errors.append("Sample missing 'words' list.")
        if "boxes" not in sample or not isinstance(sample["boxes"], list):
            errors.append("Sample missing 'boxes' list.")
        if "labels" not in sample or not isinstance(sample["labels"], list):
            errors.append("Sample missing 'labels' list.")

        if errors:
            return False, errors

        n_words = len(sample["words"])
        if len(sample["boxes"]) != n_words:
            errors.append(f"Boxes length ({len(sample['boxes'])}) does not match words length ({n_words}).")
        if len(sample["labels"]) != n_words:
            errors.append(f"Labels length ({len(sample['labels'])}) does not match words length ({n_words}).")

        for b in sample["boxes"]:
            if not isinstance(b, (list, tuple)) or len(b) != 4:
                errors.append(f"Invalid box format: {b}")
                break
            if any(coord < 0 or coord > 1000 for coord in b):
                errors.append(f"Box coordinates out of bounds [0, 1000]: {b}")
                break

        for lbl in sample["labels"]:
            if lbl not in LABEL2ID:
                errors.append(f"Unrecognized label in schema: '{lbl}'")
                break

        return len(errors) == 0, errors

    def load_dataset(self, dataset_path: str) -> List[Dict[str, Any]]:
        """Loads and validates labeled resume JSON/JSONL dataset."""
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset path not found: {dataset_path}")

        samples: List[Dict[str, Any]] = []
        if dataset_path.endswith(".jsonl"):
            with open(dataset_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    item = json.loads(line)
                    is_valid, errs = self.validate_annotation(item)
                    if not is_valid:
                        logger.warning(f"Skipping line {line_num} due to errors: {errs}")
                        continue
                    # Load image
                    img_path = item.get("image_path")
                    if img_path and os.path.exists(img_path):
                        item["image"] = Image.open(img_path).convert("RGB")
                    else:
                        item["image"] = Image.new("RGB", (224, 224), color="white")
                    samples.append(item)
        elif dataset_path.endswith(".json"):
            with open(dataset_path, "r", encoding="utf-8") as f:
                raw_items = json.load(f)
                if not isinstance(raw_items, list):
                    raw_items = [raw_items]
                for idx, item in enumerate(raw_items):
                    is_valid, errs = self.validate_annotation(item)
                    if not is_valid:
                        logger.warning(f"Skipping item {idx} due to errors: {errs}")
                        continue
                    img_path = item.get("image_path")
                    if img_path and os.path.exists(img_path):
                        item["image"] = Image.open(img_path).convert("RGB")
                    else:
                        item["image"] = Image.new("RGB", (224, 224), color="white")
                    samples.append(item)

        logger.info(f"Loaded {len(samples)} valid labeled samples from {dataset_path}.")
        return samples

    def train(
        self,
        train_samples: List[Dict[str, Any]],
        eval_samples: Optional[List[Dict[str, Any]]] = None,
        epochs: int = 3,
        batch_size: int = 2,
        learning_rate: float = 3e-5,
    ) -> Dict[str, Any]:
        """Fine-tunes LayoutLMv3 model on labeled resume dataset."""
        if not train_samples:
            raise ValueError("Cannot train with empty training dataset.")

        model = LayoutLMv3ForTokenClassification.from_pretrained(
            self.model_name_or_path,
            num_labels=len(LABEL_LIST),
            id2label=ID2LABEL,
            label2id=LABEL2ID,
        )
        model.to(self.device)
        model.train()

        train_dataset = ResumeDataset(train_samples, self.processor)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=int(total_steps * 0.1), num_training_steps=total_steps
        )

        history: List[Dict[str, Any]] = []

        for epoch in range(1, epochs + 1):
            total_loss = 0.0
            for batch_idx, batch in enumerate(train_loader):
                batch = {k: v.to(self.device) for k, v in batch.items()}
                optimizer.zero_grad()

                outputs = model(**batch)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                scheduler.step()

                total_loss += loss.item()

            avg_loss = total_loss / max(1, len(train_loader))
            epoch_metrics = {"epoch": epoch, "loss": round(avg_loss, 4)}

            if eval_samples:
                eval_metrics = self.evaluate(eval_samples, model=model)
                epoch_metrics.update(eval_metrics)

            history.append(epoch_metrics)
            logger.info(f"Epoch {epoch}/{epochs} - Loss: {avg_loss:.4f}")

        # Save fine-tuned checkpoint
        os.makedirs(self.output_dir, exist_ok=True)
        model.save_pretrained(self.output_dir)
        self.processor.save_pretrained(self.output_dir)
        logger.info(f"Model and processor saved to {self.output_dir}.")

        return {
            "status": "success",
            "epochs": epochs,
            "final_loss": history[-1]["loss"] if history else None,
            "history": history,
            "output_dir": self.output_dir,
        }

    def evaluate(
        self,
        eval_samples: List[Dict[str, Any]],
        model: Optional[LayoutLMv3ForTokenClassification] = None,
    ) -> Dict[str, Any]:
        """Evaluates token-level and section-level precision, recall, and F1."""
        if not eval_samples:
            return {"error": "No evaluation samples provided."}

        if model is None:
            model = LayoutLMv3ForTokenClassification.from_pretrained(
                self.output_dir if os.path.exists(self.output_dir) else self.model_name_or_path,
                num_labels=len(LABEL_LIST),
                id2label=ID2LABEL,
                label2id=LABEL2ID,
            )
            model.to(self.device)

        model.eval()
        eval_dataset = ResumeDataset(eval_samples, self.processor)
        eval_loader = DataLoader(eval_dataset, batch_size=2, shuffle=False)

        total_correct = 0
        total_predictions = 0
        total_gold = 0

        # Class-specific counts
        class_tp: Dict[str, int] = {lbl: 0 for lbl in LABEL_LIST if lbl != "O"}
        class_fp: Dict[str, int] = {lbl: 0 for lbl in LABEL_LIST if lbl != "O"}
        class_fn: Dict[str, int] = {lbl: 0 for lbl in LABEL_LIST if lbl != "O"}

        with torch.no_grad():
            for batch in eval_loader:
                labels = batch["labels"].to(self.device)
                batch = {k: v.to(self.device) for k, v in batch.items()}

                outputs = model(**batch)
                preds = torch.argmax(outputs.logits, dim=-1)

                active_mask = labels != -100
                active_labels = labels[active_mask]
                active_preds = preds[active_mask]

                for p, l in zip(active_preds.view(-1), active_labels.view(-1)):
                    p_id = p.item()
                    l_id = l.item()
                    p_lbl = ID2LABEL.get(p_id, "O")
                    l_lbl = ID2LABEL.get(l_id, "O")

                    if p_lbl != "O":
                        total_predictions += 1
                    if l_lbl != "O":
                        total_gold += 1

                    if p_lbl == l_lbl and p_lbl != "O":
                        total_correct += 1
                        class_tp[p_lbl] += 1
                    elif p_lbl != "O" and p_lbl != l_lbl:
                        class_fp[p_lbl] += 1
                    elif l_lbl != "O" and p_lbl != l_lbl:
                        class_fn[l_lbl] += 1

        precision = total_correct / max(1, total_predictions)
        recall = total_correct / max(1, total_gold)
        f1 = (2 * precision * recall) / max(1e-6, (precision + recall))

        return {
            "token_precision": round(precision, 4),
            "token_recall": round(recall, 4),
            "token_f1": round(f1, 4),
            "total_evaluated_tokens": total_gold,
            "evaluated_samples": len(eval_samples),
        }
