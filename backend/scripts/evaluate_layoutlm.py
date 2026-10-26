"""CLI Script for evaluating LayoutLMv3 token and record-level metrics on held-out resumes."""

import argparse
import json
import logging
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ai.layoutlm_training import LayoutLMTrainingPipeline
from app.services.ai.layoutlm_service import layoutlm_service
from app.services.ai.record_grouping import record_grouping_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Evaluate LayoutLMv3 Master Resume Extraction.")
    parser.add_argument("--test-data", default=None, help="Path to labeled evaluation dataset (JSON/JSONL).")
    parser.add_argument("--pdf-dir", default=None, help="Directory of PDF resumes for end-to-end evaluation.")
    parser.add_argument("--model-path", default=None, help="Model checkpoint path to evaluate.")

    args = parser.parse_args()

    pipeline = LayoutLMTrainingPipeline(
        model_name_or_path=args.model_path or layoutlm_service.model_name_or_path,
    )

    if args.test_data:
        logger.info(f"Evaluating token classification on {args.test_data}...")
        test_samples = pipeline.load_dataset(args.test_data)
        metrics = pipeline.evaluate(test_samples)
        print("\n--- Token Classification Evaluation Metrics ---")
        print(json.dumps(metrics, indent=2))

    if args.pdf_dir and os.path.isdir(args.pdf_dir):
        logger.info(f"Evaluating PDF extraction on documents in {args.pdf_dir}...")
        pdf_files = [
            os.path.join(args.pdf_dir, f)
            for f in os.listdir(args.pdf_dir)
            if f.lower().endswith(".pdf")
        ]
        results = []
        for pdf in pdf_files:
            try:
                doc_layout = layoutlm_service.extract_document_layout(pdf)
                structured = record_grouping_service.group_records(
                    layout_lines=[t for p in doc_layout["pages"] for t in p["tokens"]],
                    links=doc_layout["links"],
                )
                results.append({
                    "file": os.path.basename(pdf),
                    "status": "success",
                    "personal_name": bool(structured["personal_info"].get("name")),
                    "experience_count": len(structured.get("experience", [])),
                    "projects_count": len(structured.get("projects", [])),
                    "skills_count": len(structured.get("skills", [])),
                })
            except Exception as e:
                results.append({"file": os.path.basename(pdf), "status": "error", "error": str(e)})

        print("\n--- End-to-End Extraction Summary ---")
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
