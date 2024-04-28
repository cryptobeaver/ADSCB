# LLM-BSD Project

This project is a Python-based application that utilizes Streamlit for building interactive web applications and integrates with LanceDB for data storage and retrieval. It also leverages the Cohere API for natural language processing tasks.

## Prerequisites

Before running the project, make sure you have the following:

- Python 3.x installed
- Poetry installed (for dependency management)
- Cohere API key
- LanceDB database set up

## Project Structure

The project consists of the following main files:

- `run_scraper.py`: Scrapes data from a specified website and saves it as HTML files.
- `run_parser.py`: Parses the scraped HTML files and extracts relevant content.
- `run_embeddings.py`: Processes the parsed data, generates embeddings, and stores them in a LanceDB table.
- `run_api_endpoint.py`: Implements a FastAPI endpoint that accepts user queries, searches the LanceDB table, and generates responses using the Cohere API.
- `run_frontend.py`: Builds a Streamlit web application that allows users to interact with the FastAPI endpoint and view the generated responses.

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/aiwaldoh/llm-bsd.git
   ```

2. Install Poetry if you haven't already:
   ```
   pip install poetry
   ```

3. Install the project dependencies using Poetry:
   ```
   poetry install
   ```

4. Set up the Cohere API key:
   - Create a `.env` file in the project root directory.
   - Add the following line to the `.env` file:
     ```
     COHERE_API_KEY=your-api-key
     ```
   - Replace `your-api-key` with your actual Cohere API key.

5. Set up the LanceDB database:
   - Make sure you have LanceDB installed and running.
   - Update the database connection details in the relevant files (`run_embeddings.py` and `run_api_endpoint.py`) if necessary.

## Usage

1. Run the scraper to fetch data from the desired website:
   ```
   poetry run python run_scraper.py
   ```
   - Modify the `base_url`, `output_dir`, `filter_pattern`, and `sitemap_filename` variables in `run_scraper.py` according to your requirements.

2. Parse the scraped HTML files:
   ```
   poetry run python run_parser.py
   ```
   - The parsed data will be saved as `.parsed` files in the same directory as the scraped HTML files.

3. Process the parsed data and store it in the LanceDB table:
   ```
   poetry run python run_embeddings.py
   ```
   - Update the `base_url_for_docs`, `table_name`, and `folder_path` variables in `run_embeddings.py` to match your setup.

4. Start the FastAPI endpoint:
   ```
   poetry run uvicorn run_api_endpoint:app --reload
   ```
   - The API endpoint will be accessible at `http://localhost:8000/ask`.

5. Run the Streamlit frontend:
   ```
   poetry run streamlit run run_frontend.py
   ```
   - The Streamlit web application will be accessible at `http://localhost:8501`.

6. Interact with the web application by entering your queries and viewing the generated responses.

## Static Changes

- In the `run_embeddings.py` file, make sure to update the following variables according to your specific setup:
  - `base_url_for_docs`: Set it to the base URL of the documentation website you scraped.
  - `table_name`: Specify the name of the LanceDB table where you want to store the processed data.
  - `folder_path`: Set it to the directory path where the parsed data files (`.parsed`) are located.

- In the `run_api_endpoint.py` file, ensure that the `table_name` variable matches the name of the LanceDB table you specified in `run_embeddings.py`.

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).