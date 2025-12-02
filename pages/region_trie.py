# ============================
# TRIE NODE
# ============================
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.items = []
        self.score = 0


# ============================
# TRIE UTAMA
# ============================
class RegionTrie:
    def __init__(self):
        self.root = TrieNode()   # <-- BAGIAN PENTING YANG HILANG DI FILE LAMA

    def insert(self, word, item=None, score=0):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_end = True
        if item:
            node.items.append(item)
        node.score = score

    def suggest(self, prefix, k=10):
        node = self.root
        prefix = prefix.lower()

        # temukan node prefix
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        results = []

        def dfs(n):
            if len(results) >= k:
                return
            if n.is_end:
                results.extend(n.items)
            for child in n.children.values():
                dfs(child)

        dfs(node)
        return results[:k]


# ============================
# CSV UTILITY
# ============================
import csv

def load_regions_from_csv(path):
    regions = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            regions.append({
                "name": row["name"],
                "code": row["code"],
                "type": row["type"]
            })
    return regions


def build_breadcrumbs(regions):
    for r in regions:
        r["display_label"] = r["name"]


def build_trie_from_regions(regions):
    trie = RegionTrie()
    for item in regions:
        trie.insert(item["name"], item=item, score=1)
    return trie
