# Tests package for the proxy project
# This file ensures that the tests directory is treated as a Python package
# and allows for proper test discovery by Django's test runner

# Note: We don't import test modules here to avoid Django model loading issues
# Django's test discovery will find the test modules automatically 