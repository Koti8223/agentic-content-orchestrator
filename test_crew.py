import os
from dotenv import load_dotenv
from agents import run_content_studio

# Load environment variables
load_dotenv()

def main():
    print("==================================================")
    print("Testing the Multi-Agent Content Studio Pipeline...")
    print("==================================================")
    
    topic = "Python Decorators"
    provider = "Google Gemini"
    api_key = os.getenv("GOOGLE_API_KEY")
    
    print(f"Topic: {topic}")
    print(f"Provider: {provider}\n")
    print("Running agents (this will take 1-2 minutes as agents research, write, and edit)...")
    
    if not api_key:
        print("[ERROR] GOOGLE_API_KEY not found in .env file. Please check your setup.")
        return

    try:
        result = run_content_studio(topic, provider, api_key, "Technical & In-Depth")
        print("\n================ FINAL OUTPUT ================")
        print(result["output"])
        print("\n================ METRICS =====================")
        print(f"Total Tokens: {result['total_tokens']}")
        print("==============================================")
        print("\nPipeline test completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Pipeline test failed: {e}")
        print("Please check your GOOGLE_API_KEY in the .env file and ensure you are connected to the internet.")

if __name__ == "__main__":
    main()
