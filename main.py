import argparse
import sys
from utils.logger import setup_logger
from core.assistant import AssistantCore

logger = setup_logger("Main")

def run_cli_mode():
    """Runs interactive command line interface mode."""
    print("=" * 65)
    print("      AI-BASED OFFLINE DESKTOP ASSISTANT (CLI MODE)")
    print("=" * 65)
    print("Type a command or 'voice' to listen via microphone. Type 'exit' to quit.\n")

    assistant = AssistantCore(status_callback=lambda state, msg: print(f"[{state}] {msg}"))

    while True:
        try:
            user_input = input("\nUser Command > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting assistant. Goodbye!")
                break
            elif user_input.lower() == "voice":
                print("Listening for voice command...")
                response = assistant.listen_and_process_voice()
                print(f"Assistant Response: {response}")
            else:
                response = assistant.process_command_text(user_input)
                print(f"Assistant Response: {response}")
        except KeyboardInterrupt:
            print("\nTermination signal received. Exiting.")
            break
        except Exception as e:
            logger.error(f"CLI mode exception: {e}")

def main():
    parser = argparse.ArgumentParser(description="AI-Based Offline Desktop Assistant")
    parser.add_argument("--cli", action="store_true", help="Launch in Command-Line Interface mode")
    args = parser.parse_args()

    if args.cli:
        run_cli_mode()
    else:
        try:
            from gui.app import launch_gui
            launch_gui()
        except Exception as e:
            logger.error(f"Failed to launch GUI dashboard: {e}. Falling back to CLI mode.")
            run_cli_mode()

if __name__ == "__main__":
    main()
