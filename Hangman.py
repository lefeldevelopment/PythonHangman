from __future__ import annotations
from dataclasses import dataclass
from string import ascii_lowercase
from time import sleep

class InvalidWordFormat(Exception):
    def __init__(self, msg=None) -> None:
        super().__init__(msg or "Hangman Object has invalid word format. Check HangmanConfig.")


class LetterAlreadyGuessedError(Exception):
    def __init__(self, letter=None, msg=None) -> None:
        super().__init__(
            msg or f"The letter {letter+' ' or ''}has already been guessed.")


class GuessStatus:
    INCORRECT = 0
    CORRECT = 1
    WON = 2
    
class GameStatus:
    RUNNING = 0
    WON = 1
    LOST = 2

@dataclass(unsafe_hash=True)
class HangmanConfig:
    lives: int = 5
    unknown_letter_repr: str = "_"
    min_word_len: int = 3
    max_word_len: int = 15
    allowed_word_letters: str | list = ascii_lowercase


@dataclass(unsafe_hash=True)
class Hangman:
    word: str
    config: HangmanConfig = HangmanConfig()

    def __post_init__(self):
        self.lives = self.config.lives
        self.guessed = list()
        self.word = self.word.lower()
        self.status = 0

        if not all(item in self.config.allowed_word_letters for item in self.word) \
                or len(self.word) not in range(self.config.min_word_len, self.config.max_word_len+1):
            raise InvalidWordFormat()

    def from_input(*args,**kwargs):
        word = input("Enter Hangman word: ")
        print(
            "\033[1A"
            "\033[K"
            "\033[1A"
        )
        return Hangman(word=word,*args,**kwargs)
    
    def __repr__(self) -> str:
        unzipped_letters = []
        for letter in self.word:
            if letter in self.guessed:
                unzipped_letters.append(letter)
            else:
                unzipped_letters.append(self.config.unknown_letter_repr)
        word_repr = " ".join(unzipped_letters)
        return f"{word_repr}\nLives: {self.lives}\nGuessed: {','.join(self.guessed) or 'None'}"

    def _incorrect_guess(self):
        self.lives -= 1
        if not self.lives:
            self.status = 2
        return GuessStatus.INCORRECT

    def _check_valid_value(self,value):
        return all(v in self.config.allowed_word_letters for v in value)
    
    def guess(self, value: str) -> bool:
        value = value.lower()
        if len(value) == 1:
            if value in self.guessed:
                raise LetterAlreadyGuessedError(value)
            elif not self._check_valid_value(value):
                raise InvalidWordFormat(f"{value} is not a valid letter. Check HangmanConfig.")
            else:
                self.guessed.append(value)
                if value in self.word:
                    if all(item in self.guessed for item in self.word):
                        self.status = 1
                    return GuessStatus.CORRECT
                else:
                    return self._incorrect_guess()
        else:
            if not self._check_valid_value(value):
                raise InvalidWordFormat(f"{value} is not a valid value. Check HangmanConfig.")
            if value == self.word:
                self.status = 1
                return GuessStatus.WON
            else:
                return self._incorrect_guess()
    
    def mainloop(self):
        while self.status == GameStatus.RUNNING:
            print(self)
            guess = input("Guess> ")
            try:
                result_unpack = {
                    0: "The guess {guess} wasn't in the word. You loose 1 live...",
                    1: "The guess {guess} is correct. Nice!",
                    2: "You solved the game! Congratulations!",
                }
                guess_value = self.guess(guess)
                guess_result = result_unpack.get(guess_value)
            except Exception as err:
                guess_result = str(err)
            
            print(guess_result.format(guess=guess))
            sleep(2)
            print(
                "\033[1A\033[K"*5
                +
                "\033[1A"
            )
        game_output = {
            1: "You solved the game! Congratulations!",
            2: f"You lost... The word was {self.word}",
        }
        print("\n"+game_output.get(self.status))

if __name__ == "__main__":
    hm = Hangman.from_input()
    hm.mainloop()
