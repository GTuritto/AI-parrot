#!/usr/bin/env python3
"""Runner script for the podcast generator."""
import sys
import argparse
import asyncio
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import the main function
from podcast_generator.main import main

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate an AI podcast from recent articles.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--language',
        '-l',
        type=str,
        choices=['en', 'es'],
        default='en',
        help='Language for the podcast (en=English, es=Spanish)'
    )
    
    parser.add_argument(
        '--voice',
        '-v',
        type=str,
        default='Aria',
        help='Voice to use for the podcast. For Spanish, recommended: Aria, Sarah, or Lily.'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(language=args.language, voice=args.voice))
