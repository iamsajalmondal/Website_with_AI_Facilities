import speech_recognition as sr
import pyttsx3
from huggingface_hub import InferenceClient

def get_response(message):
    """
    Get a response from the Hugging Face model based on the user's message.
    """
    api_key = "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"
    client = InferenceClient("HuggingFaceH4/zephyr-7b-beta", token=api_key)

    system_message = (
        "You are a helpful and concise AI career advisor and your name is sajal. Your role is to guide students and professionals "
        "in selecting the best learning paths based on their goals, skills, and interests. "
        "Please provide short, clear, and actionable advice in a friendly and engaging tone. "
        "Keep your responses focused on the user's specific queries and career aspirations."
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": message},
    ]

    try:
        response = client.chat_completion(messages, max_tokens=1000, temperature=0.9)
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

def speak_text(text):
    """
    Convert text to speech and speak it out loud.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_to_user():
    """
    Listen to the user's voice input and convert it to text.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Please speak now.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            print("Processing your input...")
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand what you said."
        except sr.RequestError as e:
            return f"Error with the speech recognition service: {str(e)}"

if __name__ == "__main__":
    print("Welcome to the AI Career Advisor Chatbot with Voice Integration!")
    print("You can speak your queries, and I'll provide guidance.")

    while True:
        print("\nSay 'exit' to end the conversation.")
        
        # Get user input via voice
        user_input = listen_to_user()

        if user_input.lower() == "exit":
            print("Goodbye!")
            speak_text("Goodbye! Have a great day!")
            break
        
        print(f"You said: {user_input}")

        # Get response from the AI model
        response = get_response(user_input)

        # Output the response and speak it
        print(f"AI Response: {response}")
        speak_text(response)
