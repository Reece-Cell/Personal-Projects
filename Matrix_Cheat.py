from tqdm import tqdm
 
LETTER_VALUES = {
    'A': 1, 'E': 1, 'I': 1, 'O': 1,
    'N': 2, 'R': 2, 'S': 2, 'T': 2,
    'D': 3, 'G': 3, 'L': 3,
    'B': 4, 'H': 4, 'P': 4, 'M': 4, 'U': 4, 'Y': 4,
    'C': 5, 'F': 5, 'V': 5, 'W': 5,
    'K': 6,
    'J': 7, 'X': 7,
    'Q': 8, 'Z': 8
}
 
 
class TrieNode:
    __slots__ = ('children', 'is_word')
 
    def __init__(self):
        self.children = {}
        self.is_word = False
 
 
class Trie:
    def __init__(self, words):
        self.root = TrieNode()
        for word in words:
            self.insert(word)
 
    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_word = True
 
 
class WordMatrix:
    def __init__(self, letters, valid_words_file):
        letters = list(letters)
        letters += [''] * ((5 - len(letters) % 5) % 5)
        self.matrix = [letters[i:i + 5] for i in range(0, len(letters), 5)]
        self.rows = len(self.matrix)
        self.cols = len(self.matrix[0])
        self.valid_words = self.read_valid_words(valid_words_file)
        self.trie = Trie(self.valid_words)
        self.neighbors = self._precompute_neighbors()
 
    def read_valid_words(self, valid_words_file):
        with open(valid_words_file, 'r') as file:
            return set(word.strip().upper() for word in file if word.strip())
 
    def display_matrix(self):
        for row in self.matrix:
            print(" ".join(row))
        print()
 
    def calculate_word_value(self, word):
        return sum(LETTER_VALUES[ch] for ch in word)
 
    def _precompute_neighbors(self):
        """Precompute adjacency once instead of recalculating every DFS call."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        neighbors = {}
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors[(r, c)] = [
                    (r + dr, c + dc) for dr, dc in directions
                    if 0 <= r + dr < self.rows and 0 <= c + dc < self.cols
                    and self.matrix[r + dr][c + dc]  # skip padded empty cells
                ]
        return neighbors
  
    def _dfs(self, position, visited, current_string, trie_node, found_words):
        """
        Grow current_string outward from `position`. At every step, current_string
        corresponds to walking `trie_node` down the Trie. If trie_node is None,
        this path is not a prefix of anything and we've already pruned it before
        recursing, so this function is never called on a dead prefix.
 
        We do NOT stop recursing just because current_string is already a word,
        so "THE" doesn't block "THESIS" from being found along the same path.
        """
        if trie_node.is_word and len(current_string) > 1:
            found_words.add(current_string)
 
        for pos in self.neighbors[position]:
            if pos in visited:
                continue
            letter = self.matrix[pos[0]][pos[1]]
            next_node = trie_node.children.get(letter)
            if next_node is None:
                continue  # prune: no word continues with this letter
            visited.add(pos)
            self._dfs(pos, visited, current_string + letter, next_node, found_words)
            visited.remove(pos)
 
    def find_words(self):
        found_words = set()
        total_cells = self.rows * self.cols
        with tqdm(total=total_cells, desc="Progress", unit="cell") as pbar:
            for i in range(self.rows):
                for j in range(self.cols):
                    start = (i, j)
                    letter = self.matrix[i][j]
                    if not letter:
                        pbar.update(1)
                        continue
                    root_node = self.trie.root.children.get(letter)
                    if root_node is not None:
                        visited = {start}
                        self._dfs(start, visited, letter, root_node, found_words)
                    pbar.update(1)
 
        return {w: self.calculate_word_value(w) for w in found_words}
 
    # ---------- Variant: allow one "wildcard" letter along the path ----------
 
    def _dfs_with_one_free_letter(self, position, visited, current_string,
                                   trie_node, found_words, free_letter_used):
        if trie_node.is_word and len(current_string) > 1:
            found_words.add(current_string)
 
        for pos in self.neighbors[position]:
            if pos in visited:
                continue
            letter = self.matrix[pos[0]][pos[1]]
 
            # Normal continuation: letter matches an existing trie edge.
            next_node = trie_node.children.get(letter)
            if next_node is not None:
                visited.add(pos)
                self._dfs_with_one_free_letter(
                    pos, visited, current_string + letter, next_node,
                    found_words, free_letter_used
                )
                visited.remove(pos)
 
            # Wildcard continuation: spend the one free letter to jump down
            # every possible trie edge regardless of the board's actual letter.
            if not free_letter_used:
                visited.add(pos)
                for wildcard_letter, wildcard_node in trie_node.children.items():
                    self._dfs_with_one_free_letter(
                        pos, visited, current_string + wildcard_letter, wildcard_node,
                        found_words, True
                    )
                visited.remove(pos)
 
    def find_words_with_free_letter_limit_one(self):
        found_words = set()
        total_cells = self.rows * self.cols
        with tqdm(total=total_cells, desc="Progress", unit="cell") as pbar:
            for i in range(self.rows):
                for j in range(self.cols):
                    start = (i, j)
                    letter = self.matrix[i][j]
                    if not letter:
                        pbar.update(1)
                        continue
 
                    # Path taken with the board's real starting letter.
                    root_node = self.trie.root.children.get(letter)
                    if root_node is not None:
                        visited = {start}
                        self._dfs_with_one_free_letter(
                            start, visited, letter, root_node, found_words, False
                        )
 
                    # Path taken by treating the *starting* letter itself as free.
                    visited = {start}
                    for wildcard_letter, wildcard_node in self.trie.root.children.items():
                        self._dfs_with_one_free_letter(
                            start, visited, wildcard_letter, wildcard_node,
                            found_words, True
                        )
                    pbar.update(1)
 
        return {w: self.calculate_word_value(w) for w in found_words}
 
 
if __name__ == "__main__":
    letters_list = [
        'O', 'M', 'R', 'N', 'W',
        'T', 'G', 'G', 'D', 'O',
        'R', 'Z', 'G', 'L', 'T',
        'E', 'S', 'M', 'S', 'H',
        'L', 'O', 'S', 'E', 'R',
    ]
    valid_words_file = r'C:\Users\rebel\words.txt'
    word_matrix = WordMatrix(letters_list, valid_words_file)
 
    print("Matrix:")
    word_matrix.display_matrix()
 
    words_and_values = word_matrix.find_words()
    sorted_words = sorted(words_and_values.items(), key=lambda x: x[1], reverse=True)[:10]
 
    print("Top 10 Valid Words and Their Values:")
    for word, value in sorted_words:
        print(f"{word}: {value}")
 
    words_and_values_limit_one = word_matrix.find_words_with_free_letter_limit_one()
    sorted_words_limit_one = sorted(
        words_and_values_limit_one.items(), key=lambda x: x[1], reverse=True
    )[:10]
 
    print("Top 10 Valid Words with One Letter Replacement and Their Values:")
    for word, value in sorted_words_limit_one:
        print(f"{word}: {value}")
