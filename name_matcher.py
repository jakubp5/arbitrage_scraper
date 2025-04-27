from rapidfuzz import fuzz

class NameMatcher:
    def __init__(self, threshold=90):
        self.known_names = []
        self.threshold = threshold

    def match(self, name):
        name = name.lower().strip()

        for known in self.known_names:
            score = fuzz.ratio(name, known)
            if score >= self.threshold:
                return known  # return the matched canonical name

        # No match found, add new name
        self.known_names.append(name)
        return name
