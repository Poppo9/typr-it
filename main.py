import time
import difflib
import random

print("Welcome to the typing test!")
possible_words = ["Hello", "world", "this", "is", "a", "test", "python", "programming", "language", "computer", "science", "technology", "internet", "data", "algorithm", "structure", "function", "class", "object", "inheritance", "polymorphism", "encapsulation", "abstraction", "database", "web", "mobile", "software", "hardware", "network", "security", "cloud", "artificial", "intelligence", "machine", "learning", "deep", "neural", "network", "genetic", "algorithm", "quantum", "computing", "blockchain", "cryptography", "cybersecurity", "digital", "forensics", "ethical", "hacking", "privacy", "social", "media", "marketing", "advertising", "sales", "customer", "service", "support", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership", "team", "work", "effort", "time", "management", "leadership"]
words_to_type = " ".join(random.choice(possible_words) for _ in range(10))

print("Type the words below:")
print(words_to_type)

print("--------------------------------")

print("Type the words above: ")
start_time = time.time()
user_input = input()
end_time = time.time()


time_taken = end_time - start_time

accuracy = difflib.SequenceMatcher(None, words_to_type, user_input).ratio()

print(f"Time taken: {time_taken} seconds")
print(f"Words per minute: {(len(words_to_type.split()) / time_taken) * 60}")
print(f"Accuracy: {accuracy * 100}%")






