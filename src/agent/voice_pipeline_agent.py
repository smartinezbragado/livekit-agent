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
    llm,

)
from livekit.rtc import RemoteParticipant
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
        self.last_message_time = datetime.now()

    async def monitor_inactivity(self):
        while True:
            await asyncio.sleep(5) 
            elapsed = (datetime.now() - self.last_message_time).total_seconds()
            if elapsed > 60: 
                logger.warning("User inactive for more than 10 seconds. Shutting down.")
                await self.shutdown_callback()
                break

    def start_monitoring(self, shutdown_callback):
        logger.warning("Starting monitoring")
        self.shutdown_callback = shutdown_callback
        self.monitor_task = asyncio.create_task(self.monitor_inactivity())


    async def stop_monitoring(self):
        logger.warning("Stopping monitoring")
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass


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
        id="tXgbXPnsMpKXkuTgvE3h", 
        name="Elena - Stories and Narrations", 
        category="Professional Voice Clone"
    )

    voice_assistant = VoiceAssistantWithSilenceDetection(
        vad=ctx.proc.userdata["vad"],
        stt=openai.STT(
            base_url=os.environ["GROQ_BASE_URL"],
            api_key=os.environ["GROQ_API_KEY"],
            model="whisper-large-v3-turbo",
            detect_language=True
        ),
        llm=openai.LLM(
            base_url=os.environ["GROQ_BASE_URL"],
            api_key=os.environ["GROQ_API_KEY"],
            model="llama-3.1-70b-versatile"
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
        log_queue.put_nowait({
            msg.role: msg.content
        })
        voice_assistant.last_message_time = datetime.now()

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

    async def shutdown():
        await voice_assistant.stop_monitoring()
        await ctx.disconnect()
        logger.warning("Connection has been shut down.")

    # Start the inactivity monitoring
    voice_assistant.start_monitoring(shutdown_callback=shutdown)

    # Handle participant disconnection
    @ctx.room.on('participant_disconnected')
    async def on_participant_disconnected(participant_left: RemoteParticipant):
        if participant_left.identity == participant.identity:
            logger.info(f"Participant {participant_left.identity} has left the room.")
            await shutdown()

    voice_assistant.start(ctx.room, participant)
    
    await voice_assistant.say("Hola Santi, ¿cómo estás?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(
        opts=WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=os.environ["LIVEKIT_URL"],
            prewarm_fnc=prewarm
        )
    )