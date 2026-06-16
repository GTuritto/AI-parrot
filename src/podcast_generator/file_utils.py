"""File operations for the AI Podcast Generator.

This module provides the FileManager class which handles all file-related operations
for the podcast generator, including saving articles, generating audio files, and
managing the output directory structure.

Key Features:
- Save article data to CSV files
- Generate and save podcast narratives
- Convert text to speech using ElevenLabs API
- Handle translations between English and Spanish
- Manage output directory structure

Example:
    >>> file_manager = FileManager(output_dir="MyPodcasts")
    >>> await file_manager.save_mp3_file("Hello, world!", voice_name="Sarah")
"""
import os
import asyncio
import random
import re
from datetime import datetime
from typing import Literal
from elevenlabs.client import ElevenLabs
from .translator import Translator
from utils.env import APIKeys

class FileManager:
    """Manages all file operations for the podcast generator.
    
    This class handles the creation, management, and organization of all files
    generated during the podcast creation process, including text content,
    audio files, and metadata.
    
    Attributes:
        output_dir (str): Directory where all output files will be saved.
        voice_client (ElevenLabs): Client for the ElevenLabs text-to-speech API.
        translator (Translator): Handles translation between English and Spanish.
    """
    
    def __init__(self, output_dir: str = "PodcastOutput"):
        """Initialize the file manager with the output directory.
        
        Creates the output directory if it doesn't exist and initializes
        the ElevenLabs client and Translator.
        
        Args:
            output_dir: Directory where output files will be saved. Defaults to "PodcastOutput".
        """
        self.output_dir = output_dir
        
        # Initialize API keys
        api_keys = APIKeys()
        
        # Initialize ElevenLabs client with API key
        if api_keys.elevenlabs:
            self.voice_client = ElevenLabs(api_key=api_keys.elevenlabs)
        else:
            print("Warning: ELEVENLABS_API_KEY not found. Audio generation will fail.")
            self.voice_client = None
            
        self.translator = Translator()
        os.makedirs(output_dir, exist_ok=True)
    
    def get_output_path(self, filename: str) -> str:
        """Get the full path for an output file.
        
        Args:
            filename: Name of the file.
            
        Returns:
            Full path to the output file.
        """
        return os.path.join(self.output_dir, filename)
    
    async def save_narrative_file(
        self, 
        content: str, 
        prefix: str = "AIpodcast",
        language: Literal['en', 'es'] = 'en'
    ) -> str:
        """Save the narrative script to a text file.
        
        Args:
            content: The narrative content to save.
            prefix: Prefix for the filename.
            language: Language code ('en' for English, 'es' for Spanish).
            
        Returns:
            Path to the saved file.
        """
        date_str = datetime.now().strftime("%Y%m%d")
        lang_suffix = '_es' if language == 'es' else ''
        filename = f"{prefix}_{date_str}_narrative{lang_suffix}.txt"
        filepath = self.get_output_path(filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return filepath
    
    def _get_voice_id(self, voice_name: str) -> str:
        """Get the voice ID for a given voice name.
        
        Args:
            voice_name: Name of the voice to look up.
            
        Returns:
            Voice ID string.
        """
        if not self.voice_client:
            print("ElevenLabs client not available. Using default voice ID.")
            return "21m00Tcm4TlvDq8ikWAM"  # Default voice ID (Rachel)
            
        try:
            # Get all available voices
            response = self.voice_client.voices.get_all()
            
            # Find the voice by name (case-insensitive)
            voice = next((v for v in response.voices if voice_name.lower() in v.name.lower()), None)
            
            if not voice:
                print(f"Voice '{voice_name}' not found. Using the first available voice.")
                return response.voices[0].voice_id
                
            return voice.voice_id
            
        except Exception as e:
            print(f"Error getting voice ID: {e}")
            # Return a default voice ID if there's an error
            return "21m00Tcm4TlvDq8ikWAM"  # Default voice ID (Rachel)
    
    async def save_mp3_file(
        self, 
        text_content: str, 
        voice_name: str = 'Sarah', 
        language: str = 'es',
        save_translation: bool = True,
        max_retries: int = 3,
        chunk_size: int = 2048,
        add_intro_outro: bool = True
    ) -> str:
        """Convert text to speech using ElevenLabs and save as MP3.
        
        This method handles the entire process of text-to-speech conversion,
        including optional translation to Spanish and saving the resulting
        audio file. It includes retry logic for handling API rate limits
        and network issues.
        
        Args:
            text_content: The text content to convert to speech.
            voice_name: The voice name to use for speech synthesis.
                     Recommended voices:
                     - English: 'Aria', 'Domi', 'Rachel'
                     - Spanish: 'Sarah', 'Lily', 'Elin'
                     Defaults to 'Sarah' which works well for Spanish.
            language: Language code ('en' for English, 'es' for Spanish).
                     Defaults to 'es' (Spanish).
            save_translation: Whether to save the translated text to a file.
                           Useful for debugging and review.
            max_retries: Maximum number of retry attempts for API calls.
                       Defaults to 3.
            chunk_size: Size of text chunks to process at once.
                      Helps with handling large texts and avoiding timeouts.
                      Defaults to 2048 characters.
            add_intro_outro: Whether to add intro and outro to the podcast.
                           Defaults to True.
            
        Returns:
            str: Path to the saved MP3 file.
            
        Raises:
            Exception: If there's an error generating or saving the MP3 after
                     all retry attempts.
                     
        Example:
            >>> file_manager = FileManager()
            >>> mp3_path = await file_manager.save_mp3_file(
            ...     "Hello, world!",
            ...     voice_name="Sarah",
            ...     language="es"
            ... )
            >>> print(f"Audio saved to: {mp3_path}")
        """
        original_text = text_content
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Add intro and outro if requested
        if add_intro_outro:
            text_content = self._add_intro_outro(text_content, language)
        
        # Translate to Spanish if needed
        if language == 'es':
            print("Translating content to Spanish...")
            try:
                # Make sure to await the async translation
                text_content = await self.translator.translate_to_spanish(text_content)
                print("Translation complete.")
                
                # Save the translated text for reference if requested
                if save_translation:
                    trans_file = os.path.join(
                        self.output_dir, 
                        f"translated_script_{date_str}.txt"
                    )
                    with open(trans_file, 'w', encoding='utf-8') as f:
                        f.write(text_content)
                    print(f"Saved translated script to: {trans_file}")
                    
                    # Also save the original for comparison
                    orig_file = os.path.join(
                        self.output_dir, 
                        f"original_script_{date_str}.txt"
                    )
                    with open(orig_file, 'w', encoding='utf-8') as f:
                        f.write(original_text)
            except Exception as e:
                print(f"Warning: Translation failed: {str(e)}")
                print("Falling back to original text.")
                text_content = original_text
        
        # Generate output filename with language and voice
        safe_voice_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", voice_name).strip("._") or "voice"
        output_filename = f"podcast_{date_str}_{safe_voice_name}_{language}.mp3"
        output_path = os.path.join(self.output_dir, output_filename)
        
        retry_count = 0
        
        # Check if ElevenLabs client is available
        if not self.voice_client:
            error_msg = "ElevenLabs client not initialized. Please check your ELEVENLABS_API_KEY."
            print(error_msg)
            raise Exception(error_msg)
        
        while retry_count < max_retries:
            try:
                print(f"Generating speech with voice: {voice_name} (Attempt {retry_count + 1}/{max_retries})...")
                
                # Get the voice ID
                voice_id = self._get_voice_id(voice_name)
                
                # Generate the audio using the client
                audio = self.voice_client.text_to_speech.convert(
                    text=text_content,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2" if language == 'es' else "eleven_monolingual_v1"
                )
                
                # Save the audio file
                with open(output_path, 'wb') as f:
                    for chunk in audio:
                        if chunk:
                            f.write(chunk)
                
                print(f"Successfully saved podcast to: {output_path}")
                return output_path
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    error_msg = f"Error generating or saving MP3 after {max_retries} attempts: {str(e)}"
                    print(error_msg)
                    raise Exception(error_msg) from e
                
                # Exponential backoff with jitter
                wait_time = min(2 ** retry_count + random.uniform(0, 1), 30)  # Cap at 30 seconds
                print(f"Attempt {retry_count} failed: {str(e)}. Retrying in {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
        
        # If we get here, all retries have failed
        error_msg = f"Failed to generate audio after {max_retries} attempts"
        print(error_msg)
        raise Exception(error_msg)
    
    def _add_intro_outro(self, content: str, language: str) -> str:
        """Add intro and outro to the podcast content.
        
        Args:
            content: The main podcast content.
            language: Language code ('en' or 'es').
            
        Returns:
            Content with intro and outro added.
        """
        if language == 'es':
            intro = ("¡Bienvenidos al Podcast de Inteligencia Artificial! "
                    "Soy tu anfitrión de IA, y hoy te traigo las últimas noticias "
                    "y desarrollos más importantes en el mundo de la inteligencia artificial. "
                    "Vamos a comenzar.")
            outro = ("Eso es todo por el episodio de hoy. "
                    "Gracias por escuchar el Podcast de Inteligencia Artificial. "
                    "Mantente al día con las últimas innovaciones en IA, "
                    "y nos vemos en el próximo episodio. ¡Hasta pronto!")
        else:
            intro = ("Welcome to the AI Podcast! "
                    "I'm your AI host, bringing you the latest news "
                    "and most important developments in the world of artificial intelligence. "
                    "Let's dive in.")
            outro = ("That's all for today's episode. "
                    "Thank you for listening to the AI Podcast. "
                    "Stay tuned for the latest AI innovations, "
                    "and we'll see you in the next episode. Until next time!")
        
        return f"{intro} {content} {outro}"
        
