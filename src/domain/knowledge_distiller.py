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
    export_records = []

    for log in rag_interaction_logs:
        query = log.get("query", "")
        answer = log.get("answer", "")
        context = " ".join(log.get("contexts", []))

        if format_type.lower() == "alpaca":
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
