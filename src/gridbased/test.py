from thefuzz import fuzz
import Levenshtein


print(fuzz.ratio("this is a test test testtest test  test test test test test test test test", "this is a test!"))
