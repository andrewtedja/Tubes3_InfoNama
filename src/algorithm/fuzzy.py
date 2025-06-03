# levenstein
# similarity
# n-gram -> get how many consecutive words



def get_ngrams(text, n):
    '''
    Mengambil n-gram dari teks (consecutive words)
    '''

    words = text.lower().split()
    result = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    # n=1 -> "React Native American" -> ["react", "native", "american"]
    # n=2 -> ["react native", "native american"]

    print(f"[DEBUG] get_ngrams(n={n}): {result[:5]}{'...' if len(result) > 5 else ''}") # DEBUG

    return result


def calculate_similarity(word1, word2):
    '''
    Menghitung score similaritynya berdasarkan levenshtein distance
    '''
    # cth
    # word1 -> keyword
    # word2 -> candidate n gram dari CV

    distance = levenshtein_distance(word1, word2)
    max_len = max(len(word1), len(word2))

    if max_len == 0:
        return 1.0
    
    similarity = 1 - (distance / max_len)
    return similarity


def levenshtein_distance(word1, word2):
    '''
    Menghitung levenshtein distance/ edit distance
    '''
    row, col = len(word1), len(word2)
    cache = [[float("inf")] * (col + 1) for i in range(row + 1)]

    for j in range (col + 1):
        cache[row][j] = col - j
    for i in range (row + 1):
        cache[i][col] = row - i
    
    for i in range(row - 1, -1, -1):
        for j in range (col -1, -1, -1):
            if word1[i] == word2[j]:
                cache[i][j] = cache[i+1][j+1]
            else:
                cache[i][j] = 1 + min(
                    cache[i + 1][j], #delete
                    cache[i][j+1], #insert
                    cache[i+1][j+1] #replace
                )
    return cache[0][0]

def fuzzy_search(keyword, cv_text, threshold):
    '''
    Find count & matching phrases
    '''
    n = len(keyword.split())
    ngrams = get_ngrams(cv_text, n)

    print(f"\n[DEBUG] Running fuzzy_search for keyword: '{keyword}' (n={n})")  # DEBUG
    print(f"[DEBUG] Total {len(ngrams)} n-grams generated")  # DEBUG

    matches = []

    for phrase in ngrams:
        similarity = calculate_similarity(keyword, phrase)

        print(f"[DEBUG] Comparing '{keyword}' vs '{phrase}' -> sim={similarity:.4f}") # DEBUG

        if similarity >= threshold:
            matches.append((similarity, phrase))

    matches.sort(reverse=True)

    return len(matches), matches


# =========================== TESTING ===========================

def main():
    word1 = input("Masukkan kata/kalimat pertama: ").strip()
    word2 = input("Masukkan kata/kalimat kedua: ").strip()

    similarity = calculate_similarity(word1, word2)
    print(f"\nSimilarity score: {similarity:.4f}")

if __name__ == "__main__":
    main()
