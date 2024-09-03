import random

groups = [
    ("fruit",                 ["apple",    "orange",     "pineapple", "watermelon"]),
    ("programming languages", ["python",   "java",       "c",         "assembly"]),
    ("sports",                ["football", "basketball", "baseball",  "volleyball"]),
    ("subjects",              ["math",     "science",    "history",   "art"])
]

NAME = 0
WORDS = 1

class ConnectionsAPI:
    groups: list[tuple[str, list[str]]]
    group_words: list[str]

    solved_groups: list[tuple[str, list[str]]]

    def __init__(self, groups: list[tuple[str, list[str]]]):
        self.groups = groups.copy()
        self.group_words = [word for group in self.groups for word in group[WORDS]]
        self.shuffle_words()
        self.solved_groups = []

        self._max_length = max(len(word) for word in self.group_words)
    
    def shuffle_words(self, seed=None):
        if seed is None:
            random.shuffle(self.group_words)
        else:
            random.Random(seed).shuffle(self.group_words)

    def check_group(self, word_group: list[str]):
        group_found = None
        for group in self.groups:
            if all(word in group[WORDS] for word in word_group):
                group_found = group
                break
        if group_found is None:
            return None
        self.groups.remove(group_found)
        self.solved_groups.append(group_found)
        for word in group_found[WORDS]:
            self.group_words.remove(word)
        return group_found
        
    def __repr__(self):
        return f"Connections({self.groups = })"

    def __str__(self):
        lines = []
        lines.append("==" + '=|='.join(['=' * self._max_length] * 4) + '==')
        for solved_group in self.solved_groups:
            lines.append("|-" + solved_group[NAME] + '=' * (self._max_length * 4 + 3 * 3 - len(solved_group[NAME])) + '-|')
            lines.append("|-" + '-|-'.join(['-' * self._max_length] * 4) + '-|')
            lines.append("|-" + '-|-'.join([word + '-' * (self._max_length - len(word)) for word in solved_group[WORDS]]) + '-|')
            lines.append("==" + '=|='.join(['=' * self._max_length] * 4) + '==')
        for row in range(len(self.groups)):
            lines.append("| " + ' | '.join([' ' * self._max_length] * 4) + ' |')
            lines.append("| " + ' | '.join([self.group_words[row*4 + index] + ' ' * (self._max_length - len(self.group_words[row*4 + index])) for index in range(4)]) + ' |')
            lines.append("| " + ' | '.join([' ' * self._max_length] * 4) + ' |')
            lines.append("|-" + '-|-'.join(['-' * self._max_length] * 4) + '-|')
        return '\n'.join(lines)
            

connectionsapi = ConnectionsAPI(groups)

print("Hello, welcome to connections!\n")

print(connectionsapi)

selection = []
reset = True

while True:
    action = None
    if len(selection) < 4:
        while action not in connectionsapi.group_words:
            if not reset:
                print("invalid input, try again\n")
            if len(selection) == 0:
                action = input("select a valid word: ")
            else:
                action = input("select or deselect a word: ")
            reset = False
        print()
        if action in selection:
            selection.remove(action)
        else:
            selection.append(action)
    else:
        while action not in selection and action != '':
            if not reset:
                print("invalid input, try again\n")
            action = input("deselect a valid word or press enter to submit your selection: ")
            reset = False
        print()
        if action == '':
            result = connectionsapi.check_group(selection)
            if result is None:
                print("Wrong group, try again\n")
            else:
                print("Correct guess, here's the new table\n")
                print(connectionsapi)
                selection = []
                if len(connectionsapi.groups) == 0:
                    print("you won the game!")
                    exit()
        else:
            selection.remove(action)

    print(f"selected words: {selection}")
    reset = True
