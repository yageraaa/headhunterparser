import unittest
from unittest.mock import patch, MagicMock
import telebot
from bot_parser import bot


class TestTelegramBot(unittest.TestCase):
    def setUp(self):
        self.bot = bot
        self.chat_id = 123456789
        self.user = MagicMock()
        self.user.chat.id = self.chat_id
        self.user.text = 'python developer'

    @patch('bot_parser.get_vacancies')
    @patch('telebot.TeleBot.send_message')
    def test_echo_all_no_vacancies(self, mocked_send_message, mocked_get_vacancies):
        mocked_get_vacancies.return_value = []

        message = telebot.types.Message(1, None, None, self.user, text=self.user.text)

        from bot_parser import echo_all
        echo_all(message)

        mocked_send_message.assert_called_with(
            chat_id=self.chat_id,
            text='По вашему запросу вакансии не найдены.'
        )

    @patch('bot_parser.get_vacancies')
    @patch('telebot.TeleBot.send_message')
    def test_echo_all_with_vacancies(self, mocked_send_message, mocked_get_vacancies):
        mocked_get_vacancies.return_true = [
            (
            'Python Developer', 10000, 20000, 'RUR', 'Яндекс', 'Москва', 'http://ya.ru', 'Полный день', 'Без опыта')
        ]

        message = telebot.types.Message(1, None, None, self.user, text="python")

        from bot_parser import echo_all
        echo_all(message)

        calls = [
            unittest.mock.call(
                chat_id=self.chat_id,
                text='Найдено вакансий: 1\nМинимальная зарплата: 10000\nМаксимальная зарплата: 20000\nСредняя зарплата: 15000'
            ),
            unittest.mock.call(
                chat_id=self.chat_id,
                text='Python Developer 10000-20000 Яндекс Москва http://ya.ru Полный день Без опыта',
                parse_mode='Markdown'
            )
        ]
        mocked_send_message.assert_has_calls(calls, any_order=True)


if __name__ == '__main__':
    unittest.main()
