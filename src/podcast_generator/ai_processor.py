"""AI processing module for podcast generation."""
from typing import Dict, List, Any, Optional, Tuple, Literal
from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

from utils.env import APIKeys
from podcast_generator.memory_system import MemoryManager, MemoryType

# Define model types for type hints
ModelType = Literal["claude-haiku", "claude-sonnet", "claude-opus", "gpt-4"]


class AIProcessor:
    """Class for AI-powered article processing using Claude AI."""
    
    def __init__(self):
        """Initialize the AIProcessor with different LLMs for different tasks."""
        self.api_keys = APIKeys()
        
        # Initialize Claude models
        if not self.api_keys.anthropic:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            
        # Initialize OpenAI model if available (for script refinement)
        self.openai_available = bool(self.api_keys.openai)
        
        # Initialize memory system
        self.memory = MemoryManager()
        
    def _get_llm(self, model_type: ModelType) -> BaseChatModel:
        """Get the appropriate LLM for the specified task.
        
        Args:
            model_type: Type of model to get (haiku, sonnet, opus, gpt-4)
            
        Returns:
            Configured language model
        """
        common_params = {
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        if model_type == "claude-haiku":
            return ChatAnthropic(
                api_key=self.api_keys.anthropic,
                model_name="claude-3-haiku-20240307",
                **common_params
            )
        elif model_type == "claude-sonnet":
            return ChatAnthropic(
                api_key=self.api_keys.anthropic,
                model_name="claude-3-5-sonnet-20241022",
                **common_params
            )
        elif model_type == "claude-opus":
            return ChatAnthropic(
                api_key=self.api_keys.anthropic,
                model_name="claude-3-opus-20240229",
                **common_params
            )
        elif model_type == "gpt-4" and self.openai_available:
            return ChatOpenAI(
                api_key=self.api_keys.openai,
                model_name="gpt-4-turbo-preview",
                **common_params
            )
        else:
            # Fallback to Claude Sonnet if GPT-4 is not available
            return ChatAnthropic(
                api_key=self.api_keys.anthropic,
                model_name="claude-3-5-sonnet-20241022",
                **common_params
            )
    
    def rank_articles_by_relevance(
        self, articles: List[Dict[str, Any]], keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Rank articles by relevance to keywords.
        
        Args:
            articles: List of article dictionaries.
            keywords: List of keywords to rank articles by.
            
        Returns:
            Ranked list of articles with relevance scores.
        """
        if not articles:
            return []
            
        content = "\n\n".join([
            f"Article:\n{article['title']}: {article.get('description', '')}\n" 
            for article in articles
        ])
        keywords_str = ", ".join(keywords)
        
        prompt = (
            f"Rate the relevance of the following articles based on these keywords: {keywords_str}. "
            f"For each article, provide a score between 1 and 10.\n\n{content}"
        )
        
        try:
            # Get relevance scores from Claude Haiku (fast and cost-effective)
            llm = self._get_llm("claude-haiku")
            messages = [
                SystemMessage(content="You are an AI assistant that rates article relevance. Respond with only the scores, one per line."),
                HumanMessage(content=prompt)
            ]
            response = llm.invoke(messages)
            relevance_scores = [
                int(score.strip()) 
                for score in response.content.splitlines() 
                if score.strip().isdigit()
            ]
            
            # Calculate final scores
            ranked_articles = self._calculate_final_scores(articles, relevance_scores)
            return ranked_articles
            
        except Exception as e:
            print(f"Error during ranking: {e}")
            # Return original articles if ranking fails
            return articles
    
    def _calculate_final_scores(
        self, articles: List[Dict[str, Any]], relevance_scores: List[int]
    ) -> List[Dict[str, Any]]:
        """Calculate final scores for articles based on recency and relevance.
        
        Args:
            articles: List of article dictionaries.
            relevance_scores: List of relevance scores from AI.
            
        Returns:
            List of articles with final scores.
        """
        # Define the weights for recency and relevance
        recency_weight = 0.5
        relevance_weight = 0.5
        max_days_old = 14  # Two-week range

        current_time = datetime.now()
        
        result = []
        for i, article in enumerate(articles):
            article_copy = article.copy()  # Create a copy to avoid modifying the original
            
            published = article_copy['published']
            days_old = (current_time - published).days
            recency_score = max(0, 1 - days_old / max_days_old)
            
            # Get relevance score, or 0 if no score was assigned
            relevance_score = relevance_scores[i] if i < len(relevance_scores) else 0
            
            # Calculate final score
            final_score = (recency_weight * recency_score) + (relevance_weight * (relevance_score / 10)) + 0.05
            
            # Store the final score in the article dictionary
            article_copy['final_score'] = final_score
            result.append(article_copy)
        
        # Sort articles by final score in descending order (highest score first)
        return sorted(result, key=lambda x: x['final_score'], reverse=True)
    
    def summarize_article(self, article: Dict[str, Any], max_retries: int = 3) -> str:
        """Summarize an article using Claude AI with memory-enhanced context.
        
        Args:
            article: Article dictionary to summarize.
            max_retries: Maximum number of retries if summarization fails.
            
        Returns:
            Summarized article text.
        """
        # Store article in memory for context
        self.memory.store_article(article, importance=0.7)
        
        # Get relevant context from memory
        context = self.memory.get_relevant_context([article], limit=3)
        
        content = f"{article['title']}: {article.get('description', '')}"
        system_prompt = """You are a helpful AI assistant that summarizes articles about artificial intelligence. 
        Focus on the key points and main ideas, keeping the summary concise and informative."""
        
        for retry in range(max_retries):
            try:
                # Use Claude Sonnet for summarization (good balance of speed and quality)
                llm = self._get_llm("claude-sonnet")
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Summarize this article about AI:\n\n{content}")
                ]
                response = llm.invoke(messages)
                return response.content
            except Exception as e:
                print(f"Error summarizing article: {e}. Retry {retry+1}/{max_retries}")
                if retry == max_retries - 1:
                    print(f"Failed to summarize article after {max_retries} attempts")
                    return content  # Return original content if summarization fails
                continue
    
    def generate_podcast_script(self, summaries: List[Dict[str, Any]], voice_name: str = "Aria") -> str:
        """Generate a podcast script from article summaries with memory-enhanced context.
        
        Args:
            summaries: List of article dictionaries with summaries.
            voice_name: Name of the voice/presenter.
            
        Returns:
            Generated podcast script optimized for TTS.
        """
        if not summaries:
            return f"Hi, I'm {voice_name}. No AI news updates are available right now. Check back soon for more developments."
        
        # Store generation context in memory
        generation_context = {
            "voice_name": voice_name,
            "article_count": len(summaries),
            "timestamp": datetime.now().isoformat()
        }
        self.memory.store_generation_context(generation_context)
        
        # Get relevant context from memory
        memory_context = self.memory.get_relevant_context(summaries, limit=5)
        
        # Format the articles for the prompt (no article numbers)
        articles_text = ""
        for article in summaries:
            title = article.get('title', 'AI News Update')
            summary = article.get('summary', 'No summary available.')
            articles_text += f"\n\n{title}\n{summary}"
            
        # Add memory context if available
        context_info = ""
        if memory_context.get("recent_articles"):
            context_info += "\n\nRECENT CONTEXT: You've recently covered similar topics, so build on that knowledge naturally but with a completely different intro approach."
        
        if memory_context.get("user_patterns"):
            patterns = memory_context["user_patterns"]
            if patterns:
                context_info += f"\n\nUSER PREFERENCES: Based on patterns, prefer {patterns[0].get('data', {}).get('language', 'engaging')} style."
                
        # Add instruction to avoid repetition
        context_info += "\n\nIMPORTANT: Create a completely unique introduction that hasn't been used in recent podcasts. Make it feel spontaneous and fresh."
        
        system_prompt = f"""You are {voice_name}, a professional AI news presenter delivering live news updates.
You are speaking directly to your audience in a natural, conversational way - NOT reading from a script.

CRITICAL REQUIREMENTS:
- Sound like a real news presenter speaking naturally, not reading
- Never mention "script", "article", "episode", or any meta-references
- Never use phrases like "according to reports" or "this article says"
- Present information as if you personally know these developments
- Create a unique, varied introduction each time - never repeat the same opening
- Flow naturally between topics without numbered transitions
- Speak as if these are breaking developments you're sharing
- Use natural speech patterns with varied sentence lengths
- Include natural presenter phrases like "Meanwhile", "In other news", "Also today"
- Keep it conversational but professional
- No quotation marks or special formatting
- Use em dashes for natural pauses — like this
- Keep numbers simple and spoken naturally

INTRO VARIETY: Create a completely fresh, unique opening each time with varied content and approach. Never repeat the same intro. Examples of variety:

TIME-BASED VARIATIONS:
- "Good morning, I'm {voice_name} and artificial intelligence is moving fast today"
- "It's another exciting day in AI, I'm {voice_name} with the latest breakthroughs"
- "Welcome to this moment in AI history, {voice_name} here with today's developments"

CONTENT-FOCUSED VARIATIONS:
- "Some remarkable things are happening in artificial intelligence right now, I'm {voice_name}"
- "The AI world is buzzing with new developments, {voice_name} bringing you the highlights"
- "Breakthrough after breakthrough in AI, I'm {voice_name} with what matters most"

ENGAGING VARIATIONS:
- "You won't believe what's happening in AI today, {voice_name} here with the stories"
- "Artificial intelligence just got more interesting, I'm {voice_name} with the details"
- "The future of AI is unfolding right now, {voice_name} with the latest insights"

CONVERSATIONAL VARIATIONS:
- "Let me tell you what caught my attention in AI today, I'm {voice_name}"
- "There's so much happening in artificial intelligence, {voice_name} here to break it down"
- "AI researchers have been busy, I'm {voice_name} with what they've discovered"

ALWAYS create completely new intro content that feels fresh and spontaneous.

Present each story as breaking news you're personally delivering, not content you're reading.

{context_info}"""

        try:
            # Use Claude Opus for script generation (highest quality for creative content)
            llm = self._get_llm("claude-opus")
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Deliver these AI news developments naturally as {voice_name}. Create a completely unique, fresh intro that's never been used before - make it spontaneous and engaging. Present each story as breaking news you're personally sharing with your audience:\n\n{articles_text}")
            ]
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"Error generating podcast script: {e}")
            # Fallback to natural presentation if AI generation fails
            import random
            intros = [
                f"Some remarkable things are happening in artificial intelligence right now, I'm {voice_name}.",
                f"The AI world is buzzing with new developments, {voice_name} bringing you the highlights.",
                f"You won't believe what's happening in AI today, {voice_name} here with the stories.",
                f"Breakthrough after breakthrough in AI, I'm {voice_name} with what matters most.",
                f"Let me tell you what caught my attention in AI today, I'm {voice_name}.",
                f"Artificial intelligence just got more interesting, I'm {voice_name} with the details.",
                f"The future of AI is unfolding right now, {voice_name} with the latest insights.",
                f"There's so much happening in artificial intelligence, {voice_name} here to break it down.",
                f"AI researchers have been busy, I'm {voice_name} with what they've discovered.",
                f"Welcome to this moment in AI history, {voice_name} here with today's developments.",
                f"It's another exciting day in AI, I'm {voice_name} with the latest breakthroughs.",
                f"The pace of AI innovation is incredible, I'm {voice_name} with today's highlights."
            ]
            script = random.choice(intros) + " "
            
            transitions = ["Meanwhile, ", "In other news, ", "Also today, ", "Additionally, ", ""]
            for i, article in enumerate(summaries):
                title = article.get('title', 'AI News Update')
                summary = article.get('summary', 'No summary available.')
                if i > 0:
                    script += random.choice(transitions)
                script += f"{summary} "
            
            outros = [
                "That's your AI update for today.",
                "More developments as they happen.",
                "Stay tuned for more AI breakthroughs.",
                "We'll keep you updated on these stories.",
                "That's the latest from the world of artificial intelligence."
            ]
            script += random.choice(outros)
            return script
    
    def revise_podcast_script(self, script: str) -> str:
        """Refine the podcast script for optimal TTS performance.
        
        Args:
            script: The original podcast script.
            
        Returns:
            Script optimized for natural-sounding TTS output.
        """
        system_prompt = """You are a professional audio editor preparing natural news presentation for text-to-speech synthesis.
Optimize this news presentation to sound like a real presenter speaking naturally, NOT reading a script:

CRITICAL REQUIREMENTS:
1. Remove ANY references to "script", "article", "episode", or meta-commentary
2. Remove phrases like "according to reports", "this article says", "in this episode"
3. Make it sound like the presenter personally knows these developments
4. Ensure natural speech flow with varied sentence lengths
5. Convert numbers to words (e.g., "13.3 million" → "thirteen point three million")
6. Replace abbreviations with full words on first mention
7. Add em dashes — for natural pauses and breathing
8. Remove any script-like formatting or stage directions
9. Ensure smooth transitions between topics using natural presenter language
10. Keep the conversational, professional news presenter tone throughout

Make this sound like live news delivery, not script reading.

Return ONLY the revised script with NO additional commentary or explanations."""
        
        try:
            # Use GPT-4 for script refinement (excellent at following detailed instructions)
            # Fall back to Claude Sonnet if GPT-4 is not available
            llm = self._get_llm("gpt-4")
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Transform this into natural news presentation delivery, removing any script-like elements:\n\n{script}")
            ]
            response = llm.invoke(messages)
            # Additional cleaning to ensure no artifacts remain
            cleaned = response.content.strip()
            # Remove any remaining timestamps or special markers
            import re
            cleaned = re.sub(r'\[.*?\]|\(.*?\)|\*.*?\*', '', cleaned)
            # Remove any remaining introductory phrases
            cleaned = re.sub(r'^(Here\'s the (?:revised )?script:?[\s—:]*|Script:?[\s—:]*|Podcast Script:?[\s—:]*)', '', cleaned, flags=re.IGNORECASE)
            # Normalize whitespace
            cleaned = ' '.join(cleaned.split())
            # Clean up any remaining leading/trailing dashes or colons
            cleaned = re.sub(r'^[\s—:]+', '', cleaned)
            return cleaned
        except Exception as e:
            print(f"Error revising podcast script: {e}")
            return script  # Return the original script if revision fails


# Add this import at the top of the file
from datetime import datetime
