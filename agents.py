import os
# Monkey-patch CrewAI's prompt caching to prevent 'cache_breakpoint' from breaking unsupported providers (like Groq)
try:
    import crewai.llms.cache as _crewai_cache
    _crewai_cache.mark_cache_breakpoint = lambda msg: msg
except Exception:
    pass

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# Load environment variables from .env file
load_dotenv()

# Define the custom search tool using the @tool decorator
@tool("Web Search Tool")
def search_tool(query: str) -> str:
    """Search the web for a given query to fetch the latest facts and technical details."""
    return DuckDuckGoSearchRun().run(query)

def run_content_studio(topic: str, provider: str, api_key: str, tone: str, callbacks: dict = None) -> dict:
    """
    Executes the multi-agent content crew dynamically on a given topic,
    using the specified LLM provider, user's API key, and preferred content tone.
    Returns a dictionary containing the finalized output text and token usage details.
    """
    # Map user selection to LiteLLM strings
    provider_mapping = {
        "Google Gemini": "gemini/gemini-flash-latest",
        "OpenAI": "openai/gpt-4o-mini",
        "Anthropic Claude": "anthropic/claude-3-5-haiku-20241022",
        "Groq": "groq/llama-3.3-70b-versatile"
    }
    
    model_name = provider_mapping.get(provider, "gemini/gemini-flash-latest")
    
    # Instantiate the LLM dynamically
    llm = LLM(
        model=model_name,
        temperature=0.5,
        api_key=api_key,
        max_retries=5
    )
    
    # Define specialized AI Agents
    researcher = Agent(
        role="Senior Technology Researcher",
        goal="Search the web and gather in-depth, accurate information on: {topic}",
        backstory=(
            "You are an expert researcher with a knack for analyzing complex technical topics. "
            "Your job is to find the latest trends, reliable documentation, and factual data "
            "about the given topic. You separate hype from actual facts."
        ),
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    writer = Agent(
        role="Professional Tech Content Creator",
        goal=f"Write engaging, structured, and easy-to-read content about: {{topic}} maintaining a strict {tone} tone.",
        backstory=(
            f"You are a skilled content writer who specializes in making technical concepts "
            f"simple and interesting. You write in a strict {tone} tone, avoiding clickbait. "
            f"You structure your content with clean Markdown."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    editor = Agent(
        role="Senior Editorial Director",
        goal=f"Review, refine, and quality check the generated content about: {{topic}} keeping the {tone} style.",
        backstory=(
            f"You are a meticulous editor with a sharp eye for formatting, grammar, clarity, and flow. "
            f"Your job is to ensure that the content is top-tier and matches a professional {tone} style. "
            f"You polish the final blog post, LinkedIn post, and tweets."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # Define task completed callbacks to invoke frontend updates
    def research_completed_callback(output):
        if callbacks and "on_research_complete" in callbacks:
            callbacks["on_research_complete"]()

    def write_completed_callback(output):
        if callbacks and "on_write_complete" in callbacks:
            callbacks["on_write_complete"]()

    def edit_completed_callback(output):
        if callbacks and "on_edit_complete" in callbacks:
            callbacks["on_edit_complete"]()

    # Define Tasks
    research_task = Task(
        description=(
            "Conduct comprehensive research on the topic: '{topic}'. "
            "Use the search tool exactly ONCE to find the most recent facts, key concepts, "
            "code examples (if applicable), and why it matters. Do not run multiple search queries. "
            "Organize your findings into a clear, detailed bullet-point summary."
        ),
        expected_output="A structured markdown document containing key facts, trends, and details about the topic.",
        agent=researcher,
        callback=research_completed_callback
    )

    write_task = Task(
        description=(
            f"Using the research provided by the Researcher, write a comprehensive piece of content. "
            f"You MUST generate three separate pieces of content in a strict {tone} tone. "
            f"To keep these pieces clearly separated, you MUST use the following exact headers:\n"
            f"# SECTION: BLOG POST\n"
            f"for the blog post.\n"
            f"# SECTION: LINKEDIN POST\n"
            f"for the LinkedIn post.\n"
            f"# SECTION: TWITTER THREAD\n"
            f"for the Twitter/X thread.\n\n"
            f"1. **Blog Post**: An educational, engaging article of 400-600 words with headings and examples.\n"
            f"2. **LinkedIn Post**: A professional summary (150-250 words) with key takeaways and relevant hashtags.\n"
            f"3. **Twitter/X Thread**: A thread of 3-4 tweets breaking down the core message.\n\n"
            f"Maintain a clean, professional, yet {tone} tone. Do not use generic placeholders.\n\n"
            f"Do not write duplicate drafts. Generate exactly ONE version of each of the three formats."
        ),
        expected_output="A single markdown document containing the blog post, LinkedIn post, and Twitter thread separated by the exact headers: # SECTION: BLOG POST, # SECTION: LINKEDIN POST, and # SECTION: TWITTER THREAD.",
        agent=writer,
        callback=write_completed_callback
    )

    edit_task = Task(
        description=(
            f"Review the content drafted by the Writer. "
            f"1. Check for spelling, grammatical errors, and technical accuracy.\n"
            f"2. Verify that the blog post, LinkedIn post, and Twitter thread are all present.\n"
            f"3. Clean up any awkward sentences or overly generic AI phrasing.\n"
            f"4. Format the final output beautifully, ensuring it fits a {tone} tone.\n"
            f"5. You MUST preserve or add the exact header markers to separate the sections:\n"
            f"# SECTION: BLOG POST\n"
            f"# SECTION: LINKEDIN POST\n"
            f"# SECTION: TWITTER THREAD\n"
            f"Do not omit or modify these headers, as they are crucial for the frontend parser.\n"
            f"6. Output ONLY the finalized, edited content inside these three sections. Do NOT include conversational filler, introductory remarks, or both the original and edited drafts. Any duplicate or original text blocks MUST be discarded, leaving only the polished version."
        ),
        expected_output=(
            "The polished and finalized markdown document containing the Blog Post, "
            "LinkedIn Post, and Twitter thread, separated by the exact headers: "
            "# SECTION: BLOG POST, # SECTION: LINKEDIN POST, and # SECTION: TWITTER THREAD."
        ),
        agent=editor,
        callback=edit_completed_callback
    )

    max_rpm = 3 if "gemini" in model_name else 10
    
    # Create the Crew
    content_crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, write_task, edit_task],
        process=Process.sequential,
        memory=False,
        verbose=True,
        max_rpm=max_rpm
    )

    inputs = {"topic": topic}
    result = content_crew.kickoff(inputs=inputs)
    
    # Extract token usage details safely from CrewOutput
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    
    if hasattr(result, "token_usage") and result.token_usage:
        try:
            usage = result.token_usage
            if hasattr(usage, "prompt_tokens"):
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens
            elif isinstance(usage, dict):
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
        except Exception:
            pass
            
    return {
        "output": str(result),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens
    }
