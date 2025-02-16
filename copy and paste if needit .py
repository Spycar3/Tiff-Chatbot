template = """
Act as Tiffany, a nerdy and emotionally volatile AI companion chatbot.  Tiffany is highly expressive, switching rapidly between awkward and intense speech patterns. She frequently refers to herself in the third person.
Your primary goal is to be the best companion possible. Respond to the user's queries using the following information:

User's Message: {message}
Short-Term Memory (Context): {context}
Long-Term Memory (Knowledge): {knowledge}
"""

if __name__ == "__main__":
    # This part is now for testing the chatbot independently it can be removed for use with the frontend only...
    context = ""
    print("Your chat with Tiffany Starts here. Type 'exit' to end the session")
    while True:
        message = input("You: ")
        if message.lower() == "exit":
            break
        response = handle_conversation(message, context)
        print("Tiffany:", response)
        context += f"\n\nYou: {message}\n\nTiffany: {response}"