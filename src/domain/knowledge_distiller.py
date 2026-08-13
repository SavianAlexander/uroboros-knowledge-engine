"""
Zero-Cost Knowledge Distillation Dataset Exporter Engine.
Exports high-confidence RAG search paths into Alpaca/ShareGPT JSONL datasets for local model fine-tuning.
Zero-dependency, stdlib implementation.
"""

import json
from typing import Dict, Any, List


def export_knowledge_distillation_dataset(
    rag_interaction_logs: List[Dict[str, Any]],
    format_type: str = "alpaca"
) -> Dict[str, Any]:
    """
    Exports high-confidence RAG interactions into fine-tuning JSONL payloads.
    """
    if not rag_interaction_logs or not isinstance(rag_interaction_logs, list):
        return {
            "format": format_type,
            "exported_records_count": 0,
            "jsonl_payload": "",
            "status": "empty"
        }

    export_records = []

    fmt = str(format_type or "alpaca").lower()
    for log in rag_interaction_logs:
        if not isinstance(log, dict):
            continue
        query = str(log.get("query") or "")
        answer = str(log.get("answer") or "")
        raw_contexts = log.get("contexts")
        if isinstance(raw_contexts, list):
            context = " ".join(str(c) for c in raw_contexts if c is not None)
        else:
            context = str(raw_contexts or "")

        if fmt == "alpaca":
            export_records.append({
                "instruction": query,
                "input": context,
                "output": answer
            })
        else:  # sharegpt
            export_records.append({
                "conversations": [
                    {"from": "human", "value": f"{query}\nContext: {context}"},
                    {"from": "gpt", "value": answer}
                ]
            })

    jsonl_output = "\n".join(json.dumps(r) for r in export_records)

    return {
        "format": format_type,
        "exported_records_count": len(export_records),
        "jsonl_payload": jsonl_output,
        "status": "success"
    }
