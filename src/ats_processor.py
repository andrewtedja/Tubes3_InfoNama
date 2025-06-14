import time
import threading

from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from algorithm.kmp import KMP_ATS
from algorithm.bm import BM_ATS
from algorithm.aho import AHO_ATS
from algorithm.fuzzy import FuzzyMatcher
from utils.extract_pdf_match import extract_pdf_for_string_matching

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

    def load_cv(self, cv_path: str):
        """Load CV text content (cleaned long string) from its cv_path"""
        self.cv_text = extract_pdf_for_string_matching(cv_path)

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

    def search_exact(self) -> dict:
        """
        Algo untuk cari exact match
        
        Returns:
            dict: (total_exact, found_exact_keywords)
        """
        # self.keywords = self.parse_keywords(keywords)
        self.exact_results = {}

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

            found_exact_keywords = set(self.exact_results.keys())
            total_exact = sum(res.get('count', 0) for res in self.exact_results.values())
            
            print(f"Total exact matches: {total_exact}")
            
            return (total_exact, found_exact_keywords)
        
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
        total_exact = sum(res.get('count', 0) for res in self.exact_results.values())

        print(f"Total exact matches: {total_exact}")
        return (total_exact, found_exact_keywords)
    
    def search_fuzzy(self, found_exact_keywords) -> dict:
        """Algo untuk cari fuzzy match"""
        # self.keywords = self.parse_keywords(keywords)
        self.fuzzy_results = {}

        for keyword in self.keywords:
            if keyword not in found_exact_keywords:
                fuzzy_count, fuzzy_matches = self.fuzzy.fuzzy_search(keyword, self.cv_text, self.fuzzy.threshold)
                if fuzzy_count > 0:
                    self.fuzzy_results[keyword] = {
                        'count': fuzzy_count,
                        'matches': fuzzy_matches
                    }

        total_fuzzy = sum(res.get('count', 0) for res in self.fuzzy_results.values())

        print(f"Total fuzzy matches: {total_fuzzy}")
        return (total_fuzzy)
    
    def get_top_search_results(self, top_n, keywords_str, cv_dataset):
        """
        Get top_n cv that match keywords_str from cv_dataset with defined algorithm (or fuzzy if not found)

        Args:
            - self
            - top_n: number of top matches result returned
            - keywords_str: keywords to match
            - cv_dataset: JSON of all cv data (including profile and application)
        
        Returns:
            - top_results: List of top_n CVs that match keywords_str with result data to display
            - exact_match_time: Time taken for exact match process
            - fuzzy_match_time: Time taken for fuzzy match process
        """

        # Initialize Time
        exact_start_time = None
        exact_end_time = None
        fuzzy_start_time = None
        fuzzy_end_time = None

        # Store
        all_results = []
        self.keywords = self.parse_keywords(keywords_str)
        found_exact_keywords = []

        # Thread lock for collecting found keywords
        keyword_lock = threading.Lock()
        results_lock = threading.Lock()

        # Exact Match
        # Exact match start time
        exact_start_time = time.time()
        for cv in cv_dataset:
            self.load_cv(cv['cv_path'])
            self.search_exact()
            total_matches = sum(res.get('count', 0) for res in self.exact_results.values())

            if total_matches > 0:
                summary_list = []

                for kw, res in self.exact_results.items():
                    summary_list.append(f"{kw}: {res['count']} (exact)")
                
                # Append formatted result
                all_results.append({
                    'name': cv['first_name'] + " " + cv['last_name'],
                    'match_count': total_matches,
                    'summary': summary_list
                })

            # found_exact_keywords
            for keyword in self.exact_results.keys() :
                if keyword not in found_exact_keywords:
                    found_exact_keywords.append(keyword)
        
        # Exact match end time
        exact_end_time = time.time()
        exact_match_time = exact_end_time - exact_start_time
        
        # Sort exact results
        sorted_exact_results = sorted(all_results, key=lambda x: x['match_count'], reverse=True)

        # Fuzzy Match
        fuzzy_results = []
        fuzzy_match_time = 0
        if (len(all_results) < top_n):
            # Fuzzy match start time
            fuzzy_start_time = time.time()

            # Reset found_exact_keywords if all keywords already found
            if len(self.keywords) <= len(found_exact_keywords):
                found_exact_keywords = []

            for cv in cv_dataset: 
                self.load_cv(cv['cv_path'])
                self.search_fuzzy(found_exact_keywords)
                total_matches = sum(res.get('count', 0) for res in self.fuzzy_results.values())

                if total_matches > 0:
                    summary_list = []
                    
                    for kw, res in self.fuzzy_results.items():
                        unique_phrases = list(set([phrase for similar, phrase in res['matches']]))

                        for phrase in unique_phrases:
                            phrase_count = sum(1 for similar, p in res['matches'] if p == phrase)
                            summary_list.append(f"'{phrase}': {phrase_count} (fuzzy for: {kw})")
                    
                    fuzzy_results.append({
                        'name': cv['first_name'] + " " + cv['last_name'],
                        'match_count': total_matches,
                        'summary': summary_list
                    })
            
            # Fuzzy match end time
            fuzzy_end_time = time.time()
            fuzzy_match_time = fuzzy_end_time - fuzzy_start_time

            # Update sorted_exact_results  
            sorted_fuzzy_results = sorted(fuzzy_results, key=lambda x: x['match_count'], reverse=True)
            remaining_result_count = top_n - len(all_results)
            top_fuzzy_results = sorted_fuzzy_results[:remaining_result_count]
            sorted_exact_results += top_fuzzy_results

        
        # Top results
        top_results = sorted_exact_results[:top_n]
        return (top_results, exact_match_time, fuzzy_match_time)


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
