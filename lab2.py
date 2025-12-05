import re
import unittest
import sys

def divisible_by_3(s):
    if re.fullmatch(r'[01]+', s):
        return int(s, 2) % 3 == 0
    return False

def find_binary_numbers(text):
    return [w for w in re.findall(r'\b[01]+\b', text) if divisible_by_3(w)]

def main():
    print("1 – ввести текст")
    print("2 – прочитать из файла")
    choice = input("Выбор: ")

    if choice == '1':
        data = input("Текст: ")
        result = find_binary_numbers(data)
    elif choice == '2':
        path = input("Путь к файлу: ")
        with open(path, 'r') as f:
            result = find_binary_numbers(f.read())
    else:
        print("Неверный выбор")
        return

    print("Найдено:", result)

class TestBinary(unittest.TestCase):
    def test_divisible(self):
        self.assertTrue(divisible_by_3('11'))
        self.assertTrue(divisible_by_3('110'))
        self.assertFalse(divisible_by_3('10'))
        self.assertFalse(divisible_by_3('12'))

    def test_find(self):
        text = "числа: 11, 101, 110"
        self.assertEqual(find_binary_numbers(text), ['11', '110'])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        unittest.main(argv=[''], exit=False)
    else:
        main()