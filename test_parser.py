import unittest
from unittest.mock import patch
from parser import fetch_vacancies, save_vacancies_to_db

class TestVacancyFetcher(unittest.TestCase):

    @patch('requests.get')
    def test_fetch_vacancies(self, mock_get):
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            'items': [{'id': 1, 'Имя': 'Тестовая работа'}]
        }
        result = fetch_vacancies("url", {"param": "value"})
        self.assertIsInstance(result, dict)
        self.assertIn('items', result)
        self.assertEqual(result['items'][0]['id'], 1)

    @patch('psycopg2.connect')
    def test_save_vacancies_to_db(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value
        vacancies = {'items': [{'id': 1, 'Имя': 'Тестовая работа'}]}
        conn = mock_connect.return_value
        save_vacancies_to_db(conn, vacancies)
        mock_cursor.execute.assert_called()

if __name__ == '__main__':
    unittest.main()