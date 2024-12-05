from agent.cold_call_agent import initiate_call, handle_conversation
import asyncio

def main():
    """Main function to run the cold call agent."""
    lead_phone_number = input("Enter the lead's phone number: ")

    # Step 1: Initiate Call
    initiate_call(lead_phone_number)

    # Step 2: Handle the conversation
    asyncio.run(handle_conversation())

if __name__ == "__main__":
    main()