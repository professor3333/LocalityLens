import os

from hypothesis import settings

settings.register_profile("default", max_examples=100, deadline=None)
settings.register_profile("thorough", max_examples=5000, deadline=None)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "default"))
