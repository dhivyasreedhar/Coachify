# Coachify AI Coaching Agent

Coachify is an AI-powered coaching agent designed to conduct personalized coaching sessions and generate comprehensive coaching reports. These reports include an overall assessment, detailed scores across various coaching criteria, identified strengths, areas for improvement, personalized coaching notes, and a transcript of the entire coaching session.

## Features

- **Overall Assessment:** Provides an overall visual representation of the coaching score.
- **Detailed Scores:** Offers granular scoring across multiple coaching criteria.
- **Strengths and Improvement Areas:** Clearly lists identified strengths and targeted areas for growth.
- **Coaching Notes:** Summarizes key insights and actionable coaching recommendations.
- **Interactive Transcript:** Includes the complete coaching session transcript with toggle visibility functionality.
- **Print Functionality:** Enables easy printing of coaching reports.

## Tech Stack

Coachify utilizes the following technologies:

- **Flask:** A lightweight Python web framework to develop and serve the web application.
- **OpenAI:** Integration with OpenAI's models for advanced natural language understanding and generation capabilities.
- **LlamaIndex:** For efficient retrieval and querying using:
  - `VectorStoreIndex`
  - `SimpleDirectoryReader`
  - `StorageContext`
  - `load_index_from_storage`
  - `RetrieverQueryEngine`
  - `VectorIndexRetriever`

## Usage

To set up and run the Coachify AI Coaching Agent, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the project directory:**
   ```bash
   cd coachify
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Conduct a coaching session and generate a report:**
   - Start a new session.
   - Interact with the AI agent.
   - Automatically generate a detailed coaching report upon completion.

Enjoy personalized AI-powered coaching with Coachify!
