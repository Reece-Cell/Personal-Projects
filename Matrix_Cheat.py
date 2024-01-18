from tqdm import tqdm

class WordMatrix:
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

    def __init__(self, letters, valid_words_file):
        letters += [''] * (5 - len(letters) % 5)
        self.matrix = [letters[i:i+5] for i in range(0, len(letters), 5)]
        self.rows = len(self.matrix)
        self.cols = len(self.matrix[0])
        self.valid_words = set(self.read_valid_words(valid_words_file))

    def read_valid_words(self, valid_words_file):
        with open(valid_words_file, 'r') as file:
            return set(word.strip().upper() for word in file)

    def display_matrix(self):
        for row in self.matrix:
            print(" ".join(row))
        print()

    def is_valid_position(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def calculate_word_value(self, word):
        return sum(self.LETTER_VALUES[char] for char in word)

    def get_adjacent_positions(self, row, col):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # All directions including diagonals
        adjacent_positions = [(row + dr, col + dc) for dr, dc in directions]
        return [(r, c) for r, c in adjacent_positions if self.is_valid_position(r, c)]

    def is_possible_word(self, word, current_position, visited):
        if not word:
            return True

        current_char = word[0]
        next_positions = self.get_adjacent_positions(*current_position)

        for r, c in next_positions:
            if self.matrix[r][c] == current_char and (r, c) not in visited:
                if self.is_possible_word(word[1:], (r, c), visited + [(r, c)]):
                    return True

        return False
        
    def find_words(self):
        words_and_values = {}

        with tqdm(total=len(self.valid_words), desc="Progress", unit="word") as pbar:
            for word in self.valid_words:
                for i in range(self.rows):
                    for j in range(self.cols):
                        current_position = (i, j)
                        if len(word) > 1 and self.is_possible_word(word, current_position, [current_position]):
                            words_and_values[word] = self.calculate_word_value(word)
                            break  # No need to continue checking for this word in other positions
                pbar.update(1)

        return words_and_values

# Example usage:
letters_list = [
    'D', 'I', 'F', 'U', 'E',
    'T', 'I', 'D', 'O', 'N',
    'M', 'I', 'A', 'W', 'E',
    'X', 'N', 'L', 'E', 'U',
    'I', 'O', 'W', 'I', 'Y'
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


