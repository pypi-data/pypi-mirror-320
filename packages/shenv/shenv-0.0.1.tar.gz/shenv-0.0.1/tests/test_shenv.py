__copyright__ = "Copyright (c) 2025 Alex Laird"
__license__ = "MIT"

from shenv import shenv
from tests.testcase import ShenvTestCase


class TestNgrok(ShenvTestCase):
    def test_main(self):
        # WHEN
        shenv.main()
