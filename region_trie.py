import os, inspect
import re
import csv
import heapq
from typing import Dict, Any, Optional, List

def tidy_name(name: str) -> str:
    """
    Rapikan kapitalisasi ringan untuk tampilan (opsional).
    """
    if name.isupper():
        return name
    titled = " ".join(w.capitalize() if w not in {"di", "ke", "dan"} else w for w in name.split())
    return titled

def normalize(text: str) -> str:
    """
    Normalisasi teks untuk pencarian: lowercase dan hapus karakter non-alfanumerik.
    """
    if not text:
        return ""
    normalized = text.lower()
    normalized = re.sub(r'[^a-z0-9.\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

# ================== INFER STRUKTUR WILAYAH ==================

def infer_level_and_type(code: str, raw_name: str) -> Dict[str, Any]:
    """
    Tentukan level & tipe wilayah dari kode + nama.
    Level: 1=Provinsi, 2=Kab/Kota, 3=Kecamatan, 4+=Desa/Kelurahan (atau sebutan lokal).
    """
    segs = code.split(".")
    level = len(segs)

    if level == 1:
        wtype = "Provinsi"
    elif level == 2:
        upper = raw_name.upper()
        if "KOTA" in upper:
            wtype = "Kota"
        elif "KAB" in upper:  # KAB. atau KABUPATEN
            wtype = "Kabupaten"
        else:
            wtype = "Kabupaten/Kota"
    elif level == 3:
        wtype = "Kecamatan"
    else:
        upper = raw_name.upper()
        if "GAMPONG" in upper:
            wtype = "Gampong"
        elif "NAGARI" in upper:
            wtype = "Nagari"
        elif "KELURAHAN" in upper:
            wtype = "Kelurahan"
        elif "DESA" in upper:
            wtype = "Desa"
        elif "KAMPUNG" in upper:
            wtype = "Kampung"
        else:
            wtype = "Desa/Kelurahan"

    return {"level": level, "type": wtype}

def parent_code(code: str) -> Optional[str]:
    segs = code.split(".")
    return ".".join(segs[:-1]) if len(segs) > 1 else None

# ================== ALIAS NAMA ==================

def generate_aliases(display_name: str, wtype: str) -> List[str]:  
    """
    Buat alias umum untuk variasi penulisan: KAB. → Kabupaten, KEC. → Kecamatan, dst.
    """
    aliases = set()
    original = display_name.strip()
    aliases.add(original)

    upper = original.upper()

    # KAB.
    if upper.startswith("KAB.") or upper.startswith("KAB "):
        cleaned = re.sub(r"^KAB[.\s]+", "", original, flags=re.IGNORECASE).strip()
        aliases.add(f"Kabupaten {cleaned}")
        aliases.add(f"Kab. {cleaned}")

    # KOTA
    if upper.startswith("KOTA "):
        cleaned = re.sub(r"^KOTA[.\s]+", "", original, flags=re.IGNORECASE).strip()
        aliases.add(f"Kota {cleaned}")

    # KEC.
    if upper.startswith("KEC.") or upper.startswith("KECAMATAN"):
        cleaned = re.sub(r"^(KEC[.\s]+|KECAMATAN[.\s]+)", "", original, flags=re.IGNORECASE).strip()
        aliases.add(f"Kecamatan {cleaned}")
        aliases.add(f"Kec. {cleaned}")

    # Gampong/Nagari/Kampung → variasi umum
    if "GAMPONG" in upper:
        cleaned = re.sub(r"^GAMPONG[.\s]+", "", original, flags=re.IGNORECASE).strip()
        aliases.add(f"Desa {cleaned}")
        aliases.add(f"Kelurahan {cleaned}")
    if "NAGARI" in upper:
        cleaned = re.sub(r"^NAGARI[.\s]+", "", original, flags=re.IGNORECASE).strip()
        aliases.add(f"Desa {cleaned}")
    if "KAMPUNG" in upper:
        cleaned = re.sub(r"^KAMPUNG[.\s]+", "", original, flags=re.IGNORECASE).strip()
        aliases.add(f"Desa {cleaned}")

    # Tipe + nama (umum)
    if wtype in {"Kabupaten", "Kota", "Kecamatan"} and not upper.startswith(wtype.upper()):
        aliases.add(f"{wtype} {original}")

    return sorted(aliases)

# ================== TRIE ==================

class TrieNode:
    _slots_ = ("children", "items", "top_suggestions")  

    def _init_(self):  
        self.children: Dict[str, "TrieNode"] = {}
        self.items: List[Dict[str, Any]] = []
        self.top_suggestions: List[tuple] = []  # min-heap (score, uid, item)

class RegionTrie:
    def _init_(self, k_per_node: int = 10):  
        self.root = RegionTrieNode()
        self.k_per_node = k_per_node
        self._uid = 0

    def _push_topk(self, node: TrieNode, score: float, uid: int, item: Dict[str, Any]):
        heapq.heappush(node.top_suggestions, (score, uid, item))
        if len(node.top_suggestions) > self.k_per_node:
            heapq.heappop(node.top_suggestions)

    def insert(self, key_name: str, item: Dict[str, Any], score: float = 1.0):
        """
        Masukkan satu key ke Trie (key_name adalah string yang akan dicari user).
        item: dict metadata {code, name, display_label, type, level, ...}
        """
        norm = normalize(key_name)  
        node = self.root
        self._uid += 1
        uid = self._uid

        for ch in norm:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
            self._push_topk(node, score, uid, item)

        node.items.append(item)

    def suggest(self, prefix: str, k: int = 10) -> List[Dict[str, Any]]:
        norm = normalize(prefix)  
        node = self.root
        for ch in norm:
            if ch not in node.children:
                return []
            node = node.children[ch]

        suggestions = sorted(node.top_suggestions, key=lambda x: (x[0], x[1]), reverse=True)
        result, seen = [], set()
        for score, uid, item in suggestions:
            code = item.get("code")
            if code in seen:
                continue
            seen.add(code)
            result.append(item)
            if len(result) >= k:
                break
        return result

# ================== LOADER CSV + BUILD TRIE ==================

def load_regions_from_csv(csv_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Baca CSV 'kode_wilayah.csv' → dict {code: item}
    Item: code, name, type, level, parent_code
    """
    regions: Dict[str, Dict[str, Any]] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["kode"].strip()
            raw_name = row["nama"].strip()
            info = infer_level_and_type(code, raw_name)
            regions[code] = {
                "code": code,
                "name": tidy_name(raw_name),
                "type": info["type"],
                "level": info["level"],
                "parent_code": parent_code(code),
            }
    return regions

def build_breadcrumbs(regions: Dict[str, Dict[str, Any]]) -> None:
    """
    Tambahkan breadcrumb (rantai parent) dan display_label informatif untuk setiap item.
    """
    cache_path: Dict[str, List[Dict[str, Any]]] = {}

    def resolve_path(code: str) -> List[Dict[str, Any]]:
        if code in cache_path:
            return cache_path[code]
        path = []
        cur = regions.get(code)
        while cur:
            path.append(cur)
            pcode = cur.get("parent_code")
            cur = regions.get(pcode) if pcode else None
        cache_path[code] = path
        return path

    for code, item in regions.items():
        path = resolve_path(code)
        labels = []
        for node in path:
            t, n = node["type"], node["name"]
            if t == "Provinsi":
                labels.append(n)
            elif t == "Kabupaten":
                labels.append(f"Kab. {n.replace('Kabupaten ', '')}")
            elif t == "Kota":
                labels.append(f"Kota {n.replace('Kota ', '')}")
            elif t == "Kecamatan":
                labels.append(f"Kec. {n.replace('Kecamatan ', '')}")
            else:
                labels.append(n)
        display = ", ".join(labels)
        item["display_label"] = display
        item["path"] = list(reversed(path))  # provinsi → ... → item

def build_trie_from_regions(regions: Dict[str, Dict[str, Any]], k_per_node: int = 10) -> RegionTrie:
    """
    Bangun Trie dari dict regions, termasuk alias untuk variasi penulisan.
    Skor: provinsi (level=1) > kab/kota (2) > kecamatan (3) > desa (4+).
    """
    trie = RegionTrie()
    for code, item in regions.items():
        name = item["name"]
        wtype = item["type"]
        level = item["level"]
        base_score = 100 - (level - 1) * 10

        # Nama utama + label breadcrumb
        trie.insert(name, item=item, score=base_score)
        trie.insert(item["display_label"], item=item, score=base_score + 1)

        # Alias
        for alias in generate_aliases(name, wtype):
            trie.insert(alias, item=item, score=base_score - 1)

    return trie