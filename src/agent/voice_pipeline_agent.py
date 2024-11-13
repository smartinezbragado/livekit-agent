import os
import json
import asyncio
import aiofiles
import logging
from datetime import datetime
from livekit.agents import (
    AutoSubscribe, 
    JobContext, 
    WorkerOptions, 
    JobProcess,
    cli,
    llm
)
from livekit.agents.llm import ChatContext
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero, elevenlabs
from src.agent.prompts import PROMPT

logger = logging.getLogger("voice-assistant")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


class VoiceAssistantWithSilenceDetection(VoiceAssistant):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_user_input_time = datetime.now()

    async def on_user_input(self, text):
        self.last_user_input_time = datetime.now()
        await super().on_user_input(text)


async def entrypoint(ctx: JobContext):
    initial_context = ChatContext().append(
        role="system",
        text=PROMPT
    )

    await ctx.connect(
        auto_subscribe=AutoSubscribe.AUDIO_ONLY,
    )
    
    logger.info(f"connecting to room {ctx.room.name}")
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    voice = elevenlabs.Voice(
        id="D7dkYvH17OKLgp4SLulf", 
        name="Martin Osborne 5", 
        category="Professional Voice Clone"
    )

    voice_assistant = VoiceAssistantWithSilenceDetection(
        vad=silero.VAD.load(),
        stt=openai.STT(
            base_url=os.environ["GROQ_BASE_URL"],
            api_key=os.environ["GROQ_API_KEY"],
            model="whisper-large-v3-turbo"
        ),
        llm=openai.LLM(
            base_url=os.environ["GROQ_BASE_URL"],
            api_key=os.environ["GROQ_API_KEY"],
            model="llama3-groq-70b-8192-tool-use-preview"
        ),
        tts=elevenlabs.TTS(
            model="eleven_multilingual_v2", 
            voice=voice
        ),
        chat_ctx=initial_context
    )


    log_queue = asyncio.Queue()


    @voice_assistant.on("user_speech_committed")
    @voice_assistant.on("agent_speech_committed")
    def on_agent_speech_committed(msg: llm.ChatMessage):
        content = msg.content
        if isinstance(content, list):
            content = {
                x.role: x.content for x in content if x.role != "system"
            }
        log_queue.put_nowait(content)

    async def write_transcription():
        conversation = []
        async with aiofiles.open("conversation.json", "w", encoding='utf-8') as f:
            while True:
                msg = await log_queue.get()
                if msg is None:
                    break
                conversation.append(msg)
            await f.write(json.dumps(conversation, ensure_ascii=False, indent=2))

    write_task = asyncio.create_task(write_transcription())

    async def finish_queue():
        log_queue.put_nowait(None)
        await write_task

    ctx.add_shutdown_callback(finish_queue)

    voice_assistant.start(ctx.room, participant)
    
    await voice_assistant.say("Hola Santi, ¿cómo estás?", allow_interruptions=True)


    # Keep the session running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    cli.run_app(
        opts=WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=os.environ["LIVEKIT_URL"],
            prewarm_fnc=prewarm
        )
    )