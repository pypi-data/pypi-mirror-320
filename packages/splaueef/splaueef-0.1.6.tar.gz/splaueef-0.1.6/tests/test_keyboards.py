import unittest
from aiohelp.keyboards import generate_keyboard

class TestKeyboards(unittest.TestCase):
    def test_generate_keyboard(self):
        buttons = [["Button 1", "Button 2"], ["Button 3"]]
        keyboard = generate_keyboard(buttons)
        self.assertEqual(len(keyboard.keyboard), 2)  # Два ряди
        self.assertEqual(keyboard.keyboard[0][0].text, "Button 1")
