"""CLI Script for fine-tuning LayoutLMv3 on labeled resume dataset."""

import argparse
import logging
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ai.layoutlm_training import LayoutLMTrainingPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Fine-tune LayoutLMv3 for Master Resume Extraction.")
    parser.add_argument("--train-data", required=True, help="Path to labeled training dataset (JSON or JSONL).")
    parser.add_argument("--eval-data", default=None, help="Path to labeled validation dataset.")
    parser.add_argument("--output-dir", default="./storage/layoutlm_model", help="Directory to save fine-tuned model.")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs.")
    parser.add_argument("--batch-size", type=int, default=2, help="Batch size per training step.")
    parser.add_argument("--lr", type=float, default=3e-5, help="Learning rate.")
    parser.add_argument("--model-name", default="microsoft/layoutlmv3-base", help="Base model identifier.")

    args = parser.parse_args()

    pipeline = LayoutLMTrainingPipeline(
        model_name_or_path=args.model_name,
        output_dir=args.output_dir,
    )

    logger.info(f"Loading training data from {args.train_data}...")
    train_samples = pipeline.load_dataset(args.train_data)
    eval_samples = pipeline.load_dataset(args.eval_data) if args.eval_data else None

    logger.info(f"Starting LayoutLMv3 fine-tuning ({args.epochs} epochs, lr={args.lr})...")
    res = pipeline.train(
        train_samples=train_samples,
        eval_samples=eval_samples,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )

    logger.info(f"Fine-tuning complete: {res}")


if __name__ == "__main__":
    main()
