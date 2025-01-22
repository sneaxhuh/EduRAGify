# Study Assistant: Your AI-Powered Study Companion

## Overview

Study Assistant is an all-in-one platform designed to enhance the learning experience. By combining advanced AI technologies, this tool generates summaries, creates quizzes, enables Q&A with study materials, and allows users to take notes and query them later. Whether you're revising for exams or organizing study materials, Study Assistant is your ultimate companion for smarter studying.

---

## Features

- **Summary Generation**: Automatically generate concise summaries from study material to help you quickly grasp key concepts.
- **Quiz Generation**: Create quizzes from your study material to test your knowledge and reinforce learning.
- **Q&A**: Ask questions based on your study material or notes, and get accurate answers powered by advanced NLP.
- **Note-Taking & Querying**: Take notes on-the-go and query them later for quick access to critical information.
  
---

## Tech Stack

- **Streamlit**: For building an interactive and user-friendly web interface.
- **Cortex**: For efficient data storage, search, and retrieval.
- **Mistral-Large**: A powerful NLP model for accurate text understanding, summarization, and Q&A generation.
- **Snowflake**: For data storage and analytics.

---

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/EduRAGify.git
    cd EduRAGify
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up Streamlit secrets**:

    For secure handling of your credentials, use Streamlit secrets. In your project directory, create a `.streamlit/secrets.toml` file and add your credentials as follows:

    ```toml
    # secrets.toml
    SNOWFLAKE_ACCOUNT = "your_snowflake_account"
    SNOWFLAKE_USER = "your_snowflake_user"
    SNOWFLAKE_PASSWORD = "your_snowflake_password"
    SNOWFLAKE_ROLE = "your_snowflake_role"
    SNOWFLAKE_WAREHOUSE = "your_snowflake_warehouse"
    SNOWFLAKE_DATABASE = "your_snowflake_database"
    SNOWFLAKE_SCHEMA = "your_snowflake_schema"
    CORTEX_SEARCH_SERVICE = "your_cortex_search_service"
    ```

    **Important**: Make sure your `.streamlit/secrets.toml` file is not committed to your version control system. Add `.streamlit/` to your `.gitignore` file to keep your credentials secure.

4. Run the app:

    ```bash
    streamlit run app.py
    ```

---

## Usage

1. **Upload Study Material**: Upload your study documents (PDFs, text files, etc.).
2. **Summarize**: Automatically generate summaries for your uploaded material.
3. **Create Quizzes**: Generate quizzes based on the content to test your knowledge.
4. **Ask Questions**: Use the Q&A feature to ask specific questions about your study material or notes.
5. **Take Notes**: Jot down important points and query them later when needed.

---

## Future Improvements

- **Multilingual Support**: Expand the platform to support multiple languages.
- **Personalized Learning**: Implement personalized study plans based on user preferences.
- **Mobile Version**: Develop a mobile-friendly version for on-the-go study.
- **Collaboration Features**: Allow users to share notes and collaborate with peers.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
