import atexit
from typing import Any, Optional
from DrissionPage import ChromiumPage, ChromiumOptions


class DpMixin(object):
    def __init__(self,
                 *args: Any,
                 co: Optional[ChromiumOptions] = None,
                 cp: Optional[ChromiumPage] = None,
                 close_cp: bool = True,
                 **kwargs: Any):
        if co is None:
            co = self.create_co()
        self.co = co

        if cp is None:
            cp = self.create_cp(self.co)
        self.cp = cp

        self.close_cp = close_cp

        atexit.register(self.close)

    @staticmethod
    def create_co() -> ChromiumOptions:
        co = ChromiumOptions()
        return co

    @staticmethod
    def create_cp(co: ChromiumOptions) -> ChromiumPage:
        cp = ChromiumPage(co)
        return cp

    def close(self):
        if self.close_cp is True and self.cp is not None:
            self.cp.close()
        self.co = None
        self.cp = None
        self.close_cp = True

    def wait_complete(self, cp: Optional[ChromiumPage] = None):
        if cp is None:
            cp = self.cp
        while True:
            if cp.states.ready_state == "complete":
                break
