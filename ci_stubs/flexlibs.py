# Minimal stub for flexlibs used in CI/tests.

class FLExProject:
    def __init__(self):
        pass
    
    def OpenProject(self, project_name: str, shared_mode: bool = True):
        # No-op for CI/tests
        pass

def AllProjectNames():
    # Return empty list for CI/tests
    return []

def FWProjectsDir():
    # Return empty string for CI/tests
    return ""