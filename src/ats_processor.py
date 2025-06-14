from algorithm.kmp import KMP_ATS
from algorithm.bm import BM_ATS
from algorithm.aho import AHO_ATS
from algorithm.fuzzy import FuzzyMatcher

class ATSProcessor:
    def __init__(self, fuzzy_threshold=0.65, algorithm="KMP"):
        self.kmp = KMP_ATS()
        self.bm = BM_ATS()
        self.fuzzy = FuzzyMatcher(fuzzy_threshold)
        self.cv_text = ""
        self.algorithm = algorithm
        self.keywords = []
        self.exact_results = {}
        self.fuzzy_results = {}

    # ======================== HELPERS ========================

    def set_algorithm(self, algo_name: str):
        """Ubah algoritma pencocokan exact (KMP / BM/ Aho-Corasick)"""
        if algo_name in ["KMP", "BM", "Aho-Corasick"]:
            self.algorithm = algo_name.upper()
        else:
            print(f"Algorithm '{algo_name}' not recognized. Defaulting to KMP.")
            self.algorithm = "KMP"

    def load_cv(self, cv_text: str):
        """Normalize cv text jadi lowercase without awal and end space"""
        self.cv_text = cv_text.strip().lower() if cv_text else ""

    def parse_keywords(self, raw_input: str) -> list:
        """
            Split by comma, strip spaces, drop empties
            -> returns list of parsed strings lowercased
        """
        if isinstance(raw_input, str):
            return [k.strip().lower() for k in raw_input.split(",") if k.strip()]
        elif isinstance(raw_input, list):
            return [k.strip().lower() for k in raw_input if isinstance(k, str) and k.strip()]
        else:
            return []
        
    def print_results(self):
        """Display exact and fuzzy results"""
        total_exact = sum(res['count'] for res in self.exact_results.values())
        total_fuzzy = sum(res['count'] for res in self.fuzzy_results.values())

        print(f"\n[EXACT MATCHES] Total: {total_exact}")
        for kw, res in self.exact_results.items():
            count = res['count']
            if count > 0:
                print(f'  - "{kw}": {count} match(es)')

        if total_fuzzy > 0:
            print(f"\n[FUZZY MATCHES] Total: {total_fuzzy}")
            for kw, res in self.fuzzy_results.items():
                if res['matches']:
                    print(f'  - For keyword "{kw}": {res["count"]} fuzzy match(es)')
                    # Menampilkan frasa yang cocok dari CV
                    unique_phrases = list(set([phrase for sim, phrase in res['matches']]))
                    for phrase in unique_phrases:
                        print(f'    - "{phrase}"')
        
        print("\n" + "=" * 50)
        print(f"TOTAL MATCHES: {total_exact + total_fuzzy}")


    # ======================== SEARCH ========================

    def search_keywords(self, keywords: str) -> dict:
        """Algonya untuk cari exact match dan kalau gabisa -> fuzzy match"""
        self.keywords = self.parse_keywords(keywords)
        self.exact_results = {}
        self.fuzzy_results = {}

        # AHO
        if self.algorithm == "Aho-Corasick":
            if not self.keywords: 
                return (0, 0)
            
            aho_instance = AHO_ATS(self.keywords)
            found_matches = aho_instance.search_words(self.cv_text)
            for keyword in self.keywords:
                indices = found_matches.get(keyword, [])
                if indices:
                    self.exact_results[keyword] = {
                        'count': len(indices), 
                        'matches': [keyword] * len(indices)
                    }

            # FUZZY
            found_exact_keywords = set(self.exact_results.keys())
            for keyword in self.keywords:
                if keyword not in found_exact_keywords:
                    fuzzy_count, fuzzy_matches = self.fuzzy.fuzzy_search(keyword, self.cv_text, self.fuzzy.threshold)
                    if fuzzy_count > 0:
                        self.fuzzy_results[keyword] = {
                            'count': fuzzy_count,
                            'matches': fuzzy_matches
                        }

            # Calculate totals
            total_exact = sum(res.get('count', 0) for res in self.exact_results.values())
            total_fuzzy = sum(res.get('count', 0) for res in self.fuzzy_results.values())
            
            print(f"Total exact matches: {total_exact}")
            print(f"Total fuzzy matches: {total_fuzzy}")
            
            return (total_exact, total_fuzzy)
        
        # KMP/BM
        else: 
            for keyword in self.keywords:
                indexes = []

                if self.algorithm == "BM":
                    indexes = self.bm.bm_search(self.cv_text, keyword)
                else:
                    indexes = self.kmp.kmp_search(self.cv_text, keyword)

                count = len(indexes)
                if count > 0:
                    self.exact_results[keyword] = {
                        'count': count,
                        'matches': [keyword] * count
                    }

        # simpen exact match
        found_exact_keywords = self.exact_results.keys()

        # ========================== FUZZY MATCH ==========================

        for keyword in self.keywords:
            if keyword not in found_exact_keywords:
                fuzzy_count, fuzzy_matches = self.fuzzy.fuzzy_search(keyword, self.cv_text, self.fuzzy.threshold)
                if fuzzy_count > 0:
                    self.fuzzy_results[keyword] = {
                        'count': fuzzy_count,
                        'matches': fuzzy_matches
                    }

        total_exact = sum(res.get('count', 0) for res in self.exact_results.values())
        total_fuzzy = sum(res.get('count', 0) for res in self.fuzzy_results.values())

        print(f"Total exact matches: {total_exact}")
        print(f"Total fuzzy matches: {total_fuzzy}")
        return (total_exact, total_fuzzy)


# ========== Example Use ==========

if __name__ == "__main__":
    cv_text = """
    ahishers react native amErican
    """

    print("Available algorithms: KMP, BM, AHO")
    selected_algo = input("Choose algorithm (KMP/BM/AHO (Aho-Corasick)): ").strip().upper()

    # TEMP FIX
    if selected_algo == "AHO":
        selected_algo = "Aho-Corasick"

    if selected_algo not in ["KMP", "BM", "Aho-Corasick"]:
        print("Invalid choice. Defaulting to KMP.")
        selected_algo = "KMP"

    processor = ATSProcessor(fuzzy_threshold=0.65, algorithm=selected_algo)
    processor.load_cv(cv_text)

    keywords = input("Enter keywords (comma-separated): ")
    total_exact, total_fuzzy = processor.search_keywords(keywords)

    print(f"\nAlgorithm used: {selected_algo}")

    print(f"Inputted keywords: {keywords}")
    processor.print_results()
