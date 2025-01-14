import unittest
from typing import Any

from constify import freezeparams


class TestFreezeParams(unittest.TestCase):
    def setUp(self) -> None:
        @freezeparams
        def add_to(value: Any, liste: list[Any] = []) -> list[Any]:
            liste.append(value)
            return liste

        self.add_to = add_to

    def test_default_value(self) -> None:
        test_cases = [(56, [56]), (98, [98])]

        for value, expected_value in test_cases:
            with self.subTest(value=value, expected_value=expected_value):
                self.assertEqual(self.add_to(value), expected_value)
                self.assertEqual(self.add_to(value=value), expected_value)

    def test_non_default_value(self) -> None:
        value = 3
        my_list = [1, 2]
        expected_value = [1, 2, 3]
        self.assertEqual(self.add_to(value, my_list), expected_value)
        self.assertEqual(self.add_to(value, liste=my_list), expected_value)
        self.assertEqual(my_list, [1, 2])
