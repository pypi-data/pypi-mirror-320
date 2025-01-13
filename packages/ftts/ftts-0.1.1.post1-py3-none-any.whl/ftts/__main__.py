from jsonargparse import CLI
from .utils.prepare_model import (
    prepare_chattts,
    clear_cache,
    download,
    prepare_stream_chattts,
)
from .services.realtime import serve_realtime_chattts


def main():
    commands = {
        "prepare": {
            "chattts": prepare_chattts,
            "_help": "Prepare tts models",
            "stream-chattts": prepare_stream_chattts,
        },
        "clear": clear_cache,
        "download": download,
        "serve": {"chattts": serve_realtime_chattts, "_help": "Serve realtime tts"},
    }

    CLI(components=commands)


if __name__ == "__main__":
    main()
