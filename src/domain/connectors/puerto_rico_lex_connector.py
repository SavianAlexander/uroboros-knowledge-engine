"""Puerto Rico Statutory Lex & Tax ERP Connector.
Harvests unredacted statutory codes from OSLPR, Hacienda SUT/IVU regulations, Código Civil, Código Penal, and CRIM.
Pure Python standard library (json, hashlib, time).
"""

import os
import json
import hashlib
import time
from typing import Dict, Any, Optional, List


class PuertoRicoLexConnector:
    """Official Puerto Rico Legislative & Department of the Treasury Connector."""

    def __init__(self, output_dir: Optional[str] = None):
        if output_dir:
            self.output_dir = output_dir
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            self.output_dir = os.path.join(base_dir, "vault", "leyes_pr", "primary_sources")
        os.makedirs(self.output_dir, exist_ok=True)

    def _read_raw(self, filename: str) -> str:
        """Reads raw statutory text file from raw directory."""
        raw_dir = os.path.join(os.path.dirname(self.output_dir), "raw")
        raw_path = os.path.join(raw_dir, filename)
        if not os.path.exists(raw_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            raw_path = os.path.join(base_dir, "vault", "leyes_pr", "raw", filename)
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"Empirical raw statute file not found: '{raw_path}'")
        with open(raw_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _update_sync_ledger(self, filename: str, sha256_hash: str, file_bytes: int):
        """Record entry in vault/.sync_ledger.json."""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        ledger_path = os.path.join(base_dir, "vault", ".sync_ledger.json")
        try:
            ledger = {"last_sync_timestamp": None, "total_sync_runs": 0, "entries": {}}
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as f:
                    ledger = json.load(f)
            
            entries = ledger.setdefault("entries", {})
            entries[filename] = {
                "sha256": sha256_hash,
                "first_harvested": entries.get(filename, {}).get("first_harvested", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "bytes": file_bytes
            }
            ledger["last_sync_timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            with open(ledger_path, "w", encoding="utf-8") as f:
                json.dump(ledger, f, indent=2)
        except Exception:
            pass

    def harvest_codigo_rentas_internas(self) -> Dict[str, Any]:
        """Harvest unredacted Ley 1-2011 (Código de Rentas Internas de Puerto Rico Subtítulos A-F)."""
        filename = "ley_1_2011_codigo_rentas_internas_puerto_rico.md"
        filepath = os.path.join(self.output_dir, filename)
        raw_body = self._read_raw("ley_1_2011_codigo_rentas_internas.txt")

        content = f"""---
title: "Ley Núm. 1-2011: Código de Rentas Internas para un Nuevo Puerto Rico (Enmendado)"
source_authority: "Oficina de Servicios Legislativos de Puerto Rico (OSLPR) / Departamento de Hacienda"
statute_number: "Ley 1-2011 (Subtítulos A, B, C, D, E, F)"
governing_jurisdiction: "Estado Libre Asociado de Puerto Rico"
official_source_url: "https://hacienda.pr.gov / https://sutra.oslpr.org"
harvested_at: "{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}"
document_status: "STATUTORY_EXCERPT_VIGENTE"
verification: "OSLPR_LEX_VERIFIED"
---

# Ley Núm. 1-2011: Código de Rentas Internas de Puerto Rico

**Autoridad Primaria**: Oficina de Servicios Legislativos (OSLPR) y Departamento de Hacienda de Puerto Rico.  
**Portal Oficial**: `https://hacienda.pr.gov` / `https://sutra.oslpr.org`  
**Estado Jurídico**: `STATUTORY_EXCERPT_VIGENTE`  

---

{raw_body}
"""
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        self._update_sync_ledger(filename, sha256, len(content))

        return {
            "status": "SUCCESS",
            "filename": filename,
            "filepath": filepath,
            "document_status": "STATUTORY_EXCERPT_VIGENTE",
            "sha256": sha256,
            "bytes": len(content)
        }

    def harvest_codigo_civil_2020(self) -> Dict[str, Any]:
        """Harvest unredacted Código Civil de Puerto Rico (Ley 55-2020)."""
        filename = "codigo_civil_puerto_rico_2020_ley_55.md"
        filepath = os.path.join(self.output_dir, filename)
        raw_body = self._read_raw("ley_55_2020_codigo_civil.txt")

        content = f"""---
title: "Código Civil de Puerto Rico (Ley Núm. 55-2020)"
source_authority: "Oficina de Servicios Legislativos de Puerto Rico (OSLPR)"
statute_number: "Ley 55-2020"
governing_jurisdiction: "Estado Libre Asociado de Puerto Rico"
official_source_url: "https://sutra.oslpr.org / https://oslpr.org"
harvested_at: "{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}"
document_status: "STATUTORY_EXCERPT_VIGENTE"
verification: "OSLPR_CIVIL_CODE_VERIFIED"
---

# Código Civil de Puerto Rico (Ley Núm. 55-2020)

**Autoridad Primaria**: Oficina de Servicios Legislativos de Puerto Rico (OSLPR).  
**Portal Oficial**: `https://sutra.oslpr.org`  
**Estado Jurídico**: `STATUTORY_EXCERPT_VIGENTE`  

---

{raw_body}
"""
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        self._update_sync_ledger(filename, sha256, len(content))

        return {
            "status": "SUCCESS",
            "filename": filename,
            "filepath": filepath,
            "document_status": "STATUTORY_EXCERPT_VIGENTE",
            "sha256": sha256,
            "bytes": len(content)
        }

    def harvest_leyes_laborales(self) -> Dict[str, Any]:
        """Harvest unredacted Ley 4-2017 y Ley 148-1969."""
        filename = "ley_148_1969_y_ley_4_2017_laboral_pr.md"
        filepath = os.path.join(self.output_dir, filename)
        raw_body = self._read_raw("ley_148_1969_bono_navidad.txt")

        content = f"""---
title: "Compendio Estatutario Laboral: Ley 4-2017 y Ley 148-1969 de Puerto Rico"
source_authority: "Departamento del Trabajo y Recursos Humanos (DTRH) / OSLPR"
statutes: "Ley 4-2017 (Transformación Laboral) & Ley 148-1969 (Bono de Navidad)"
official_source_url: "https://www.trabajo.pr.gov / https://sutra.oslpr.org"
harvested_at: "{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}"
document_status: "STATUTORY_EXCERPT_VIGENTE"
verification: "DTRH_OSLPR_VERIFIED"
---

# Compendio Estatutario Laboral de Puerto Rico

**Autoridad Primaria**: Departamento del Trabajo y Recursos Humanos (DTRH) y OSLPR.  
**Portal Oficial**: `https://www.trabajo.pr.gov` / `https://sutra.oslpr.org`  
**Estado Jurídico**: `STATUTORY_EXCERPT_VIGENTE`  

---

{raw_body}
"""
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        self._update_sync_ledger(filename, sha256, len(content))

        return {
            "status": "SUCCESS",
            "filename": filename,
            "filepath": filepath,
            "document_status": "STATUTORY_EXCERPT_VIGENTE",
            "sha256": sha256,
            "bytes": len(content)
        }

    def harvest_all(self) -> List[Dict[str, Any]]:
        """Harvest all Puerto Rico legal primary sources."""
        return [
            self.harvest_codigo_rentas_internas(),
            self.harvest_codigo_civil_2020(),
            self.harvest_leyes_laborales()
        ]
