from collections import defaultdict
import re

class AHO_ATS:

    def char_to_index(self, char):
        """Convert character to index, handling only lowercase letters a-z"""
        if 'a' <= char <= 'z':
            return ord(char) - 97  # Convert 'a'-'z' to 0-25
        else:
            return 0  

    def __init__(self, words):

        # filter alphanumeric
        self.words = []
        for word in words:
            # Keep only alphanumeric characters and spaces, convert to lowercase
            cleaned_word = re.sub(r'[^\w\s]', '', word.lower()).strip()
            if cleaned_word:  # Only add non-empty words
                self.words.append(cleaned_word)
        
        if not self.words:
            self.max_states = 1
            self.goto = [[]]
            self.out = [0]
            self.fail = [0]
            self.states_count = 1
            return


        # Guess how many 'nodes' or 'states' we might need (sum of word lengths)
        self.max_states = sum([len(word) for word in words])
        self.max_characters = 26

        # Final state (if a state marks end of a complete word), use bitmask to store
        self.out = [0]*(self.max_states+1)

        # Failure link
        self.fail = [-1]*(self.max_states+1) 

        # From a state, given a character, where do we go next?
        self.goto = [[-1]*self.max_characters for _ in range(self.max_states+1)]

        self.words = [word.lower() for word in words]
        self.states_count = self.build_matching()


    # Build the goto and failure link tables
    def build_matching(self) -> int:
        if not self.words:
            return 1

        # ========= 1. Build the basic Trie (main paths) =========
        k = len(self.words)
        states = 1 # root


        for i in range(k):
            word = self.words[i]
            current_state = 0

            for character in word:
                ch = self.char_to_index(character)

                # if no path for curr char -> create new state
                if self.goto[current_state][ch] == -1:
                    self.goto[current_state][ch] = states
                    states += 1
                current_state = self.goto[current_state][ch]

            # Flag state as end of word (word ke i ends here)
            self.out[current_state] |= (1<<i)



        # Kalo gada path, balik ke root
        for ch in range(self.max_characters):
            if self.goto[0][ch] == -1:
                self.goto[0][ch] = 0
        

        # ========= 2. Build the failure link (fallback paths) =========

        queue = [] # BFS tiap state
        for ch in range(self.max_characters):

            # Liat semua yang bisa di reach dari root, set fallback ke root
            if self.goto[0][ch] != 0:
                self.fail[self.goto[0][ch]] = 0
                queue.append(self.goto[0][ch])

        
        while queue:
            state = queue.pop(0)
            for ch in range(self.max_characters):
                # For each state, cari failure link dari semua children-nya
                if self.goto[state][ch] != -1:
                    failure = self.fail[state]

                    '''
                    If my parent's fallback path doesn't work for this character,
                    # try *its* fallback path, and so on, until we find a way forward.
                    '''
                    while self.goto[failure][ch] == -1:
                        failure = self.fail[failure]

                    failure = self.goto[failure][ch]
                    self.fail[self.goto[state][ch]] = failure

                    self.out[self.goto[state][ch]] |= self.out[failure]
                    queue.append(self.goto[state][ch])
        
        return states

    def find_next_state(self, current_state, next_input):
        '''
            Figure out next move during search
        '''
        answer = current_state
        ch = self.char_to_index(next_input)

        # Kalo gada path, balik failure link
        while self.goto[answer][ch] == -1:
            answer = self.fail[answer]
        return self.goto[answer][ch]


    def search_words(self, text):
        '''
            Search for matching words in text
        '''

        if not self.words:
            return defaultdict(list)

        text = re.sub(r'[^\w\s]', '', text.lower())
        current_state = 0
        result = defaultdict(list)

        for i in range(len(text)):
            current_state = self.find_next_state(current_state, text[i])

            # If this state doesn't mark the end of any word, just keep going.
            if self.out[current_state] == 0: 
                continue

            # Final state, check matching words
            for j in range(len(self.words)):
                # Check bitmask flag. Does the flag for the j-th word exist here?
                if (self.out[current_state] & (1<<j)) > 0:
                    word = self.words[j]

                    result[word].append(i-len(word)+1)
        return result

# ============= Test =============
if __name__ == "__main__":
    words = ["he", "she", "hers", "his"]
    text = "ahishers"
    aho_chorasick = AHO_ATS(words)
    result = aho_chorasick.search_words(text)
    for word in result:
        for i in result[word]:
            print("Word", word, "appears from", i, "to", i+len(word)-1)

