# News Scraper Bot for Thoughtful AI Process

This project is a web scraping bot designed to extract news articles based on a specified search phrase and category. The bot uses the RPA Framework and Selenium for web interactions and is designed to run on the Robocorp platform. This project is part of a selection process for Thoughtful AI.

## Table of Contents

- [News Scraper Bot for Thoughtful AI Process](#news-scraper-bot-for-thoughtful-ai-process)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [Robocorp Configuration](#robocorp-configuration)
    - [Work Items](#work-items)
  - [Running the Bot](#running-the-bot)
    - [Locally](#locally)
    - [Robocorp Cloud Execution](#robocorp-cloud-execution)
  - [Error Handling](#error-handling)
  - [Project Structure](#project-structure)
    - [bot_scraper.py](#bot_scraperpy)
    - [work_item_loader.py](#work_item_loaderpy)
    - [news_scraper.py](#news_scraperpy)
    - [excel_saver.py](#excel_saverpy)
    - [custom_selenium.py](#custom_seleniumpy)
  - [Conclusion](#conclusion)

## Prerequisites

Ensure you have the following installed on your system:

- Python 3.8 or higher
- Robocorp Lab or VS Code with Robocorp extension
- Git

## Installation

1. **Clone the Repository:**

   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies:**
   Use `conda` to create an environment and install the required packages from `conda.yaml`.
   ```sh
   conda env create -f conda.yaml
   conda activate <environment-name>
   ```

## Configuration

### Robocorp Configuration

1. **Robocorp Lab:**
   Open the project folder in Robocorp Lab.

2. **VS Code:**
   Open the project folder in VS Code with the Robocorp extension.

### Work Items

The bot uses work items to get input data. Ensure you configure the work items correctly in the Robocorp Cloud:

- `search_phrase`: The phrase to search for in news articles.
- `category`: The category of news articles.
- `months`: The number of months to look back for articles.

## Running the Bot

### Locally

1. **Run the bot:**
   ```sh
   rcc run
   ```

### Robocorp Cloud Execution

1. **Upload the robot to Robocorp Cloud:**
   Follow the instructions on the Robocorp documentation to upload the robot to the cloud.

2. **Create a new process:**
   In Robocorp Cloud, create a new process and add the uploaded robot to this process.

3. **Configure the work items:**
   Ensure the input work items are correctly configured.

4. **Run the process:**
   Trigger the process from the Robocorp Cloud interface.

## Error Handling

The bot includes error handling mechanisms to ensure robustness:

- **Logging:**
  Errors and important information are logged using Python's `logging` module.

- **Exception Handling:**
  Key functions include try-except blocks to handle and log exceptions appropriately.

- **Validation:**
  Input data is validated to ensure required fields are present and correctly formatted.

## Project Structure

```
.
├── bot_scraper.py
├── conda.yaml
├── custom_selenium.py
├── excel_saver.py
├── LICENSE
├── news_scraper.py
├── rcc
├── README.md
├── robot.yaml
├── tasks.py
└── work_item_loader.py
```

### bot_scraper.py

script that orchestrates the loading of work items, scraping news articles, and saving them to an Excel file.

### work_item_loader.py

Handles the loading and validation of work items from the Robocorp platform.

### news_scraper.py

Performs the web scraping operations, including searching for news articles, filtering by category, and extracting relevant information.

### excel_saver.py

Saves the scraped news articles to an Excel file.

### custom_selenium.py

A custom wrapper around Selenium to simplify browser interactions.

## Conclusion

This bot is designed to automate the process of scraping news articles based on specified criteria. By following the steps in this README, you can configure, run, and extend the bot to meet your specific requirements. If you encounter any issues or have questions, please refer to the documentation or reach out for support.
