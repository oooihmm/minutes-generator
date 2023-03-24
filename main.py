import os
import logging
import requests
from dotenv import load_dotenv

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from papago_translator import PapagoTranslator
from openai_generator import MinuteGenerator

load_dotenv()
app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("app_mention")
def handle_mentions(body, say):
    user = body["event"]["user"]
    thread_ts = body["event"]["ts"]
    channel = body["event"]["channel"]

    if "files" in body["event"]:
        files = body["event"]["files"]

        for file_info in files:
            file_id = file_info["id"]
            public_url = file_info["url_private"]
            file_name = file_info["name"]
            file_type = file_info["filetype"]

            accept_types = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "mebm"]
            if file_type in accept_types: # 지원되는 파일 형식인지 파악
                file_save_status = download_file(public_url, file_name) # 파일 다운로드

                if file_save_status:
                    try:
                        say(text=file_name + " 파일의 회의록을 작성하고 있습니다. 잠시만 기다려주세요.", 
                        thread_ts=thread_ts, 
                        channel=channel)

                        generator = MinuteGenerator()
                        generate_result = generator.generate_minute(file_name) # 회의록 작성(whisper) / success: return text, fail: return False

                        if generate_result != False:
                            summary_result = generator.summary_minute(generate_result) # 회의록 요약(gpt) / success: return summary, fail: return False

                            if summary_result != False :
                                translator = PapagoTranslator()
                                translate_result = translator.translate_minute(summary_result) # 영문 요약본 번역(papago) / success: return result, fail: return False

                                if translate_result != False:
                                    say(text=file_name + " 파일에서 생성된 회의록은 다음과 같습니다. \n" + translate_result, 
                                    thread_ts=thread_ts, 
                                    channel=channel)
                                    os.remove(file_name)

                    except:
                        say(text="오류가 발생했습니다. 다시 시도해주세요", 
                        thread_ts=thread_ts, 
                        channel=channel)

            else:
                say(text="지원하지 않는 파일 형식입니다.", 
                thread_ts=thread_ts, 
                channel=channel)

    else:
        say(text="저는 회의록을 작성하는 봇입니다. 제가 필요해지면 저를 멘션해주세요.", 
            thread_ts=thread_ts, 
            channel=channel)


def download_file(public_url, file_name):
    headers = {
        "Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"
    }
    response = requests.get(public_url, headers=headers)

    if response.status_code == 200:
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        return True
    else:
        return False

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()