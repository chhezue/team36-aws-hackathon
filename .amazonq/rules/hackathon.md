# AI Response Generation Mandate: Project 'LocalBriefing'

**Primary Directive:** All future responses, without exception, must be generated based *exclusively* on the information and specifications contained within this document. Do not introduce external information, alternative technologies, or deviate from the defined project scope. This document is the single source of truth.

---

### 1. Project Overview

* **Project Name:** "AI Neighborhood News Summary Assistant" (Code Name: `LocalBriefing`).
* **Core Mission:** To provide users with a personalized daily news briefing based on their selected `Gu` (district) and `Dong` (neighborhood) in Seoul, South Korea.
* **Primary Technology Stack:** Python and Django.

---

### 2. System Architecture

The system is composed of three core components: a **Collector**, a **Processor**, and an **API Server**.

1.  **Client (User):** A user accesses the service via a web or mobile application, sets their location (e.g., Gangnam-gu, Yeoksam-dong), and requests their daily briefing.
2.  **API Server (Django):**
    * **User Management:** Manages user profiles and location settings.
    * **Data Serving:** Provides the processed briefing data to the client via an API.
    * **Database (PostgreSQL):** Stores user information, collected raw data, and the final AI-summarized briefings.
3.  **Background Worker (Celery & Redis):**
    * **Scheduler:** Automatically triggers the data collection and processing jobs at a set time every day (e.g., 4 AM).
    * **Collector (Web Scraper):** Uses Python libraries such as `requests`, `BeautifulSoup`, and `Selenium` to scrape information from predefined data sources.
    * **Processor (AI Summarizer):** Sends the collected raw text to an AI model (specified as **Amazon Bedrock**) to be summarized and categorized. The results are then stored in the database.

**Operational Flow:**
(Daily at 4 AM) **Scheduler** runs → **Collector** scrapes data from district offices, online communities, etc. → **Processor** sends text to the **AI Model** for summarization → Summarized content is saved to the **Database** → (When user accesses) The **Django Server** retrieves the latest briefing from the DB and delivers it via **API**.

---

### 3. Recommended AWS Services & Production Architecture

For production, the project will leverage the following AWS services. Two architectural patterns are proposed.

#### Recommended Services:
* **AI Core (Summarization):** **Amazon Bedrock** is the designated service for the production summarization engine. It provides access to high-performance foundation models like Anthropic's Claude, which is well-suited for Korean text summarization.
* **Application Server (Running Django):** **AWS Elastic Beanstalk** will be used to automatically provision and manage the infrastructure (EC2, load balancing, etc.) for the Django application.
* **Database:** **Amazon RDS for PostgreSQL** is the managed relational database service.
* **Automated Data Processing:** **AWS Lambda** and **Amazon EventBridge** will be used for scheduled, serverless execution of the data collection (scraping) and processing (summarization) tasks.

#### Architecture Option A: Standard Architecture
A traditional model where the Django application, running on Elastic Beanstalk, handles all logic.
* **Web Server & Batch Jobs:** Django on **Elastic Beanstalk**.
* **Database:** **Amazon RDS**.
* **AI Summarization:** Handled via an API call to **Amazon Bedrock** from within the Django application.
* **Flow:** `User ↔ Elastic Beanstalk (Django + Scheduler) ↔ RDS & Bedrock`

#### Architecture Option B: Modern Serverless-based Architecture (Preferred for Efficiency)
This model decouples the background processing from the API server for better scalability and cost-efficiency.
* **Web Server (API):** Django on **Elastic Beanstalk**.
* **Database:** **Amazon RDS**.
* **Batch Jobs (Collection/Summarization):** **Amazon EventBridge** triggers an **AWS Lambda** function on a schedule. The Lambda function performs the scraping and calls **Amazon Bedrock**, then writes the result to **RDS**.
* **Flows:**
    * API: `User ↔ Elastic Beanstalk (API) ↔ RDS`
    * Data Processing: `EventBridge (Scheduler) → Lambda (Scraping/AI) → RDS & Bedrock`

---

### 4. Development Process: Vibe Coding with Amazon Q Developer

The development process will be accelerated using a "vibe coding" approach with **Amazon Q Developer**. The following are examples of prompts to be used:

* **Phase 1: Project Scaffolding**
    > **Prompt:** "I'm starting a new project called 'LocalBriefing' using Python and Django. Create a basic project structure. I'll need a 'users' app to manage user information and a 'briefings' app to handle the daily briefing content."

* **Phase 2: Model Design**
    > **Prompt:** "In the 'briefings' app, define the Django models. I need a `Briefing` model that has a foreign key to the user, a `date` field, and a `JSONField` to store the categorized summary. Also, create a `RawData` model to store the original scraped text before processing, with fields for the source URL, category, and content."

* **Phase 3: Collector Development**
    > **Prompt:** "Write a Python function using `requests` and `BeautifulSoup` to scrape the 'news' section of the Gangnam-gu District Office website. The function should take a URL as input and return a list of dictionaries, with each dictionary containing the title and content of a post from the first page."

* **Phase 4: Processor Development (AI Summarizer)**
    > **Prompt:** "Now, create a Python function that uses the AWS SDK for Python (Boto3) to interact with Amazon Bedrock. This function will take a large block of text as input. Your task is to send this text to Bedrock with a specific instruction: **'Summarize the following text into 3 key sentences in the style of a neighborhood news report for a resident of South Korea. Use a friendly tone for each sentence.'** The function should return the summarized text."

* **Phase 5: API Endpoint Creation**
    > **Prompt:** "Using Django Rest Framework, create an API endpoint. When a logged-in user makes a GET request to `/api/briefing/today/`, it should retrieve the most recent briefing for that user's saved location from the database and return it as a JSON response."

---

### 5. Data Sources & Briefing Categories

The daily briefing will consist of the following categories, collected from the specified sources.

| Category (Item) | Details | Data Source | Collection Method |
| :--- | :--- | :--- | :--- |
| **☀️ Today's Local Weather** | Max/Min temperature, precipitation probability, fine dust levels. | KMA Public Data Portal, AirKorea | **API Call** |
| **📢 District/Community News** | Policy announcements, facility construction notices, local festivals, subsidy info. | 강남구청 공지사항 및 행사정보 CSV | **CSV Import** |
| **💬 Community Hot Issues** | Summary of popular posts and discussions from local online communities. | Naver Cafes (e.g., Gangnam Mom) | **Web Scraping** |
| **🥕 Popular Second-hand Items** | "Free sharing" items or popular listings from second-hand markets. | Karrot (Daangn) web version | **Web Scraping** |
| **🍽️ New Local Restaurants** | Information about general restaurants, bakeries, and cafes in Gangnam-gu. | 강남구 음식점 인허가정보 CSV (일반음식점, 제과점, 휴게음식점) | **CSV Import** |
| **📰 Other Local News**| News related to the district from Instagram, Naver News, YouTube etc. | Social Media, News Portals | **Web Scraping** |

**Important Considerations for Data Collection:**
* **Copyright & Terms of Service (ToS):** Strictly adhere to the ToS of each website. Implement delays (`time.sleep()`) to avoid overloading servers.
* **Data Cleansing:** A crucial preprocessing step involves removing ads and other irrelevant HTML elements to extract pure text content. This process can also be aided by generating code with Amazon Q.