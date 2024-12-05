import unittest
from unittest.mock import patch, MagicMock
import asyncio
from scripts.main import main

class TestMain(unittest.TestCase):

    @patch('builtins.input', return_value='1234567890')
    @patch('scripts.main.initiate_call')
    @patch('scripts.main.handle_conversation')
    def test_main(self, mock_handle_conversation, mock_initiate_call, mock_input):
        mock_handle_conversation.return_value = asyncio.Future()
        mock_handle_conversation.return_value.set_result(None)

        main()

        mock_input.assert_called_once_with("Enter the lead's phone number: ")
        mock_initiate_call.assert_called_once_with('1234567890')
        mock_handle_conversation.assert_called_once()
        print("Main function test passed.")

if __name__ == '__main__':
    unittest.main()