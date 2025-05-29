"""LangGraph workflow for podcast generation."""
import asyncio
from typing import TypedDict, List, Dict, Any, Tuple

from langgraph.graph import StateGraph, END

from podcast_generator.article_fetcher import fetch_multiple_sources, INTERESTING_KEYWORDS
from podcast_generator.ai_processor import AIProcessor
from podcast_generator.file_utils import FileManager


# Define state for LangGraph
class PodcastState(TypedDict):
    """State type for the podcast generation workflow."""
    
    articles: List[Dict[str, Any]]
    summaries: List[Dict[str, Any]]
    ranked_articles: List[Dict[str, Any]]
    revised_script: str
    language: str
    voice_name: str


# Number of articles to include in the final podcast (10-12 articles)
NUM_ARTICLES = 12


# Define node functions for the LangGraph workflow
async def fetch_articles_function(state: PodcastState) -> PodcastState:
    """Fetch articles from multiple sources.
    
    Args:
        state: Current workflow state.
        
    Returns:
        Updated state with fetched articles.
    """
    print("Fetching articles...")
    articles = await fetch_multiple_sources()
    print(f"Fetched {len(articles)} articles")
    state['articles'] = articles
    return state


async def sort_articles_by_date(state: PodcastState) -> PodcastState:
    """Sort articles by publication date (newest first).
    
    Args:
        state: Current workflow state.
        
    Returns:
        Updated state with sorted articles.
    """
    print("Sorting articles by date...")
    # Sort articles by published date (newest first)
    sorted_articles = sorted(
        state['articles'],
        key=lambda x: x['published'],
        reverse=True
    )
    state['ranked_articles'] = sorted_articles[:NUM_ARTICLES]  # Take most recent N articles
    print(f"Selected {len(state['ranked_articles'])} most recent articles")
    return state


async def summarize_articles_function(state: PodcastState) -> PodcastState:
    """Summarize articles using AI.
    
    Args:
        state: Current workflow state.
        
    Returns:
        Updated state with summarized articles.
    """
    print("Summarizing articles...")
    processor = AIProcessor()
    summarized_articles = []
    
    for article in state['ranked_articles']:
        article_copy = article.copy()
        summary = processor.summarize_article(article_copy)
        article_copy['summary'] = summary
        summarized_articles.append(article_copy)
    
    state['summaries'] = summarized_articles
    print(f"Summarized {len(summarized_articles)} articles")
    return state


def should_retry_summarization(state: PodcastState) -> str:
    """Decide whether to retry summarization or proceed.
    
    Args:
        state: Current workflow state.
        
    Returns:
        Next node name.
    """
    if len(state.get('summaries', [])) > 0:
        return "save_csv"
    return "summarize_articles"


def generate_podcast_script(state: PodcastState) -> PodcastState:
    """Generate a podcast script from article summaries.
    
    Args:
        state: Current workflow state.
        
    Returns:
        Updated state with generated podcast script.
    """
    print("Generating podcast script...")
    processor = AIProcessor()
    script = processor.generate_podcast_script(state['summaries'])
    revised_script = processor.revise_podcast_script(script)
    state['revised_script'] = revised_script
    print("Podcast script generated and revised")
    return state


async def save_podcast_files(state: PodcastState) -> PodcastState:
    """Save podcast files (narrative version and MP3).
    
    Args:
        state: Current workflow state.
        
    Returns:
        Updated state after saving files.
    """
    print("Saving podcast files...")
    file_manager = FileManager()
    
    # Get language and voice from state (default to English and Aria if not set)
    language = state.get('language', 'en')
    voice_name = state.get('voice_name', 'Aria')
    
    # Save clean narrative version (using the revised script as source)
    narrative_path = await file_manager.save_narrative_file(
        content=state['revised_script'],
        language=language
    )
    print(f"Saved {language.upper()} narrative script to: {narrative_path}")
    
    # Save MP3 using the narrative version
    with open(narrative_path, 'r', encoding='utf-8') as f:
        narrative_content = f.read()
    
    print(f"Generating audio with voice: {voice_name}")
    
    try:
        # Save MP3 with translation if needed
        mp3_path = await file_manager.save_mp3_file(
            text_content=narrative_content,
            voice_name=voice_name,
            language=language,
            save_translation=True  # Save the translated text for reference
        )
        print(f"✓ Successfully generated podcast MP3: {mp3_path}")
        
    except Exception as e:
        print(f"Error generating podcast audio: {str(e)}")
        # Fall back to English if Spanish fails
        if language == 'es':
            print("Falling back to English...")
            mp3_path = await file_manager.save_mp3_file(
                text_content=state['revised_script'],  # Use original English text
                voice_name=voice_name,
                language='en',
                save_translation=False
            )
            print(f"✓ Successfully generated English podcast MP3: {mp3_path}")
    
    return state


def create_podcast_workflow() -> StateGraph:
    """Create the podcast generation workflow graph.
    
    Returns:
        Compiled LangGraph workflow.
    """
    # Create the graph
    graph = StateGraph(PodcastState)
    
    # Add nodes to the graph
    graph.add_node("fetch_articles", fetch_articles_function)
    graph.add_node("sort_articles", sort_articles_by_date)
    graph.add_node("summarize_articles", summarize_articles_function)
    graph.add_node("generate_script", generate_podcast_script)
    graph.add_node("save_files", save_podcast_files)
    
    # Define edges for the workflow
    graph.add_edge("fetch_articles", "sort_articles")
    graph.add_edge("sort_articles", "summarize_articles")
    graph.add_conditional_edges(
        "summarize_articles", 
        should_retry_summarization, 
        {
            "save_csv": "generate_script",
            "summarize_articles": "summarize_articles"
        }
    )
    graph.add_edge("generate_script", "save_files")
    graph.add_edge("save_files", END)
    
    # Set the entry point
    graph.set_entry_point("fetch_articles")
    
    # Compile the graph
    return graph.compile()


async def run_podcast_workflow(language: str = 'en', voice_name: str = 'Aria') -> PodcastState:
    """Run the podcast generation workflow.
    
    Args:
        language: Language code ('en' for English, 'es' for Spanish).
        voice_name: Name of the voice to use for the podcast.
        
    Returns:
        Final state of the workflow.
    """
    workflow = create_podcast_workflow()
    
    # Initialize the state with language and voice settings
    initial_state: PodcastState = {
        'articles': [],
        'summaries': [],
        'ranked_articles': [],
        'revised_script': '',
        'language': language,
        'voice_name': voice_name
    }
    
    # Run the workflow
    final_state = await workflow.ainvoke(initial_state)
    return final_state
