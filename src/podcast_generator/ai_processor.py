"""AI processing module for podcast generation."""
from typing import Dict, List, Any, Optional, Tuple, Literal

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

from utils.env import APIKeys

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
        """Summarize an article using Claude AI.
        
        Args:
            article: Article dictionary to summarize.
            max_retries: Maximum number of retries if summarization fails.
            
        Returns:
            Summarized article text.
        """
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
    
    def generate_podcast_script(self, summaries: List[Dict[str, Any]]) -> str:
        """Generate a podcast script from article summaries.
        
        Args:
            summaries: List of article dictionaries with summaries.
            
        Returns:
            Generated podcast script optimized for TTS.
        """
        if not summaries:
            return "Welcome to Artificial Intelligence Today. No AI news updates are available right now. Check back soon for more updates."
        
        # Format the articles for the prompt
        articles_text = ""
        for i, article in enumerate(summaries, 1):
            articles_text += f"\n\nArticle {i}: {article['title']}\n{article.get('summary', 'No summary available.')}"
        
        system_prompt = """You are a professional radio host creating a clean, engaging podcast script about the latest AI news.
The script will be read by a text-to-speech system, so please follow these guidelines carefully:

- Write in a natural, conversational tone
- Keep sentences short and clear (max 15-20 words)
- Avoid complex sentence structures
- Use simple, direct language
- Skip any meta-commentary about the script format
- Don't mention being a host or use phrases like "in this episode"
- Avoid quotation marks and special formatting
- Use em dashes for pauses — like this
- Keep numbers simple (e.g., "thirteen point three million" instead of "13.3 million")
- Start with the content immediately - no intros or titles
- Create a seamless narrative that flows naturally from one story to the next"""

        try:
            # Use Claude Opus for script generation (highest quality for creative content)
            llm = self._get_llm("claude-opus")
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Create a podcast script based on these articles:\n\n{articles_text}")
            ]
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"Error generating podcast script: {e}")
            # Fallback to simple formatting if AI generation fails
            script = "Welcome to Artificial Intelligence Today. "
            for article in summaries:
                script += f"{article['title']}. {article.get('summary', 'No summary available.')} "
            script += "That's all for today's AI update."
            return script
    
    def revise_podcast_script(self, script: str) -> str:
        """Refine the podcast script for optimal TTS performance.
        
        Args:
            script: The original podcast script.
            
        Returns:
            Script optimized for natural-sounding TTS output.
        """
        system_prompt = """You are a professional audio editor preparing a script for text-to-speech synthesis.
Please optimize the podcast script for the best possible TTS output following these rules:

1. Start with the content immediately - NO introductory phrases
2. Remove any script-like elements (e.g., "Host:", "Narrator:", "[sound effect]")
3. Convert numbers to words (e.g., "13.3 million" → "thirteen point three million")
4. Replace abbreviations with full words (e.g., "AI" → "artificial intelligence" on first mention)
5. Break long sentences into shorter ones (max 15-20 words)
6. Remove or rephrase complex technical terms for clarity
7. Add em dashes — for natural pauses
8. Remove any meta-commentary about the script format
9. Ensure smooth transitions between ideas
10. Remove any self-referential phrases (e.g., "in this episode")
11. Make sure the script sounds natural when spoken aloud

Return ONLY the revised script with NO additional commentary or explanations."""
        
        try:
            # Use GPT-4 for script refinement (excellent at following detailed instructions)
            # Fall back to Claude Sonnet if GPT-4 is not available
            llm = self._get_llm("gpt-4")
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Please optimize this podcast script for TTS:\n\n{script}")
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
