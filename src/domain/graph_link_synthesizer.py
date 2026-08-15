"""
Knowledge Graph Self-Healing & Wikilink Synthesizer.
Scans unlinked concept nodes across raw vault files and automatically inserts missing semantic [[wikilinks]].
Zero-dependency, stdlib implementation.
"""
import re
import unicodedata
from collections import deque
from typing import Dict, Any, List, Set, Optional, Tuple


class AhoCorasickNode:
    __slots__ = ('children', 'fail', 'outputs')
    
    def __init__(self):
        self.children: Dict[str, 'AhoCorasickNode'] = {}
        self.fail: Optional['AhoCorasickNode'] = None
        self.outputs: List[str] = []


class AhoCorasickAutomaton:
    """
    Zero-dependency stdlib Aho-Corasick multi-pattern search automaton.
    Provides linear O(N) text search time across 100,000+ concept titles.
    """
    def __init__(self, patterns: List[str]):
        self.root = AhoCorasickNode()
        self._build_trie(patterns)
        self._build_failure_links()

    def _build_trie(self, patterns: List[str]):
        for pattern in patterns:
            norm_p = unicodedata.normalize("NFC", str(pattern)).strip()
            if len(norm_p) < 3:
                continue
            curr = self.root
            for ch in norm_p.lower():
                if ch not in curr.children:
                    curr.children[ch] = AhoCorasickNode()
                curr = curr.children[ch]
            curr.outputs.append(norm_p)

    def _build_failure_links(self):
        queue = deque()
        for ch, child in self.root.children.items():
            child.fail = self.root
            queue.append(child)

        while queue:
            curr = queue.popleft()
            for ch, child in curr.children.items():
                fail_node = curr.fail
                while fail_node is not None and ch not in fail_node.children:
                    fail_node = fail_node.fail
                
                child.fail = fail_node.children[ch] if fail_node else self.root
                if child.fail and child.fail.outputs:
                    child.outputs.extend(child.fail.outputs)
                queue.append(child)

    def search_in_text(self, text: str) -> List[Tuple[int, int, str]]:
        """
        Finds all (start_idx, end_idx, original_title) matches in text.
        """
        matches = []
        curr = self.root
        lower_text = text.lower()

        for idx, ch in enumerate(lower_text):
            while curr is not None and ch not in curr.children:
                curr = curr.fail
            
            if curr is None:
                curr = self.root
                continue
            
            curr = curr.children[ch]
            if curr.outputs:
                for pattern in curr.outputs:
                    start_idx = idx - len(pattern) + 1
                    end_idx = idx + 1
                    matches.append((start_idx, end_idx, pattern))

        return matches


def auto_synthesize_wikilinks(text_content: str, known_doc_titles: List[str]) -> Dict[str, Any]:
    """
    Scans text_content for unlinked occurrences of known_doc_titles and synthesizes [[wikilinks]].
    # ponytail: Aho-Corasick multi-pattern automaton; ceiling: linear O(N) vault scan; upgrade: persist compiled trie cache if title count exceeds 1,000,000
    """
    if not text_content or not known_doc_titles:
        return {"status": "clean", "synthesized_text": text_content, "links_added": 0}

    synthesized = unicodedata.normalize("NFC", str(text_content))
    valid_titles = [str(t).strip() for t in (known_doc_titles or []) if t is not None and len(str(t).strip()) >= 3]
    if not valid_titles:
        return {"status": "clean", "synthesized_text": synthesized, "links_added": 0}

    # Find ranges already inside [[wikilinks]]
    existing_link_ranges: List[Tuple[int, int]] = []
    for m in re.finditer(r'\[\[(.*?)\]\]', synthesized):
        existing_link_ranges.append((m.start(), m.end()))

    def is_inside_existing_link(start: int, end: int) -> bool:
        for ex_s, ex_e in existing_link_ranges:
            if not (end <= ex_s or start >= ex_e):
                return True
        return False

    def is_word_boundary(start: int, end: int, text: str) -> bool:
        if start > 0 and (text[start - 1].isalnum() or text[start - 1] == '_'):
            return False
        if end < len(text) and (text[end].isalnum() or text[end] == '_'):
            return False
        return True

    automaton = AhoCorasickAutomaton(valid_titles)
    raw_matches = automaton.search_in_text(synthesized)

    # Filter matches for valid word boundaries and not already linked
    valid_matches = []
    for start_idx, end_idx, matched_title in raw_matches:
        if is_inside_existing_link(start_idx, end_idx):
            continue
        if not is_word_boundary(start_idx, end_idx, synthesized):
            continue
        valid_matches.append((start_idx, end_idx, matched_title, len(matched_title)))

    # Sort valid matches: prefer longer matches, then by start position
    valid_matches.sort(key=lambda x: (-x[3], x[0]))

    # Non-overlapping interval selection (greedy longest first)
    selected_matches: List[Tuple[int, int, str]] = []
    occupied_spans: List[Tuple[int, int]] = list(existing_link_ranges)

    for start_idx, end_idx, title, _ in valid_matches:
        collision = False
        for occ_s, occ_e in occupied_spans:
            if not (end_idx <= occ_s or start_idx >= occ_e):
                collision = True
                break
        if not collision:
            selected_matches.append((start_idx, end_idx, title))
            occupied_spans.append((start_idx, end_idx))

    # Sort selected intervals descending by start_idx for safe right-to-left substitution
    selected_matches.sort(key=lambda x: x[0], reverse=True)

    links_added = len(selected_matches)
    added_titles: List[str] = []
    text_chars = list(synthesized)

    for start_idx, end_idx, title in selected_matches:
        original_text_slice = "".join(text_chars[start_idx:end_idx])
        replacement = f"[[{original_text_slice}]]"
        text_chars[start_idx:end_idx] = list(replacement)
        added_titles.append(title)

    result_text = "".join(text_chars)

    return {
        "status": "success",
        "original_char_count": len(text_content),
        "links_added": links_added,
        "synthesized_titles": added_titles,
        "synthesized_text": result_text
    }

