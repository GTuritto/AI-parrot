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
import json
import csv
import asyncio
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Literal
import asyncio
from elevenlabs.client import ElevenLabs
from .translator import Translator

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
        self.voice_client = ElevenLabs()
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
    
    async def save_article_data(self, articles: List[Dict[str, Any]]) -> str:
        """Save article data to a CSV file.
        
        Args:
            articles: List of article dictionaries.
            
        Returns:
            Path to the saved CSV file.
        """
        if not articles:
            return ""
            
        # Generate filename with current date
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"podcast_articles_{date_str}.csv"
        filepath = self.get_output_path(filename)
        
        # Extract field names from the first article
        fieldnames = list(articles[0].keys())
        
        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for article in articles:
                writer.writerow(article)
                
        return filepath
    
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
    
    async def save_to_file(self, content: str, filename: str) -> str:
        """Save content to a file.
        
        Args:
            content: Content to save.
            filename: Name of the file.
            
        Returns:
            Path to the saved file.
        """
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
        voice_name: str = "Sarah",
        language: Literal['en', 'es'] = 'es',
        save_translation: bool = True,
        max_retries: int = 3,
        chunk_size: int = 2048
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
        output_filename = f"podcast_{date_str}_{voice_name}_{language}.mp3"
        output_path = os.path.join(self.output_dir, output_filename)
        
        retry_count = 0
        
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
    
    def save_articles_to_csv(self, articles: List[Dict[str, Any]]) -> str:
        """Save articles to a CSV file.
        
        Args:
            articles: List of article dictionaries.
            
        Returns:
            Path to the saved CSV file.
        """
        file_path = self.get_file_path("csv")
        
        headers = ["Title", "Summary", "Link"]
        
        with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for article in articles:
                writer.writerow({
                    "Title": article["title"],
                    "Summary": article.get("summary", "Summary not available"),
                    "Link": article["link"]
                })
        
        return file_path
        
    def _clean_podcast_script(self, script: str) -> str:
        """Clean and format the podcast script for natural reading.
        
        Args:
            script: The original podcast script.
            
        Returns:
            Cleaned narrative text ready for TTS.
        """
        import re
        
        # Remove any introductory phrases that might have been added by the AI
        script = re.sub(
            r'^(Here(?:''s| is) the (?:revised )?(?:podcast )?script:?|'
            r'Let me (?:create|write) (?:a|the) (?:podcast )?script (?:for you|now):?|'
            r'\*\*[^*]+\*\:?\s*|'
            r'^---\s*)',
            '', 
            script, 
            flags=re.IGNORECASE | re.MULTILINE
        )
        
        # Remove any remaining timestamps, section markers, or special formatting
        script = re.sub(r'\b(?:\d{1,2}:\d{2}(?::\d{2})?|\[.*?\]|\*\*[^*]+\*\*|##+\s*|\*\s*|_|~~|`)\s*', ' ', script)
        
        # Normalize all whitespace and handle em dashes
        script = ' '.join(script.split())
        script = re.sub(r'--+', '—', script)  # Convert multiple dashes to em dash
        
        # Split into sentences and clean each one
        sentences = []
        for sentence in re.split(r'([.!?]\s*)', script):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Capitalize the first letter of each sentence
            if sentence and sentence[0].isalpha() and sentence[0].islower():
                sentence = sentence[0].upper() + sentence[1:]
                
            sentences.append(sentence)
        
        # Join sentences back together
        cleaned_text = ''.join(sentences)
        
        # Add paragraph breaks after sentences that end a complete thought
        cleaned_text = re.sub(r'([.!?])(\s+[A-Z])', '\1\n\n\2', cleaned_text)
        
        # Clean up any remaining artifacts
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize spaces
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)  # Normalize newlines
        cleaned_text = re.sub(r'\s+([.,!?])', '\1', cleaned_text)  # Remove spaces before punctuation
        cleaned_text = re.sub(r'([.!?])\s+', '\1 ', cleaned_text)  # Single space after sentence endings
        cleaned_text = re.sub(r'\s*—\s*', ' — ', cleaned_text)  # Add spaces around em dashes
        
        # Ensure proper capitalization at the start of paragraphs
        paragraphs = []
        for para in cleaned_text.split('\n\n'):
            para = para.strip()
            if not para:
                continue
                
            # Capitalize first letter of each paragraph
            if para and para[0].isalpha() and para[0].islower():
                para = para[0].upper() + para[1:]
                
            # Ensure the paragraph ends with punctuation
            if para and para[-1] not in '.!?':
                para += '.'
                
            paragraphs.append(para)
        
        # Join with double newlines between paragraphs
        return '\n\n'.join(paragraphs)
