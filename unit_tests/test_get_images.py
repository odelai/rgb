import sys
import os
import pika
import logging
import logging.config
import yaml
import unittest
from PIL import Image
from io import BytesIO
from typing import List
from get_images.get_images import *


class TestGetImages(unittest.TestCase):    
    def test_is_valid_args(self):
        logger = setup_logger()
        
        empty = [""]
        self.assertEqual(is_valid_args(empty, logger), False)

        three_args = ["", "first", "second", "third"]
        self.assertEqual(is_valid_args(three_args, logger), False)
        
        one_arg_wrong_dir = ["", "non_existent_dir"]
        self.assertEqual(is_valid_args(one_arg_wrong_dir, logger), False)
        
        two_args_wrong_dir = ["", "non_existent_dir", "does_not_matter_arg"]
        self.assertEqual(is_valid_args(two_args_wrong_dir, logger), False)
        
        one_arg_correct_dir = ["", "/example_dir"]
        self.assertEqual(is_valid_args(one_arg_correct_dir, logger), True)
        
        two_args_correct_dir = ["", "/example_dir", "does_not_matter_arg"]
        self.assertEqual(is_valid_args(two_args_correct_dir, logger), True)    
     