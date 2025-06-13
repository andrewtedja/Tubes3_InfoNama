
class KMP_ATS:
    def __init__(self):
        pass
        
    def compute_lps(self, pattern) -> list:
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
    
    def kmp_search(self, text, pattern) -> list:
        """
        Implementasi algoritma KMP untuk mencari semua kemunculan
        pattern dalam text
        """
        if not pattern:
            return 0

        n = len(text)
        m = len(pattern)
        
        if m == 0:
            return 0
        
        # Compute LPS array
        lps = self.compute_lps(pattern)


        found_indexes = []
        i = 0  # index text
        j = 0  # index pattern
        
        while i < n:
            if text[i] == pattern[j]:
                i += 1
                j += 1
            
            if j == m:
                # Pattern found
                start_index = i - j
                found_indexes.append(start_index)
                j = lps[j - 1]
            elif i < n and text[i] != pattern[j]:
                # Mismatch
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        
        return found_indexes
    
    
    # def search_keywords(self, keywords):
    #     """
    #     Mencari semua kata kunci dalam CV dengan algoritma KMP
    #     """
    #     self.keywords = [keyword.lower() for keyword in keywords]
    #     self.exact_results = {}
    #     self.fuzzy_results = {}

    #     total_exact_matches = 0
    #     total_fuzzy_matches = 0
        
    #     print("======= EXACT MATCHING (KMP) =======")
    #     for keyword in self.keywords:
    #         print(f'\nFinding: "{keyword}"')

    #         exact_matches = self.kmp_search(self.cv_text, keyword)
    #         self.exact_results[keyword] = exact_matches
    #         print(f"[DEBUG] exact_matches for '{keyword}': {exact_matches}") # DEBUG


    #         total_exact_matches += exact_matches

    #         # FUZZY MATCH if exact match not found
    #         if (exact_matches == 0):
    #             print("\n======= FUZZY MATCHING (KMP) =======\n")
    #             print(f'Trying fuzzy matching for "${keyword}"')
    #             fuzzy_count, fuzzy_matches = fuzzy_search(keyword, self.cv_text, self.threshold)

    #             self.fuzzy_results[keyword] = {
    #                 'count': fuzzy_count,
    #                 'matches': fuzzy_matches
    #             }
    #             total_fuzzy_matches += fuzzy_count

    #             if fuzzy_matches:
    #                 print(f'Fuzzy matches ditemukan: {fuzzy_matches}')
    #             else:
    #                 print(f'Tidak ada fuzzy matches yang memenuhi threshold {self.threshold}')

    #     return total_exact_matches, total_fuzzy_matches, self.exact_results, self.fuzzy_results
    


def main():
    # Example use
    ats = KMP_ATS()
    
    cv_text = """food prep chef skills highly skilled in cooking and preparing a variety of cuisines inborn ability to explore new cooking avenues thorough understanding of sanitation needs of the kitchen operate kitchen equipment such as ovens and grills for cooking purposes maintain knowledge of all recipes so that the head chefs place can be filled in effectively in case of absenteeism summary exceptional culinary insight. knowledge of standard food preparation ability to work in a high volume environment chef in preparing exceptional meals motivated food serving professional with 5+ years food and beverage experience in casual and fine dining. highlights kitchen productivity basic knife skills uses proper sanitation practices able to regularly liftmove up to 25-50 lbs preparation of various food items good personal hygiene team-oriented well groomed high level of cleanly kitchen maintenance team-oriented accomplishments sandwich preparation experience knowledge of basic food preparation food handling knowledge italian cuisine american cuisine ethnic foods preparation plate presentation skills banquet operations and off-site catering expert serve safe 2015 seasoned and cooked food according to recipes or personal judgment and experience. ensured consistent high quality of plate presentation. maintained contact with kitchen staff, management, serving staff and customers. baked, roasted, broiled, and steamed meats, fish, vegetables and other foods. supported all kitchen operations when chef was absent. experience 092010 - 042011 company name city , state food prep chef followed all established restaurant practices and procedures. carefully maintained sanitation, health and safety standards in all work areas. prepared items according to written or verbal orders, working on several different orders simultaneously. 062011 - 112012 company name city , state cook followed all established restaurant practices and procedures. maintained a neat, well groomed appearance including impeccable personal hygiene, hair restraint and minimal jewelry that met company standards. closely followed standard procedures for safe food preparation, assembly and presentation to ensure customer satisfaction. cut and chopped food items and cooked on a grill or in fryers. 122012 - 032013 company name city , state cook operated large-volume cooking equipment such as grills, deep-fat fryers and griddles. took necessary steps to meet customer needs and effectively resolve food or service issues. served fresh, hot food with a smile in a timely manner. accurately measured ingredients required for specific food items. followed all established restaurant practices and procedures. 022013 - 062013 company name city , state cook assisted co-workers. assisted co-workers. cooked food properly and in a timely fashion, using safety precautions weighed, measured, and mixed ingredients according to recipes using various kitchen utensils and equipment cleaned and prepared various foods for cooking or serving 062014 - 112014 company name city , state chef developed strategies to enhance catering and retail food service revenue and productivity goals. prepared healthy, enjoyable breakfasts and dinners for diners. effectively managed and assisted kitchen staff in producing food for banquets, catered events and member dining areas. effectively used items in stock to decrease waste and profit loss. ensured consistent high quality of plate presentation seasoned and cooked food according to recipes or personal judgment and experience created and explored new cuisines instructed cooks and other workers in the preparation, cooking, garnishing, and presentation of food cooked food properly and in a timely fashion, using safety precautions used all food handling standards 012014 - 122014 company name city , state food service cook temp assisted co-workers. performed kitchen maintenance for a private facility. responsible for daily set up of five stations. stocked and rotated products, stocked supplies, and paper goods in a timely basis stored clean equipment and utensils supervised and coordinated activities of cooks and workers engaged in food preparation used all food handling standards cleaned, cut, and cooked meat, fish, or poultry complied with scheduled kitchen sanitation and ensured all standards and practices were met cooked food properly and in a timely fashion, using safety precautions 012015 - 052015 company name city , state line cook consistently verified that kitchen staff followed all recipes and portioned serving guidelines correctly. consistently kept a clean and safe environment by adhering to all federal, state and local sanitation and safety requirements. communicated clearly and positively with co-workers and management. worked well with teammates and openly invited coaching from the management team. followed all established restaurant practices and procedures. education 2011 william m davies career  tech city , state , usa high school diploma : culinary auto body courses in hospitality and restaurant management classes in restaurant and facility operations basic vocational : prep cook courses in: food preparation, kitchen management,patisserie and confectionery, international cuisine"""
    
    ats.process_cv(cv_text)
    
    user_input = input("\nKata kunci (pisah dengan koma): ")
    keywords = [keyword.strip() for keyword in user_input.split(',')]
    
    
    ats.search_keywords(keywords)
    ats.display_results()

if __name__ == "__main__":
    main()