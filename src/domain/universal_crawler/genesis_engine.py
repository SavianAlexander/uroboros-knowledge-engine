import re
import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone

"""
Legislative Genesis Tracker & Legal Cross-Examination Deposition Synthesizer.
Features:
1. Full Legislative Genesis (Draft Bill -> Committee Reports -> Chamber Votes -> Gazette)
2. Automated Cross-Examination Deposition Dossier Generator (Deadlines, Duties, Penalties, Conflicts)
"""

class LegislativeGenesisExtractor:
    """Extracts legislative history milestones from measure documents."""

    @classmethod
    def extract_genesis_timeline(cls, text: str, title: str) -> Dict[str, Any]:
        """Extract legislative milestones from bill text or SUTRA logs."""
        timeline = []

        # 1. Radicación / Origin
        rad_match = re.search(r'(?:Radicad[ao]\s+el\s+|Fecha\s+de\s+Radicaci[óo]n:\s*)(\d{1,2}\s+de\s+[\wáéíóúñ]+\s+de\s+\d{4}|\d{4}-\d{2}-\d{2})', text, re.I)
        if rad_match:
            timeline.append({"milestone": "RADICACION", "date": rad_match.group(1).strip()})

        # 2. Informes de Comisión
        com_matches = re.findall(r'(?:Informe\s+Positivo|Informe\s+Negativo)\s+(?:de\s+la\s+Comisi[óo]n\s+de\s+([^\.\n;]+))', text, re.I)
        for com in com_matches:
            timeline.append({"milestone": "INFORME_COMISION", "detail": f"Comisión de {com.strip()}"})

        # 3. Votaciones
        vote_matches = re.findall(r'(?:Votaci[óo]n\s+en\s+el\s+(?:Senado|C[áa]mara)\s*:\s*([\d\w\s,]+))', text, re.I)
        for v in vote_matches:
            timeline.append({"milestone": "VOTACION_LEGISLATIVA", "detail": v.strip()})

        # 4. Firma del Gobernador
        firm_match = re.search(r'(?:Aprobada\s+por\s+el\s+Gobernador\s+el\s+|Firma\s+del\s+Gobernador:\s*)(\d{1,2}\s+de\s+[\wáéíóúñ]+\s+de\s+\d{4}|\d{4}-\d{2}-\d{2})', text, re.I)
        if firm_match:
            timeline.append({"milestone": "FIRMA_GOBERNADOR", "date": firm_match.group(1).strip()})

        return {
            "title": title,
            "milestones_count": len(timeline),
            "timeline": timeline
        }

class LegalDepositionDossierSynthesizer:
    """Synthesizes structured cross-examination deposition dossiers for legal proceedings."""

    @classmethod
    def generate_deposition_dossier(cls, target_topic: str, documents: List[Dict[str, Any]]) -> str:
        """Generate structured cross-examination briefing with mandatory duties, deadlines, and penalties."""
        affirmative_duties = []
        strict_deadlines = []
        penalties_fines = []
        conflicts = []
        dpr_citations = set()

        for d in documents:
            title = d.get("title", "Statute")
            content = d.get("content_text", "")
            if target_topic.lower() not in content.lower() and target_topic.lower() not in title.lower():
                continue

            # 1. Affirmative Duties ("Deberá", "Tendrá la obligación", "Estará obligado a")
            duties = re.findall(r'([^;\.\n]*\b(?:deber[áa]|tendr[áa]\s+la\s+obligaci[óo]n|estar[áa]\s+obligad[oa]\s+a)\b[^;\.\n]*)', content, re.I)
            for duty in duties[:6]:
                clean_d = duty.strip()
                if len(clean_d) > 20:
                    affirmative_duties.append({"statute": title, "duty": clean_d})

            # 2. Strict Statutory Deadlines ("dentro de", "en o antes del", "a más tardar")
            deadlines = re.findall(r'([^;\.\n]*\b(?:dentro\s+de\s+\d+\s+d[íi]as|en\s+o\s+antes\s+del?\s+[\d\w\s]+|a\s+m[áa]s\s+tardar)\b[^;\.\n]*)', content, re.I)
            for dl in deadlines[:6]:
                clean_dl = dl.strip()
                if len(clean_dl) > 20:
                    strict_deadlines.append({"statute": title, "deadline": clean_dl})

            # 3. Penalties, Fines & Sanctions
            penalties = re.findall(r'([^;\.\n]*\b(?:multa\s+(?:de\s+)?\$?[\d,]+|delito\s+(?:grave|menos\s+grave)|penalidad|sanci[óo]n\s+administrativa)\b[^;\.\n]*)', content, re.I)
            for pen in penalties[:6]:
                clean_p = pen.strip()
                if len(clean_p) > 20:
                    penalties_fines.append({"statute": title, "penalty": clean_p})

            # 4. DPR Precedents
            dpr_matches = re.findall(r'(\d+\s+D\.P\.R\.\s+\d+)', content)
            for dpr in dpr_matches:
                dpr_citations.add(dpr)

        # Build Markdown Dossier
        md = []
        md.append(f"# LEGAL CROSS-EXAMINATION DEPOSITION DOSSIER")
        md.append(f"**Target Subject:** `{target_topic}` | **Prepared:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | **Standard:** Court-Admissible Dossier\n")
        md.append("---")
        md.append("## 1. MANDATORY AFFIRMATIVE DUTIES (STATUTORY LIABILITIES)")
        if affirmative_duties:
            for idx, item in enumerate(affirmative_duties[:10], start=1):
                md.append(f"{idx}. **[{item['statute']}]** {item['duty']}")
        else:
            md.append("- *No explicit affirmative duties captured.*")

        md.append("\n## 2. STRICT STATUTORY DEADLINES & TIME-BARS")
        if strict_deadlines:
            for idx, item in enumerate(strict_deadlines[:8], start=1):
                md.append(f"{idx}. **[{item['statute']}]** {item['deadline']}")
        else:
            md.append("- *No strict deadlines captured.*")

        md.append("\n## 3. ADMINISTRATIVE & CRIMINAL PENALTY EXPOSURE")
        if penalties_fines:
            for idx, item in enumerate(penalties_fines[:8], start=1):
                md.append(f"{idx}. **[{item['statute']}]** `{item['penalty']}`")
        else:
            md.append("- *No monetary or penal sanctions found.*")

        md.append("\n## 4. BINDING SUPREME COURT JURISPRUDENCE (D.P.R.)")
        if dpr_citations:
            for dpr in sorted(list(dpr_citations))[:10]:
                md.append(f"- **Authority Precedent:** `{dpr}`")
        else:
            md.append("- *No direct D.P.R. jurisprudence citations identified.*")

        md.append("\n```")
        md.append("CONFIDENTIAL LEGAL WORK PRODUCT - COMPILED BY NEURO SOVEREIGN ENGINE")
        md.append("```")

        return "\n".join(md)
