import random
from dataclasses import dataclass

SEED = None
if SEED is not None:
    random = random.Random(SEED)

error_log: list[str] = []

# ------------------------------------------------------------------------
# Create Groups
WORDS_IN_GROUP = 4

@dataclass
class FullGroup:
    """stores data of a full connections group with an unlimited number of words"""
    name: str
    words: list[str]
    
@dataclass
class Group:
    """stores data of a connections group limited to 4 words"""
    name: str
    words: tuple[str, str, str, str]
    
GROUPS = [
    FullGroup("fruit",       ["apple", "banana", "orange", "strawberry", "grape", "watermelon", "pineapple", "mango", "peach", "cherry", "plum"]),
    FullGroup("programming", ["c", "c++", "c#", "go", "html", "java", "php", "python", "ruby", "rust", "javascript", "css"]),
    FullGroup("sports",      ["soccer", "basketball", "hockey", "tennis", "volleyball", "football", "mma", "baseball"]),
    FullGroup("subjects",    ["philosophy", "geography", "psychology", "history", "archaeology", "anthropology", "chemistry", "biology", "physics", "economics", "math", "linguistics", "architecture", "education", "engineering", "medicine"]),
    FullGroup("technology",  ["computer", "phone", "clock", "car", "airplane", "television", "camera"]),
    FullGroup("artists",     ["pollock", "da vinci", "michelangelo", "van gogh", "monet", "picasso"]),
    FullGroup("books",       ["harry potter", "lord of the rings", "percy jackson", "fablehaven", "game of thrones", "narnia"]),
    FullGroup("superheroes", ["batman", "superman", "captain america", "iron man", "wolverine", "thor", "hulk", "xavier", "wonder woman", "spider man"]),
]

def create_groups():
    return [
        Group(group.name, tuple(random.sample(group.words, k=WORDS_IN_GROUP))) 
        for group in random.sample(GROUPS, k=WORDS_IN_GROUP)
    ]

# ------------------------------------------------------------------------
# Connections API
class ConnectionsAPI:
    """API class for connections (only handles logic)"""
    remaining_groups: list[Group]
    remaining_words: list[str]

    selected_words: list[str]
    solved_groups: list[Group]
    lives = 4

    def __init__(self, groups: list[Group] | None = None):
        if groups is None:
            groups = create_groups()
        self.remaining_groups = groups

        self.remaining_words = [word for group in self.remaining_groups for word in group.words]
        random.shuffle(self.remaining_words)

        self.selected_words = []
        self.solved_groups = []

    def toggle_word_selection(self, selected_word: str) -> bool:
        if selected_word not in self.remaining_words:
            return False
        if selected_word in self.selected_words:
            self.selected_words.remove(selected_word)
        else:
            self.selected_words.append(selected_word)

    def find_selected_group(self) -> Group | None:
        """Find group aligning with the selected_words (returns None otherwise)"""
        seleected_group: Group | None = None
        for group in self.remaining_groups:
            if all(word in group.words for word in self.selected_words):
                seleected_group = group
                break
        return seleected_group

    def submit_selection(self) -> bool:
        """Submit selected words"""
        selected_group = self.find_selected_group()
        self.selected_words.clear()
        if selected_group is None:
            self.lives -= 1
            return False
        
        self.remaining_groups.remove(selected_group)
        self.solved_groups.append(selected_group)
        for word in selected_group.words:
            self.remaining_words.remove(word)
        return True
    
    def loss_condition(self):
        return self.lives == 0
    def win_condition(self):
        return len(self.remaining_groups) == 0

# ------------------------------------------------------------------------
# Connections Display
class ConnectionsDisplay:
    """Manages logic for displaying connections game"""
    connections_api: ConnectionsAPI
    max_word_length: int

    def __init__(self, connections_api: ConnectionsAPI):
        self.connections_api = connections_api

        self.max_word_length = 0
        for word in self.connections_api.remaining_words:
            word_length = len(word)
            if word_length > self.max_word_length:
                self.max_word_length = word_length
    
    def color_at_position(self, row_i, column_i):
        if row_i < len(self.connections_api.solved_groups):
            return f"\033[1;{41 + row_i}m"
        row_i -= len(self.connections_api.solved_groups)
        word = self.connections_api.remaining_words[row_i * WORDS_IN_GROUP + column_i]
        if word in self.connections_api.selected_words:
            return f"\033[48;5;242m"
        return ''
    
    def word_display_at_position(self, row_i, column_i):
        if row_i < len(self.connections_api.solved_groups):
            word = self.connections_api.solved_groups[row_i].words[column_i]
        else:
            row_i -= len(self.connections_api.solved_groups)
            word = self.connections_api.remaining_words[row_i * 4 + column_i]
        return word + ' ' * (self.max_word_length - len(word))
    
    def group_display_at_row(self, row_i):
        group_name = self.connections_api.solved_groups[row_i].name
        color = self.color_at_position(row_i, None)
        row_length = self.max_word_length * WORDS_IN_GROUP + 3 * (WORDS_IN_GROUP - 1)
        return color + ' ' + group_name + ' ' * (row_length - len(group_name)) + ' \033[0m'

    def __str__(self) -> str:
        lines = []
        lines.append("_" + '_'.join(['_' * (self.max_word_length + 2)] * WORDS_IN_GROUP) + '_')
        # ------------------------------------
        # display solved groups
        for row_i in range(len(self.connections_api.solved_groups)):
            lines.append("|" + self.color_at_position(row_i, None) + '-'.join('-' * (self.max_word_length + 2) for column_i in range(WORDS_IN_GROUP)) + '\033[0m' + '|')
            lines.append("|" + self.group_display_at_row(row_i) + "|")
            lines.append("|" + self.color_at_position(row_i, None) + '-'.join('-' * (self.max_word_length + 2) for column_i in range(WORDS_IN_GROUP)) + '\033[0m' + '|')
            lines.append("|" + '|'.join(self.color_at_position(row_i, column_i) + ' ' + self.word_display_at_position(row_i, column_i) + ' ' + '\033[0m' for column_i in range(WORDS_IN_GROUP)) + '|')
            lines.append("|" + '|'.join(self.color_at_position(row_i, column_i) + '_' * (self.max_word_length + 2) + '\033[0m' for column_i in range(WORDS_IN_GROUP)) + '|')
        # ------------------------------------
        # display remaining words
        for row_i in range(len(self.connections_api.solved_groups), WORDS_IN_GROUP):
            lines.append("|" + '|'.join(self.color_at_position(row_i, column_i) + ' ' * (self.max_word_length + 2) + '\033[0m' for column_i in range(WORDS_IN_GROUP)) + '|')
            lines.append("|" + '|'.join(self.color_at_position(row_i, column_i) + ' ' * (self.max_word_length + 2) + '\033[0m' for column_i in range(WORDS_IN_GROUP)) + '|')
            lines.append("|" + '|'.join(self.color_at_position(row_i, column_i) + ' ' + self.word_display_at_position(row_i, column_i) + ' ' + '\033[0m' for column_i in range(WORDS_IN_GROUP)) + '|')
            lines.append("|" + '|'.join(self.color_at_position(row_i, column_i) + ' ' * (self.max_word_length + 2) + '\033[0m' for column_i in range(WORDS_IN_GROUP)) + '|')
            lines.append("|" + '|'.join(self.color_at_position(row_i, column_i) + '_' * (self.max_word_length + 2) + '\033[0m' for column_i in range(WORDS_IN_GROUP)) + '|')
        lines.append(f"remaining lives: \033[31m{'♡ ' * self.connections_api.lives}\033[0m")
        return '\n'.join(lines)

# ------------------------------------------------------------------------
# Connections Game
class ConnectionsGame:
    """Runs connections, connecting the api and the display"""
    connections_api: ConnectionsAPI
    connections_display: ConnectionsDisplay

    def __init__(self, connections_api: ConnectionsAPI | None = None, connections_display: ConnectionsDisplay | None = None):
        if connections_api is None:
            connections_api = ConnectionsAPI()
        self.connections_api = connections_api
        if connections_display is None:
            connections_display = ConnectionsDisplay(self.connections_api)
        self.connections_display = connections_display

    def run(self):
        print("Hello! Welcome to a Connections Clone made in python.")

        print(self)

        game_over = False
        win_flag = False
        while not game_over:
            reset = True
            note = ""
            if len(self.connections_api.selected_words) == 0:
                # ------------------------------------
                # no selected words (must select word)
                while True:
                    if not reset:
                        print("invalid word (not in list of remaining words), try again")
                    user_input = input("select a remaining word: ").strip().lower()
                    if user_input in self.connections_api.remaining_words:
                        self.connections_api.selected_words.append(user_input)
                        break
                    reset = False
            elif len(self.connections_api.selected_words) < WORDS_IN_GROUP:
                # ------------------------------------
                # selected words less than max (select word or deselect from selection)
                while True:
                    if not reset:
                        print("invalid word (not in list of remaining words), try again")
                    user_input = input("select or deselect a remaining word: ").strip().lower()
                    if user_input in self.connections_api.selected_words:
                        self.connections_api.selected_words.remove(user_input)
                        break
                    elif user_input in self.connections_api.remaining_words:
                        self.connections_api.selected_words.append(user_input)
                        break
                    reset = False
            else:
                # ------------------------------------
                # selected words at maximum (deselect word or submit selection)
                while True:
                    if not reset:
                        print("invalid input, try again")
                    user_input = input("deselect a selected word or press enter to submit your selection: ").strip().lower()
                    if user_input in self.connections_api.selected_words:
                        self.connections_api.selected_words.remove(user_input)
                        break
                    elif user_input == '':
                        result = self.connections_api.submit_selection()
                        if result == False:
                            note = "words do not align as a group (1 life lost) :("
                        if self.connections_api.loss_condition():
                            game_over = True
                            win_flag = False
                            note = "you have lost the game, better luck next time :("
                        elif self.connections_api.win_condition():
                            game_over = True
                            win_flag = True
                            note = "you have won the game, congratulations :)"
                        break
                    reset = False
            print(self)
            if note != '':
                print(note)

        return win_flag


    def __str__(self) -> str:
        return str(self.connections_display)


# ------------------------------------------------------------------------
# Run game
if __name__ == "__main__":
    connections_game = ConnectionsGame()
    connections_game.run()