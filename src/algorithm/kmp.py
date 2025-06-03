from fuzzy import fuzzy_search

class KMP_ATS:
    def __init__(self):
        self.cv_text = ""
        self.keywords = []
        self.exact_results = {}
        self.fuzzy_results = {}
        self.threshold = 0.65
        
    def compute_lps(self, pattern):
        """
        Menghitung tabel LPS (Longest Proper Prefix)
        untuk pattern yang diberikan
        """
        m = len(pattern)
        lps = [0] * m
        length = 0  # panjang prefix terpanjang sebelumnya
        i = 1
        
        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        
        return lps
    
    def kmp_search(self, text, pattern):
        """
        Implementasi algoritma KMP untuk mencari semua kemunculan
        pattern dalam text
        """
        n = len(text)
        m = len(pattern)
        
        if m == 0:
            return 0
        
        # Compute LPS array
        lps = self.compute_lps(pattern)
        
        count = 0  # jumlah kecocokan
        i = 0  # index text
        j = 0  # index pattern
        
        while i < n:
            if text[i] == pattern[j]:
                i += 1
                j += 1
            
            if j == m:
                # Pattern found
                count += 1
                j = lps[j - 1]
            elif i < n and text[i] != pattern[j]:
                # Mismatch
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        
        return count
    
    def process_cv(self, cv_text):
        """
        Konversi cv ke lowercase untuk case-insensitive search
        """
        self.cv_text = cv_text.lower()
    
    def search_keywords(self, keywords):
        """
        Mencari semua kata kunci dalam CV dengan algoritma KMP
        """
        self.keywords = [keyword.lower() for keyword in keywords]
        self.exact_results = {}
        self.fuzzy_results = {}

        total_exact_matches = 0
        total_fuzzy_matches = 0
        
        print("======= EXACT MATCHING (KMP) =======")
        for keyword in self.keywords:
            print(f'\nFinding: "{keyword}"')

            exact_matches = self.kmp_search(self.cv_text, keyword)
            self.exact_results[keyword] = exact_matches
            print(f"[DEBUG] exact_matches for '{keyword}': {exact_matches}") # DEBUG


            total_exact_matches += exact_matches

            # FUZZY MATCH if exact match not found
            if (exact_matches == 0):
                print("\n======= FUZZY MATCHING (KMP) =======\n")
                print(f'Trying fuzzy matching for "${keyword}"')
                fuzzy_count, fuzzy_matches = fuzzy_search(keyword, self.cv_text, self.threshold)

                self.fuzzy_results[keyword] = {
                    'count': fuzzy_count,
                    'matches': fuzzy_matches
                }
                total_fuzzy_matches += fuzzy_count

                if fuzzy_matches:
                    print(f'Fuzzy matches ditemukan: {fuzzy_matches}')
                else:
                    print(f'Tidak ada fuzzy matches yang memenuhi threshold {self.threshold}')

        return total_exact_matches, total_fuzzy_matches, self.exact_results, self.fuzzy_results
    
    def display_results(self):
        """
        Menampilkan hasil pencarian
        """

        total_exact = sum(self.exact_results.values())
        print(f"\n[EXACT] Terdapat total {total_exact} kesamaan")

        if self.fuzzy_results:
            total_fuzzy = sum([result['count'] for result in self.fuzzy_results.values()])
            print(f"\n [FUZZY] Matches: {total_fuzzy} total")

            for keyword, result in self.fuzzy_results.items():
                if result['matches']:
                    print(f'  "{keyword}": {result["count"]} matches')
                    for match in result['matches']:
                        print(f'    - {match}')


        print(f"\nTOTAL MATCHES: {total_exact + sum([result['count'] for result in self.fuzzy_results.values()])}")

def main():
    # Example use
    ats = KMP_ATS()
    
    cv_text = """React, React N4tive American, MySQQL"""
    
    ats.process_cv(cv_text)
    
    user_input = input("\nKata kunci (pisah dengan koma): ")
    keywords = [keyword.strip() for keyword in user_input.split(',')]
    
    
    ats.search_keywords(keywords)
    ats.display_results()

if __name__ == "__main__":
    main()