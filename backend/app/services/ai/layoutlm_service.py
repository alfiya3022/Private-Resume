"""LayoutLMv3 Model and Inference Service for Master Resume Extraction."""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple
import fitz  # PyMuPDF
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification

from app.core.config import settings
from app.services.ai.layoutlm_schema import (
    LABEL_LIST,
    ID2LABEL,
    LABEL2ID,
)

logger = logging.getLogger(__name__)


class LayoutLMService:
    """Manages LayoutLMv3 model loading, PDF layout feature extraction, and token-level inference."""

    _instance: Optional["LayoutLMService"] = None

    def __new__(cls) -> "LayoutLMService":
        if cls._instance is None:
            cls._instance = super(LayoutLMService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self.device = torch.device(getattr(settings, "LAYOUTLM_DEVICE", "cpu"))
        self.model_name_or_path = getattr(settings, "LAYOUTLM_MODEL_NAME_OR_PATH", "microsoft/layoutlmv3-base")
        self._processor: Optional[LayoutLMv3Processor] = None
        self._model: Optional[LayoutLMv3ForTokenClassification] = None
        self._is_fine_tuned: bool = False
        self._initialized = True

    @property
    def processor(self) -> LayoutLMv3Processor:
        if self._processor is None:
            self._load_processor()
        return self._processor

    @property
    def model(self) -> LayoutLMv3ForTokenClassification:
        if self._model is None:
            self._load_model()
        return self._model

    def _load_processor(self) -> None:
        """Loads LayoutLMv3 processor without OCR dependency (word boxes supplied via PyMuPDF)."""
        try:
            logger.info("Initializing LayoutLMv3 processor...")
            self._processor = LayoutLMv3Processor.from_pretrained(
                self.model_name_or_path,
                apply_ocr=False,
            )
        except Exception as exc:
            logger.error(f"Failed to load LayoutLMv3 processor from {self.model_name_or_path}: {exc}")
            # Fallback to base model identifier if custom path failed
            if self.model_name_or_path != "microsoft/layoutlmv3-base":
                self._processor = LayoutLMv3Processor.from_pretrained(
                    "microsoft/layoutlmv3-base",
                    apply_ocr=False,
                )
            else:
                raise exc

    def _load_model(self) -> None:
        """Loads LayoutLMv3 token classification model onto target device."""
        try:
            logger.info(f"Loading LayoutLMv3 model from {self.model_name_or_path}...")
            # Check if custom fine-tuned weights exist
            is_local_dir = os.path.isdir(self.model_name_or_path) and os.path.exists(
                os.path.join(self.model_name_or_path, "config.json")
            )
            self._is_fine_tuned = is_local_dir

            self._model = LayoutLMv3ForTokenClassification.from_pretrained(
                self.model_name_or_path,
                num_labels=len(LABEL_LIST),
                id2label=ID2LABEL,
                label2id=LABEL2ID,
            )
            self._model.to(self.device)
            self._model.eval()
            logger.info(f"LayoutLMv3 model loaded successfully (fine_tuned={self._is_fine_tuned}, device={self.device}).")
        except Exception as exc:
            logger.error(f"Failed to load LayoutLMv3 model: {exc}")
            if self.model_name_or_path != "microsoft/layoutlmv3-base":
                logger.info("Falling back to microsoft/layoutlmv3-base pretrained model...")
                self._model = LayoutLMv3ForTokenClassification.from_pretrained(
                    "microsoft/layoutlmv3-base",
                    num_labels=len(LABEL_LIST),
                    id2label=ID2LABEL,
                    label2id=LABEL2ID,
                )
                self._model.to(self.device)
                self._model.eval()
                self._is_fine_tuned = False
            else:
                raise exc

    def extract_page_features(
        self, doc: fitz.Document, page_num: int
    ) -> Tuple[Image.Image, List[str], List[List[int]], List[List[float]], List[Dict[str, Any]]]:
        """Extracts rendered page image, text words, normalized boxes, raw bboxes, and link annotations."""
        page = doc[page_num]
        w, h = page.rect.width, page.rect.height

        # 1. Render page image
        pix = page.get_pixmap(dpi=150)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # 2. Extract words and bounding boxes: (x0, y0, x1, y1, word, block_no, line_no, word_no)
        raw_words = page.get_text("words")
        words: List[str] = []
        raw_boxes: List[List[float]] = []
        norm_boxes: List[List[int]] = []

        for item in raw_words:
            x0, y0, x1, y1, word_text = item[0], item[1], item[2], item[3], str(item[4])
            clean_word = word_text.strip()
            if not clean_word:
                continue

            words.append(clean_word)
            raw_boxes.append([round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)])

            # Normalize to [0, 1000] scale for LayoutLMv3
            nx0 = max(0, min(1000, int(1000.0 * x0 / max(1.0, w))))
            ny0 = max(0, min(1000, int(1000.0 * y0 / max(1.0, h))))
            nx1 = max(0, min(1000, int(1000.0 * x1 / max(1.0, w))))
            ny1 = max(0, min(1000, int(1000.0 * y1 / max(1.0, h))))
            norm_boxes.append([nx0, ny0, nx1, ny1])

        # 3. Extract link annotations
        links: List[Dict[str, Any]] = []
        for lk in page.get_links():
            uri = lk.get("uri")
            rect = lk.get("from")
            if uri and rect:
                links.append({
                    "uri": str(uri).strip(),
                    "rect": [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)],
                    "page": page_num,
                })

        return image, words, norm_boxes, raw_boxes, links

    def predict_page(
        self,
        image: Image.Image,
        words: List[str],
        norm_boxes: List[List[int]],
        raw_boxes: List[List[float]],
    ) -> List[Dict[str, Any]]:
        """Executes LayoutLMv3 token classification on a single page, respecting sequence limits."""
        if not words:
            return []

        results: List[Dict[str, Any]] = []

        # Process words in chunks if word count exceeds safe limit (~300 words usually yields ~512 subwords)
        chunk_size = 280
        overlap = 30
        idx = 0

        while idx < len(words):
            end_idx = min(idx + chunk_size, len(words))
            chunk_words = words[idx:end_idx]
            chunk_norm_boxes = norm_boxes[idx:end_idx]
            chunk_raw_boxes = raw_boxes[idx:end_idx]

            try:
                encoding = self.processor(
                    image,
                    chunk_words,
                    boxes=chunk_norm_boxes,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding="max_length",
                )

                # Move tensors to model device
                for k in encoding:
                    if isinstance(encoding[k], torch.Tensor):
                        encoding[k] = encoding[k].to(self.device)

                with torch.no_grad():
                    outputs = self.model(**encoding)
                    logits = outputs.logits
                    probs = F.softmax(logits, dim=-1).squeeze(0)
                    preds = torch.argmax(logits, dim=-1).squeeze(0)

                # Map subwords back to words via word_ids
                word_ids = encoding.word_ids(0)
                seen_words = set()

                for token_idx, word_id in enumerate(word_ids):
                    if word_id is None or word_id in seen_words:
                        continue
                    if word_id < len(chunk_words):
                        label_id = int(preds[token_idx].item())
                        confidence = float(probs[token_idx, label_id].item())
                        label_str = ID2LABEL.get(label_id, "O")

                        results.append({
                            "word": chunk_words[word_id],
                            "label": label_str,
                            "confidence": round(confidence, 4),
                            "bbox": chunk_raw_boxes[word_id],
                            "normalized_bbox": chunk_norm_boxes[word_id],
                        })
                        seen_words.add(word_id)

            except Exception as e:
                logger.warning(f"Error during LayoutLMv3 chunk inference: {e}")
                for w_item, r_box, n_box in zip(chunk_words, chunk_raw_boxes, chunk_norm_boxes):
                    results.append({
                        "word": w_item,
                        "label": "O",
                        "confidence": 0.0,
                        "bbox": r_box,
                        "normalized_bbox": n_box,
                    })

            if end_idx >= len(words):
                break
            idx += (chunk_size - overlap)

        return results

    def extract_document_layout(self, file_path: str) -> Dict[str, Any]:
        """Extracts complete multi-page document features, layout tokens, and link annotations."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume PDF not found at {file_path}")

        doc = fitz.open(file_path)
        try:
            if doc.is_encrypted:
                raise ValueError("Password-protected or encrypted PDFs are not supported.")

            total_pages = len(doc)
            all_pages_data: List[Dict[str, Any]] = []
            all_links: List[Dict[str, Any]] = []
            total_words_count = 0

            for p_idx in range(total_pages):
                image, words, norm_boxes, raw_boxes, links = self.extract_page_features(doc, p_idx)
                total_words_count += len(words)
                all_links.extend(links)

                predictions = self.predict_page(image, words, norm_boxes, raw_boxes)

                all_pages_data.append({
                    "page_index": p_idx,
                    "word_count": len(words),
                    "tokens": predictions,
                    "page_width": doc[p_idx].rect.width,
                    "page_height": doc[p_idx].rect.height,
                })

            if total_words_count == 0:
                raise ValueError("No readable text found in this PDF. Scanned or image-only PDFs are not supported.")

            return {
                "file_path": file_path,
                "total_pages": total_pages,
                "total_words": total_words_count,
                "is_fine_tuned": self._is_fine_tuned,
                "pages": all_pages_data,
                "links": all_links,
            }
        finally:
            doc.close()


layoutlm_service = LayoutLMService()
