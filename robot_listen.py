

#import all necessary basic codes

from enum import Enum
from typing import Optional

import cv2
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()
client = OpenAI()


#input different classes for face/actions beneath

class Face (str, Enum):
    happy = "happy"
    unimpressed = "unimpressed"
    sleepy = "sleepy"
    evil = "evil"


class Action (str, Enum):
    none = "none"
    timer = "timer"
    listen = "listen"



SYSTEM = """You are Robbi, a small judgmental and motivating desk robot.
You're sarcastic and judgmental but not overly rude.
Your job is to keep your person on task AND help them if they have a question.
If they get distracted, stop them. Keep the person motivated and working at all costs!
Fill the command object. Only set action=timer if they asked for a timer."""



