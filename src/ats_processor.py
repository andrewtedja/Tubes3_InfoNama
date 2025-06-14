from algorithm.kmp import KMP_ATS
from algorithm.bm import BM_ATS
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

    def set_algorithm(self, algo_name: str):
        """Ubah algoritma pencocokan exact (KMP / BM)"""
        if algo_name in ["KMP", "BM"]:
            self.algorithm = algo_name.upper()
        else:
            print(f"Algorithm '{algo_name}' not recognized. Defaulting to KMP.")
            self.algorithm = "KMP"

    def load_cv(self, cv_text: str):
        """Normalize cv text jadi lowercase without awal and end space"""
        self.cv_text = cv_text.strip().lower() if cv_text else ""

    def parse_keywords(self, raw_input):
        """Split by comma, strip spaces, drop empties"""
        if isinstance(raw_input, str):
            return [k.strip().lower() for k in raw_input.split(",") if k.strip()]
        elif isinstance(raw_input, list):
            return [k.strip().lower() for k in raw_input if isinstance(k, str) and k.strip()]
        else:
            return []

    def search_keywords(self, keywords):
        """Algonya untuk cari exact match dan kalau gabisa -> fuzzy match"""
        self.keywords = self.parse_keywords(keywords)
        self.exact_results = {}
        self.fuzzy_results = {}

        total_exact = 0
        total_fuzzy = 0

        for keyword in self.keywords:
            if self.algorithm == "BM":
                exact = self.bm.bm_search(self.cv_text, keyword)
            else:
                exact = self.kmp.kmp_search(self.cv_text, keyword)

            self.exact_results[keyword] = exact
            total_exact += exact

            if exact == 0:
                fuzzy_count, fuzzy_matches = self.fuzzy.fuzzy_search(keyword, self.cv_text, self.fuzzy.threshold)

                self.fuzzy_results[keyword] = {
                    'count': fuzzy_count,
                    'matches': fuzzy_matches
                }
                total_fuzzy += fuzzy_count

                if fuzzy_matches:
                    print(f'Fuzzy matches ditemukan: {fuzzy_matches}')
                else:
                    print(f'Tidak ada fuzzy matches yang memenuhi threshold')

        return total_exact, total_fuzzy


    def print_results(self):
        """Display exact and fuzzy results"""
        total_exact = sum(self.exact_results.values())
        total_fuzzy = sum(res['count'] for res in self.fuzzy_results.values())

        print(f"\n[EXACT MATCHES] Total: {total_exact}")
        for kw, count in self.exact_results.items():
            if count > 0:
                print(f'  - "{kw}": {count} match(es)')

        if total_fuzzy > 0:
            print(f"\n[FUZZY MATCHES] Total: {total_fuzzy}")
            for kw, res in self.fuzzy_results.items():
                if res['matches']:
                    print(f'  - "{kw}": {res["count"]} fuzzy match(es)')
                    for sim, phrase in res['matches']:
                        print(f'    - "{phrase}" (similarity: {sim:.3f})')
        
        print("\n" + "=" * 50)
        print(f"TOTAL MATCHES: {total_exact + total_fuzzy}")

        

# ========== Example Use ==========

if __name__ == "__main__":
    cv_text = """
    react native american developer backend engineer skilled in python and sql
    """

    print("Available algorithms: KMP, BM")
    selected_algo = input("Choose algorithm (KMP/BM): ").strip().upper()
    if selected_algo not in ["KMP", "BM"]:
        print("Invalid choice. Defaulting to KMP.")
        selected_algo = "KMP"

    processor = ATSProcessor(fuzzy_threshold=0.65, algorithm=selected_algo)
    processor.load_cv(cv_text)

    keywords = input("Enter keywords (comma-separated): ")
    total_exact, total_fuzzy = processor.search_keywords(keywords)

    print(f"\nAlgorithm used: {selected_algo}")
    print(f"Inputted keywords: {keywords}")
    processor.print_results()
