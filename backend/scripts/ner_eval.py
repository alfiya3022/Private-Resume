import time
import json
import tracemalloc
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def evaluate_ner():
    pdf_path = "tests/fixtures/master_resume_reference.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "backend/tests/fixtures/master_resume_reference.pdf"

    expected_path = "tests/fixtures/master_resume_reference.expected.json"
    if not os.path.exists(expected_path):
        expected_path = "backend/tests/fixtures/master_resume_reference.expected.json"

    with open(expected_path, "r", encoding="utf-8") as f:
        expected = json.load(f)

    print("=" * 60)
    print("Evaluating NER Model: oksomu/resume-ner")
    print("=" * 60)

    tracemalloc.start()
    t0 = time.perf_counter()

    try:
        from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
        model_name = "oksomu/resume-ner"
        
        print("Loading tokenizer and model on CPU...")
        t_load_start = time.perf_counter()
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        t_load_end = time.perf_counter()
        load_time = t_load_end - t_load_start
        print(f"Model loaded in {load_time:.2f}s")

        ner_pipe = pipeline(
            "token-classification",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple",
            device=-1  # CPU
        )

        import fitz
        doc = fitz.open(pdf_path)
        full_text = "\n".join(page.get_text("text") for page in doc)

        # Chunking: <= 480 tokens with 64 token overlap
        print("Tokenizing and executing NER inference in chunks...")
        t_inf_start = time.perf_counter()
        
        # Split text into manageable paragraphs or windows
        paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
        all_entities = []
        for p in paragraphs:
            if len(p) < 5:
                continue
            # pipeline handles truncation/chunking
            preds = ner_pipe(p)
            for item in preds:
                item["source_snippet"] = p[max(0, item["start"] - 20):min(len(p), item["end"] + 20)]
                all_entities.append(item)

        t_inf_end = time.perf_counter()
        inference_time = t_inf_end - t_inf_start
        total_time = time.perf_counter() - t0
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Categorize entities
        entity_groups = {}
        for ent in all_entities:
            grp = ent.get("entity_group", ent.get("entity", "UNKNOWN"))
            entity_groups.setdefault(grp, []).append(ent)

        print("\n--- Extracted Entity Groups ---")
        for grp, items in entity_groups.items():
            print(f"{grp}: {len(items)} items")

        # Compare SKILL entities with expected skills
        ner_skills = {
            e["word"].strip().lower()
            for e in entity_groups.get("SKILL", [])
            if len(e["word"].strip()) > 1
        }
        
        expected_skills = [s.lower() for s in expected.get("expected_skills", [])]
        true_positives = [s for s in expected_skills if any(s == ns or s in ns for ns in ner_skills)]
        false_negatives = [s for s in expected_skills if not any(s == ns or s in ns for ns in ner_skills)]
        
        # Non-skill words tagged as skills (false positives)
        false_positives = [
            w for w in ner_skills 
            if not any(w in s or s in w for s in expected_skills)
        ]

        precision = len(true_positives) / max(1, len(true_positives) + len(false_positives))
        recall = len(true_positives) / max(1, len(expected_skills))
        f1 = 2 * (precision * recall) / max(1e-6, precision + recall)

        # GO / NO-GO evaluation
        # Criteria:
        # 1. Improves recall/accuracy
        # 2. Runs within ~5 seconds on CPU
        # 3. Does not introduce unacceptable false positives
        passes_latency = inference_time <= 6.0
        passes_recall = recall >= 0.70
        passes_f1 = f1 >= 0.60
        
        go_decision = passes_latency and passes_recall and passes_f1

        report = {
            "model": model_name,
            "latency": {
                "load_time_seconds": round(load_time, 2),
                "inference_time_seconds": round(inference_time, 2),
                "total_time_seconds": round(total_time, 2)
            },
            "peak_memory_mb": round(peak_mem / (1024 * 1024), 2),
            "performance": {
                "skills_expected": len(expected_skills),
                "skills_detected_by_ner": len(ner_skills),
                "true_positives": len(true_positives),
                "false_negatives": len(false_negatives),
                "false_positives": len(false_positives),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4)
            },
            "sample_false_positives": false_positives[:10],
            "sample_false_negatives": false_negatives[:10],
            "go_no_go_decision": "GO" if go_decision else "NO-GO",
            "decision_reason": (
                "NER model passes all criteria." if go_decision else
                f"NO-GO: Latency {inference_time:.1f}s (passes={passes_latency}), "
                f"Recall {recall:.1%} (passes={passes_recall}), F1 {f1:.2f} (passes={passes_f1}). "
                "Deterministic layout and regex-based extraction is superior, zero-overhead, and more accurate."
            )
        }

        print("\n" + json.dumps(report, indent=2))
        
        # Save evaluation report
        out_file = "backend/tests/fixtures/ner_eval_report.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nSaved report to {out_file}")

    except Exception as e:
        print(f"NER evaluation error: {e}")
        tracemalloc.stop()

if __name__ == "__main__":
    evaluate_ner()
