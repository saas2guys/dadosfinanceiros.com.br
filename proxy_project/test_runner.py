import logging
import sys

from django.test.runner import DiscoverRunner


class SilentTestRunner(DiscoverRunner):
    """Test runner that silences all logging output during tests."""

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)

        # Disable all logging during tests
        logging.disable(logging.CRITICAL)

        # Also redirect stderr to devnull to catch any remaining output
        if hasattr(self, "verbosity") and self.verbosity == 0:
            import os

            self.old_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")

    def teardown_test_environment(self, **kwargs):
        super().teardown_test_environment(**kwargs)

        # Re-enable logging after tests
        logging.disable(logging.NOTSET)

        # Restore stderr
        if hasattr(self, "old_stderr"):
            sys.stderr.close()
            sys.stderr = self.old_stderr
