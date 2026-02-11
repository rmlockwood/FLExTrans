# Stub for fuzzywuzzy module (fuzzy string matching)

class FuzzMatcher:
    def ratio(self, s1, s2):
        """Return similarity ratio between 0 and 100"""
        return 50
    
    def partial_ratio(self, s1, s2):
        """Return partial ratio"""
        return 50
    
    def token_set_ratio(self, s1, s2):
        """Return token set ratio"""
        return 50
    
    def token_sort_ratio(self, s1, s2):
        """Return token sort ratio"""
        return 50

fuzz = FuzzMatcher()

class Process:
    @staticmethod
    def extract(query, choices, limit=None):
        """Mock extract function for fuzzy matching"""
        return [(choice, 50) for choice in choices[:limit or len(choices)]]
    
    @staticmethod
    def extractOne(query, choices):
        """Mock extractOne function"""
        if choices:
            return (choices[0], 50)
        return None
    
    @staticmethod
    def dedupe(contains_dupes):
        """Mock dedupe function"""
        return list(dict.fromkeys(contains_dupes))

process = Process()
