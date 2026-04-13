#!/usr/bin/env python3
"""Main entry point for AI Assistant CLI"""
import sys
from .client import LMStudioClient
from .chat import ChatHistory
from .config import DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE


def print_welcome():
    """Print welcome message and instructions"""
    from .config import PERSONALITY_NAME
    
    print("\n" + "=" * 60)
    print(f"🎩 {PERSONALITY_NAME} - Your Personal AI Butler")
    print("=" * 60)
    print("Commands:")
    print("  /help     - Show this help message")
    print("  /clear    - Clear chat history")
    print("  /save     - Save chat history to file")
    print("  /load     - Load chat history from file")
    print("  /models   - List available models")
    print("  /model    - Switch to a different model")
    print("  /personality - Display current personality settings")
    print("  /quit     - Exit the assistant")
    print("=" * 60)
    print()


def main():
    """Main function to run the CLI assistant"""
    
    # Initialize client and chat
    client = LMStudioClient()
    chat = ChatHistory()
    
    print_welcome()
    
    # Check connection and get available models
    try:
        models = client.get_available_models()
        if models:
            print(f"✅ Connected to LM Studio")
            print(f"📦 Available models: {', '.join(models[:5])}")
            if len(models) > 5:
                print(f"   ... and {len(models) - 5} more")
            print(f"🎯 Using model: {client.model or models[0]}")
        else:
            print("⚠️  No models found in LM Studio. Please load a model first.")
    except Exception as e:
        print(f"❌ Cannot connect to LM Studio: {e}")
        print("Make sure LM Studio is running with server enabled on http://localhost:1234")
        print()
    
    print("Type your message and press Enter to chat.\n")
    
    while True:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                command = user_input.lower().split()[0]
                
                if command == '/quit' or command == '/exit':
                    print("\n👋 Goodbye!")
                    break
                
                elif command == '/help':
                    print_welcome()
                
                elif command == '/clear':
                    chat.clear()
                    print("🗑️  Chat history cleared.\n")
                
                elif command == '/save':
                    chat.save_to_file()
                    print("💾 Chat history saved.\n")
                
                elif command == '/load':
                    if chat.load_from_file():
                        print(f"📂 Loaded {chat.get_message_count()} messages from history.\n")
                    else:
                        print("No saved history found.\n")
                
                elif command == '/models':
                    models = client.get_available_models()
                    if models:
                        print("\n📦 Available models:")
                        for i, model in enumerate(models, 1):
                            marker = "✓" if model == (client.model or models[0]) else " "
                            print(f"  {marker} {i}. {model}")
                        print()
                    else:
                        print("No models available.\n")
                
                elif command == '/model':
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        print("Usage: /model <model_name>\n")
                    else:
                        new_model = parts[1]
                        available = client.get_available_models()
                        if new_model in available or not available:
                            client.model = new_model
                            print(f"🎯 Switched to model: {new_model}\n")
                        else:
                            print(f"Model '{new_model}' not found. Use /models to see available models.\n")
                
                elif command == '/personality':
                    from .config import PERSONALITY_NAME, PERSONALITY_DESCRIPTION
                    print(f"\n🎭 Current Personality: {PERSONALITY_NAME}")
                    print("-" * 60)
                    print(PERSONALITY_DESCRIPTION)
                    print("-" * 60 + "\n")
                
                else:
                    print(f"Unknown command: {command}. Type /help for available commands.\n")
                
                continue
            
            # Add user message to history
            chat.add_user_message(user_input)
            
            # Get response from AI
            print("🎩 Jarvis: ", end="", flush=True)
            
            try:
                full_response = ""
                response_stream = client.chat_completion(
                    messages=chat.get_messages(),
                    max_tokens=DEFAULT_MAX_TOKENS,
                    temperature=DEFAULT_TEMPERATURE,
                    stream=True
                )
                
                for chunk in response_stream:
                    print(chunk, end="", flush=True)
                    full_response += chunk
                
                print()  # New line after response
                
                # Add assistant response to history
                chat.add_assistant_message(full_response)
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Make sure LM Studio is running and a model is loaded.\n")
                # Remove the failed user message from history
                chat.messages.pop()
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
