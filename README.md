# AI-parrot: Automating AI News Podcast Creation with LangGraph

AI-parrot is a demo project that leverages LangGraph's power to automate the generation of a podcast from the latest AI news. From fetching and ranking news articles to generating a professional podcast script and converting it to audio, AI-parrot handles it all using intelligent agents. This project highlights LangGraph's flexibility and capabilities in building sophisticated agent-based workflows.

## Key Features
- **Automated News Fetching:** Fetches the latest AI news from trusted sources and selects relevant articles.
- **Article Ranking:** It utilizes AI to rank news articles based on recency and relevance to artificial intelligence.
- **Script Generation:** Automatically generates a podcast script using AI agents in a friendly, conversational style.
- **AI-Powered Script Revision:** Refines the script to ensure it’s engaging, polished, and ready for a radio show.
- **Text-to-Speech Conversion:** Converts the podcast script to an MP3 format using TTS services, ready for sharing.
  
## Why This Project?
This project was created as part of the [AI4Devs](https://www.lidr.co/ia-devs) for [LIDR](https://www.lidr.co/) course to showcase LangGraph's potential and how it can be used to automate complex workflows, such as content generation and audio production. It’s designed to be a hands-on demo, offering a practical application of agent-based systems, and will continue to evolve as new features are added.

## What’s Next?
AI-parrot is far from finished! As the project grows, expect to see:

- **New sources for AI news:** Expanding beyond current sources to include a broader range of content.
- **Advanced ranking models:** Incorporating more sophisticated ranking algorithms to improve relevance scoring.
- **Dynamic script generation:** Adding the ability to tweak podcast scripts based on audience preferences.
- **More customization options:** Allowing users to modify the podcast tone and style with even more granularity.
- **Integration with Workflow Platforms:** Integrating with platforms like Zapier can allow us to schedule and automate the publishing.

Stay tuned, as AI-parrot will continue to evolve!

## How to Get Started
To clone the repository and set up your local environment, follow these steps:

1. ### Clone the repository:
```bash
git clone https://github.com/your-repo/AI-parrot.git
cd AI-parrot
```

2. ### Install the dependencies:
```bash
pip install -r requirements.txt
```
3. ### Set up environment variables by creating a .env file with your API keys:
```makefile
MISTRAL_API_KEY=<your-mistral-api-key>
NEWS_API_KEY=<your-news-api-key>
```
4. ### Run the project:
```bash
python main.py
````

## Contributing
This project is open for contributions! Please submit pull requests, raise issues, or suggest any features. Your feedback is invaluable in making AI-parrot even better.

