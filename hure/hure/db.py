from pymongo import MongoClient
import os
import sys
from dotenv import load_dotenv

load_dotenv()

conn = MongoClient(os.environ.get('MONGODB_URI'))
