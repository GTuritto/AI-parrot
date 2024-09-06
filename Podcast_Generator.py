import os
import asyncio
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
import aiofiles
import csv
import math
import random
from gtts import gTTS
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()
news_api_key = os.getenv("NEWS_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
mistral_api_key = os.getenv("MISTRAL_API_KEY")
mistral_model = os.getenv("Mistral_Model_ID")

# Initialize Mistral for summarization and ranking
mistral_agent = ChatMistralAI(api_key=mistral_api_key, model=mistral_model)

# Number of news articles to fetch, summarize, and generate in the podcast
NUM_ARTICLES = 20  # Increased this to fetch more articles initially

# Define the date range (1 week old)
def is_within_last_two_weeks(published_date):
    two_weeks_ago = datetime.now() - timedelta(days=14)  # Expand to last 14 days
    return published_date >= two_weeks_ago

# Define keywords for interesting articles
interesting_keywords = ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "LLM", "GPT", "Large Language Model", "ChatGPT", "ChatGPT-4", "Mistral", "MistralAI", "Llama", "Ollama", "OpenAI", "Anthropic", "Claude", "AI Ethics", "AI Policy", "AI Regulation", "AI Governance"]

# Define state for LangGraph
class AgentState(TypedDict):
    articles: List[dict]
    summaries: List[dict]
    ranked_articles: List[dict]

# Function to fetch articles
async def fetch_articles_function(state):
    techcrunch_url = "https://techcrunch.com/tag/artificial-intelligence/feed/"
    feed = feedparser.parse(techcrunch_url)
    articles = []
    
    for entry in feed.entries[:30]:  # Fetch more articles to ensure we get enough interesting ones
        published = datetime(*entry.published_parsed[:6])
        if is_within_last_two_weeks(published):  # Use expanded two-week window
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'description': entry.summary,
                'published': published
            })
    state['articles'] = articles
    return state

# Function to rank articles using both recency and relevance
async def rank_articles_function(state):
    content = "\n\n".join([f"Article:\n{article['title']}: {article['description']}\n" for article in state['articles']])
    keywords = ", ".join(interesting_keywords)
    
    # Mistral prompt for relevance scoring
    prompt = f"Rate the relevance of the following articles based on these keywords: {keywords}. For each article, provide a score between 1 and 10.\n\n{content}"
    
    try:
        # Get relevance scores from Mistral
        response = mistral_agent.invoke([{"role": "user", "content": prompt}])
        relevance_scores = [int(score.strip()) for score in response.content.splitlines() if score.strip().isdigit()]
        
        # Define the weights for recency and relevance
        recency_weight = 0.5  # Reduced weight for recency to prioritize relevance more
        relevance_weight = 0.5
        max_days_old = 14  # Two-week range

        current_time = datetime.now()
        
        for i, article in enumerate(state['articles']):
            published = article['published']
            days_old = (current_time - published).days
            recency_score = max(0, 1 - days_old / max_days_old)  # Closer to 0 as the article gets older
            
            # Get relevance score, or 0 if no score was assigned
            relevance_score = relevance_scores[i] if i < len(relevance_scores) else 0
            
            # Adjust the final score calculation to give a small boost to all articles
            final_score = (recency_weight * recency_score) + (relevance_weight * (relevance_score / 10)) + 0.05  # Reducing strict filtering
            
            # Store the final score in the article dictionary
            article['final_score'] = final_score
        
        # Sort articles by final score in descending order (highest score first)
        state['ranked_articles'] = sorted(state['articles'], key=lambda x: x['final_score'], reverse=True)[:NUM_ARTICLES]
    
    except Exception as e:
        print(f"Error during ranking: {e}")
    
    return state

# Function to summarize articles using Mistral with retries
async def summarize_articles_function(state, max_retries=3):
    summarized_articles = []
    
    # Limit the number of articles to summarize (or summarize all)
    for article in state['ranked_articles'][:NUM_ARTICLES]:  # Ensures NUM_ARTICLES are summarized
        content = f"{article['title']}: {article['description']}"
        prompt = f"Summarize the following article, focusing on key points about artificial intelligence and its applications:\n\n{content}"
        retries = 0
        
        while retries < max_retries:
            try:
                response = mistral_agent.invoke([{"role": "user", "content": prompt}])
                article['summary'] = response.content
                summarized_articles.append(article)
                break
            except Exception as e:
                retries += 1
                print(f"Error summarizing article: {e}. Retry {retries}/{max_retries}")
        
        if retries == max_retries:
            article['summary'] = "Summary could not be generated."
            summarized_articles.append(article)
    
    state['summaries'] = summarized_articles
    return state

# Define conditional function to decide retry logic
def should_retry_summarization(state):
    if len(state['summaries']) > 0:
        return "save_csv"
    return "summarize_articles"

# Function to generate and revise the podcast script using AI in one step
def generate_and_revise_podcast_script(state):
    intro_variations = [
        "In other news,", "Next up,", "Moving on to the next story,", "Here’s another update,", 
        "Another interesting development,", "Meanwhile,", "Shifting gears to our next story,", 
        "Let’s turn to the next topic,"
    ]
    commentary_variations = [
        "It's fascinating to see how this story is evolving and shaping the AI landscape. Let’s keep an eye on this as more developments unfold.",
        "This is a key development in the AI field, and it's sure to have a big impact moving forward.",
        "It’s amazing to witness how quickly things are changing with AI. We’ll be sure to follow this story as it develops.",
        "What a significant update! AI continues to drive innovations, and this is something to watch closely.",
        "The AI landscape is being transformed with stories like this, and it’s certainly exciting to see where it’s heading."
    ]
    
    # Generate the initial script
    script = "Welcome to the latest episode of 'Artificial Intelligence Today', where we bring you the top stories and trends in artificial intelligence. Let's dive right into the headlines that are shaping the future of technology.\n\n"
    
    first_article = state['summaries'][0]
    script += f"{first_article['title']}\n{first_article['summary']}\n{random.choice(commentary_variations)}\n\n"
    
    # Use NUM_ARTICLES to control how many articles are included in the script
    for article in state['summaries'][1:NUM_ARTICLES]:
        script += f"{random.choice(intro_variations)}\n{article['title']}\n{article['summary']}\n{random.choice(commentary_variations)}\n\n"
    
    script += "And that’s a wrap for this AI news highlights. Stay tuned for more updates and stories that are defining the future of artificial intelligence. Thanks for listening, and until next time, stay curious and stay informed!"
    
    # Revise the script using AI for better flow and style
    prompt = f"""
    You are a professional radio host. Revise the following podcast script to make it sound more engaging, friendly, and professional for a radio show audience. Keep the tone conversational but polished.

    Here's the script:

    {script}

    Revise the script to make it sound more engaging, friendly, and professional for the podcast audience, but keep the tone conversational and polished.
    """
    
    try:
        # Send the script to Mistral AI for revision
        response = mistral_agent.invoke([{"role": "user", "content": prompt}])
        revised_script = response.content
        state['revised_script'] = revised_script  # Store the revised script in state
    except Exception as e:
        print(f"Error revising podcast script: {e}")
        state['revised_script'] = script  # Use the original script if revision fails

    return state  # Return the updated state instead of the script

# Function to save the revised podcast script
async def save_podcast_script_function(state):
    script_directory = "PodcastScript"
    os.makedirs(script_directory, exist_ok=True)  # Ensure the directory exists
    current_date = datetime.now().strftime("%Y%m%d")
    
    # Ensure the script is generated and revised only once
    if 'revised_script' not in state:  # Check if revised script exists
        state = generate_and_revise_podcast_script(state)  # Generate if not present
    
    # Save the revised script to a file
    script_filepath = os.path.join(script_directory, f"AIpodcast_{current_date}.txt")
    async with aiofiles.open(script_filepath, "w") as file:
        await file.write(state['revised_script'])  # Write the revised script to file
    print(f"Revised podcast script saved to: {script_filepath}")
    
    return state

# Function to convert the revised script to MP3
def convert_script_to_mp3(state):
    script_directory = "PodcastScript"
    os.makedirs(script_directory, exist_ok=True)  # Ensure the directory exists
    current_date = datetime.now().strftime("%Y%m%d")
    
    # Ensure the script is generated and revised only once
    if 'revised_script' not in state:  # Check if revised script exists
        state = generate_and_revise_podcast_script(state)  # Generate if not present
    
    # Convert the revised script to an MP3 file
    mp3_filepath = os.path.join(script_directory, f"AIpodcast_{current_date}.mp3")
    tts = gTTS(state['revised_script'], lang='en')  # Generate the MP3 from the revised script
    tts.save(mp3_filepath)
    print(f"Revised podcast script converted to MP3 and saved to: {mp3_filepath}")
    
    return state

# Function to save articles to CSV
def save_articles_to_csv_function(state):
    script_directory = "PodcastScript"
    os.makedirs(script_directory, exist_ok=True)
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"AIpodcast_{current_date}.csv"
    filepath = os.path.join(script_directory, filename)
    
    headers = ["Title", "Summary", "Link"]
    
    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        for article in state['summaries']:
            writer.writerow({
                "Title": article["title"],
                "Summary": article.get("summary", "Summary not available"),
                "Link": article["link"]
            })
    
    print(f"Articles list saved to: {filepath}")
    return state

# Define the graph
graph = StateGraph(AgentState)

# Add nodes to the graph
graph.add_node("fetch_articles", fetch_articles_function)
graph.add_node("rank_articles", rank_articles_function)
graph.add_node("summarize_articles", summarize_articles_function)
graph.add_node("save_csv", save_articles_to_csv_function)
graph.add_node("generate_and_revise_podcast_script", generate_and_revise_podcast_script)
graph.add_node("save_podcast_script", save_podcast_script_function)
graph.add_node("convert_to_mp3", convert_script_to_mp3)

# Define edges for the workflow
graph.add_edge("fetch_articles", "rank_articles")
graph.add_edge("rank_articles", "summarize_articles")
graph.add_conditional_edges("summarize_articles", should_retry_summarization, {"save_csv": "save_csv", "retry": "summarize_articles"})
graph.add_edge("save_csv", "generate_and_revise_podcast_script")  # Ensure state is passed here
graph.add_edge("generate_and_revise_podcast_script", "save_podcast_script")  # Revised script is in the state
graph.add_edge("save_podcast_script", "convert_to_mp3")  # Use the same state for MP3 conversion

# Set the entry point
graph.set_entry_point("fetch_articles")

# Compile the graph
app = graph.compile()

# Invoke the workflow using async method (ainvoke)
async def run_workflow():
    await app.ainvoke({"articles": [], "summaries": [], "ranked_articles": []})

# Main event loop
asyncio.run(run_workflow())
