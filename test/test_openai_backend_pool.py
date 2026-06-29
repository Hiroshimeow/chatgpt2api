from __future__ import annotations

import unittest
from unittest import mock

from services import openai_backend_pool as pool_mod


class FakeSession:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeBackend:
    created: list["FakeBackend"] = []

    def __init__(self, access_token: str = "") -> None:
        self.access_token = access_token
        self.progress_callback = None
        self.session = FakeSession()
        FakeBackend.created.append(self)


class OpenAIBackendPoolTests(unittest.TestCase):
    def setUp(self) -> None:
        FakeBackend.created.clear()

    def test_reuses_idle_backend_until_max_leases(self) -> None:
        with mock.patch.object(pool_mod, "OpenAIBackendAPI", FakeBackend):
            pool = pool_mod.OpenAIBackendPool(max_leases_per_backend=3)
            with pool.lease("token-a") as first:
                self.assertEqual(first.access_token, "token-a")
            with pool.lease("token-a") as second:
                self.assertIs(first, second)
            with pool.lease("token-a") as third:
                self.assertIs(first, third)
            self.assertEqual(len(FakeBackend.created), 1)
            self.assertTrue(first.session.closed)
            self.assertEqual(pool.stats()["entries"], 0)

    def test_does_not_share_backend_while_in_use(self) -> None:
        with mock.patch.object(pool_mod, "OpenAIBackendAPI", FakeBackend):
            pool = pool_mod.OpenAIBackendPool(max_leases_per_backend=10)
            first = pool.acquire("token-a")
            second = pool.acquire("token-a")
            try:
                self.assertIsNot(first, second)
                self.assertEqual(len(FakeBackend.created), 2)
                self.assertEqual(pool.stats()["in_use"], 2)
            finally:
                pool.release(second)
                pool.release(first)
            self.assertEqual(pool.stats()["idle"], 2)

    def test_resets_progress_callback_on_release(self) -> None:
        with mock.patch.object(pool_mod, "OpenAIBackendAPI", FakeBackend):
            pool = pool_mod.OpenAIBackendPool(max_leases_per_backend=10)
            callback = lambda _status: None
            backend = pool.acquire("token-a", progress_callback=callback)
            self.assertIs(backend.progress_callback, callback)
            pool.release(backend)
            self.assertIsNone(backend.progress_callback)


if __name__ == "__main__":
    unittest.main()
