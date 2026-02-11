# Stub for mixpanel module used in CI/tests
# mixpanel is an analytics library that's not needed for unit tests

class Mixpanel:
    """Mock Mixpanel analytics class"""
    def __init__(self, token):
        self.token = token
    
    def track(self, distinct_id, event_name, properties=None):
        """Mock track method - no-op for CI/tests"""
        pass
    
    def flush(self):
        """Mock flush method - no-op for CI/tests"""
        pass
