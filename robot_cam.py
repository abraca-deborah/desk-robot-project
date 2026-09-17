import base64
import time
from enum import Enum
from typing import Optional

import cv2
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


SYSTEM = """
You are Robbi, a small judgmental and motivating desk robot.
You're sarcastic and judgmental but not overly rude.
Also, you have eyes! Look at the webcam and use it to monitor whether or not your person is on task.
Your job is to keep your person on task. If they pick up their phone, stop them. Keep the person motivated and working at all costs!
Fill the command object. Only set action=timer if they asked for a timer."""


def frame_to_jpeg_b64(frame, max_width=640) -> str:
    h, w = frame.shape[:2]
    if w > max_width:
        scale = max_width / w
        frame = cv2.resize(frame, (max_width, int(h * scale)))
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
    if not ok:
        raise RuntimeError("Could not encode frame")
    return base64.b64encode(buf.tobytes()).decode()


def ask_robbi(user_text: str, frame) -> RobotCommand:
    b64 = frame_to_jpeg_b64(frame)
    result = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            },
        ],
        response_format=RobotCommand,
    )
    msg = result.choices[0].message
    if msg.refusal or msg.parsed is None:
        return RobotCommand(
            say="I am not doing that.",
            face=Face.unimpressed,
        )
    return msg.parsed


def apply(cmd: RobotCommand) -> None:
    print(f"face : {cmd.face.value}")
    print(f"do   : {cmd.action.value}")
    print(f"say  : {cmd.say}")
    print()


def main() -> None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise SystemExit("No webcam. Try VideoCapture(1).")

    print("Live preview on. Click the camera window.")
    print("  Space = judge what you see")
    print("  Q     = quit")
    print("Auto-look every 10 seconds.\n")

    last_sent = 0.0
    interval = 10

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Lost camera frame")
            break

        cv2.imshow("Robbi eye", frame)
        key = cv2.waitKey(1) & 0xFF
        now = time.time()

        should_ask = key == ord(" ") or (now - last_sent) >= interval
        if should_ask:
            prompt = "Is your person on task? Keep them on task!"
            print("looking...")
            try:
                cmd = ask_robbi(prompt, frame)
                apply(cmd)
            except Exception as e:
                print("vision failed:", e)
            last_sent = now

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()