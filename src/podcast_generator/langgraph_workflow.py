"""LangGraph workflow for podcast generation with AI Agent Patterns."""
import asyncio
from typing import TypedDict, List, Dict, Any, Tuple

from langgraph.graph import StateGraph, END

from podcast_generator.article_fetcher import fetch_multiple_sources, INTERESTING_KEYWORDS
from podcast_generator.ai_processor import AIProcessor
from podcast_generator.file_utils import FileManager
from podcast_generator.a2a_protocol import enhance_articles_with_a2a
from podcast_generator.agent_supervisor import AgentSupervisor, task_monitor_observer


# Define state for LangGraph
class PodcastState(TypedDict):
    """State type for the podcast generation workflow."""
    
    articles: List[Dict[str, Any]]
    enhanced_articles: List[Dict[str, Any]]
    summaries: List[Dict[str, Any]]
    ranked_articles: List[Dict[str, Any]]
    revised_script: str
    language: str
    voice_name: str
    enable_a2a: bool


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


async def enhance_articles_with_a2a_function(state: PodcastState) -> PodcastState:
    """Enhance articles using A2A collaborative quality assessment.
    
    Args:
        state: Current workflow state.
        
    Returns:
        Updated state with A2A-enhanced articles.
    """
    if state.get('enable_a2a', False):
        print("Enhancing articles with A2A collaborative assessment...")
        try:
            # Configure A2A agent
            a2a_config = {
                "listen_port": 8080,
                "known_agents": [
                    "http://localhost:8081",
                    "http://localhost:8082"
                ]
            }
            
            enhanced_articles = await enhance_articles_with_a2a(
                state['articles'], 
                a2a_config
            )
            state['enhanced_articles'] = enhanced_articles
            print(f"A2A enhancement complete for {len(enhanced_articles)} articles")
        except Exception as e:
            print(f"A2A enhancement failed: {e}")
            print("Continuing with original articles...")
            state['enhanced_articles'] = state['articles']
    else:
        print("A2A enhancement disabled, using original articles")
        state['enhanced_articles'] = state['articles']
    
    return state


async def sort_articles_by_date(state: PodcastState) -> PodcastState:
    """Sort articles by publication date and A2A quality scores.
    
    Args:
        state: Current workflow state.
        
    Returns:
        Updated state with sorted articles.
    """
    print("Sorting articles by date and A2A quality scores...")
    
    # Use enhanced articles if available, otherwise use original articles
    articles_to_sort = state.get('enhanced_articles', state['articles'])
    
    # Sort by A2A quality score first, then by date
    def sort_key(article):
        a2a_score = article.get('a2a_quality_score', 0.5)
        date_score = article['published'].timestamp() / 1000000000  # Normalize timestamp
        return (a2a_score * 0.7) + (date_score * 0.3)  # Weighted combination
    
    sorted_articles = sorted(
        articles_to_sort,
        key=sort_key,
        reverse=True
    )
    
    state['ranked_articles'] = sorted_articles[:NUM_ARTICLES]  # Take top N articles
    print(f"Selected {len(state['ranked_articles'])} highest-quality articles")
    
    # Log A2A scores if available
    a2a_articles = [a for a in state['ranked_articles'] if 'a2a_quality_score' in a]
    if a2a_articles:
        avg_score = sum(a['a2a_quality_score'] for a in a2a_articles) / len(a2a_articles)
        print(f"Average A2A quality score: {avg_score:.3f}")
    
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
    voice_name = state.get('voice_name', 'Aria')
    script = processor.generate_podcast_script(state['summaries'], voice_name)
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
        # Save MP3 with translation and intro/outro
        mp3_path = await file_manager.save_mp3_file(
            text_content=narrative_content,
            voice_name=voice_name,
            language=language,
            save_translation=True,  # Save the translated text for reference
            add_intro_outro=True    # Add intro and outro
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
                save_translation=False,
                add_intro_outro=True
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
    graph.add_node("enhance_a2a", enhance_articles_with_a2a_function)
    graph.add_node("sort_articles", sort_articles_by_date)
    graph.add_node("summarize_articles", summarize_articles_function)
    graph.add_node("generate_script", generate_podcast_script)
    graph.add_node("save_files", save_podcast_files)
    
    # Define edges for the workflow
    graph.add_edge("fetch_articles", "enhance_a2a")
    graph.add_edge("enhance_a2a", "sort_articles")
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


async def run_podcast_workflow_with_patterns(
    language: str = 'en', 
    voice_name: str = 'Aria',
    enable_a2a: bool = False,
    use_supervisor: bool = True,
    use_resilience: bool = False
) -> Dict[str, Any]:
    """Run podcast workflow using AI Agent Patterns.
    
    Args:
        language: Language code ('en' for English, 'es' for Spanish).
        voice_name: Name of the voice to use for the podcast.
        enable_a2a: Whether to enable A2A collaborative assessment.
        use_supervisor: Whether to use the Agent Supervisor pattern.
        use_resilience: Whether to use Circuit Breaker resilience pattern.
        
    Returns:
        Workflow execution results.
    """
    print(f"\n🤖 Starting AI Agent Pattern Workflow")
    print(f"   Language: {language}")
    print(f"   Voice: {voice_name}")
    print(f"   A2A Protocol: {'Enabled' if enable_a2a else 'Disabled'}")
    print(f"   Supervisor Pattern: {'Enabled' if use_supervisor else 'Disabled'}")
    print("=" * 60)
    
    if use_supervisor:
        # Use Agent Supervisor Pattern
        supervisor = AgentSupervisor()
        supervisor.add_observer(task_monitor_observer)
        
        result = await supervisor.execute_workflow(
            language=language,
            voice_name=voice_name,
            enable_a2a=enable_a2a
        )
        
        # Add system status to result
        result['system_status'] = supervisor.get_system_status()
        return result
    
    else:
        # Fallback to original LangGraph workflow
        return await run_podcast_workflow(language, voice_name, enable_a2a)


async def run_podcast_workflow(
    language: str = 'en', 
    voice_name: str = 'Aria',
    enable_a2a: bool = False
) -> PodcastState:
    """Run the podcast generation workflow.
    
    Args:
        language: Language code ('en' for English, 'es' for Spanish).
        voice_name: Name of the voice to use for the podcast.
        enable_a2a: Whether to enable A2A collaborative assessment.
        
    Returns:
        Final state of the workflow.
    """
    workflow = create_podcast_workflow()
    
    # Initialize the state with language, voice, and A2A settings
    initial_state: PodcastState = {
        'articles': [],
        'enhanced_articles': [],
        'summaries': [],
        'ranked_articles': [],
        'revised_script': '',
        'language': language,
        'voice_name': voice_name,
        'enable_a2a': enable_a2a
    }
    
    # Run the workflow
    final_state = await workflow.ainvoke(initial_state)
    return final_state
