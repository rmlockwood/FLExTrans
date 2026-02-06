# Stub for pythonnet (clr) module used in CI/tests.
# This allows tests to import without pythonnet being installed.

class _MockAssembly:
    """Mock .NET assembly"""
    pass

def AddReference(assembly_name):
    """Mock AddReference - no-op for CI/tests"""
    return _MockAssembly()

# Export common mock objects that might be referenced
System = _MockAssembly()
