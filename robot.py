from enum import Enum
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI()

class Face(str, Enum):
    happy = "happy"
    unimpressed = "unimpressed"
    sleepy = "sleepy"
    evil = "evil"


class Action(str, Enum):
    none = "none"
    timer = "timer"
    look = "look"


class RobotCommand(BaseModel):
    say: str = Field(description="Spoken line, under 20 words")
    face: Face
    action: Action = Action.none
    timer_minutes: Optional[int] = None


SYSTEM = """You are Robbi, a small judgmental and motivating desk robot.
You're sarcastic and judgmental but not overly rude.
Your job is to keep your person on task. If they pick up their phone, stop them. Keep the person motivated and working at all costs!
Fill the command object. Only set action=timer if they asked for a timer.
"""


def ask_robbi(user_text: str) -> RobotCommand:
    result = client.chat.completions.parse(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_text},
        ],
        response_format=RobotCommand,
    )
    msg = result.choices[0].message
    if msg.refusal:
        return RobotCommand(
            say="I am not doing that.",
            face=Face.unimpressed,
            action=Action.none,
        )
    return msg.parsed


def apply(cmd: RobotCommand) -> None:
    print(f"face : {cmd.face.value}")
    print(f"do   : {cmd.action.value}", end="")
    if cmd.action == Action.timer:
        minutes = cmd.timer_minutes or 25
        minutes = max(1, min(minutes, 60))
        print(f" ({minutes} min)")
    else:
        print()
    print(f"say  : {cmd.say}")


def main() -> None:
    print("What do you want today?\n")
    while True:
        user = input("You: ").strip()
        if user.lower() in {"quit", "exit", "q"}:
            break
        if not user:
            continue
        try:
            cmd = ask_robbi(user)
        except Exception as e:
            print("parse failed:", e)
            cmd = RobotCommand(
                say="How about we try that in a language I can understand?",
                face=Face.sleepy,
                action=Action.none,
            )
        apply(cmd)
        print()


if __name__ == "__main__":
    main()