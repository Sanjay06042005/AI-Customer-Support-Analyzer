\# 🤖 AI Customer Support Analyzer



An AI-powered customer support ticket analysis application built using \*\*Python, Pandas, Groq LLM, and Streamlit\*\*.



The system allows users to ask natural-language questions about customer support tickets and receive data-driven answers based on the actual dataset.



\## 🚀 Features



\* Natural-language customer support ticket queries

\* Category, priority, status, unresolved, and agent filtering

\* Date-range analysis

\* Month-based analysis

\* Ticket lookup and ticket listing

\* Average response time analysis

\* Average resolution time analysis

\* Fastest and highest response-time analysis

\* Fastest and highest resolution-time analysis

\* Customer rating analysis

\* Rating analysis by category, priority, and agent

\* Common issue analysis

\* Daily ticket analysis

\* Monthly ticket analysis

\* Date-range ticket summaries

\* Streamlit dashboard with charts and KPIs

\* CSV dataset download

\* Groq API fallback when AI generation is unavailable



\## 🏗️ Architecture



```text

User Question

&#x20;     ↓

Local Python Query Understanding

&#x20;     ↓

Filter Extraction

&#x20;     ↓

Pandas Data Filtering \& Analysis

&#x20;     ↓

Groq LLM

&#x20;     ↓

Natural-Language Answer

&#x20;     ↓

Streamlit UI

```



\### Why this architecture?



Python and Pandas perform the actual calculations and filtering on the dataset.



The Groq LLM is used mainly to understand and format the final response.



This prevents the LLM from being responsible for numerical calculations and avoids sending the entire dataset to the model.



\## 📊 Dataset



The project uses a customer support ticket dataset containing \*\*500 tickets\*\*.



Columns include:



\* `ticket\_id`

\* `created\_at`

\* `category`

\* `priority`

\* `status`

\* `response\_time\_hrs`

\* `resolution\_time\_hrs`

\* `agent\_id`

\* `customer\_rating`

\* `issue\_summary`



\## 🛠️ Technologies



\* \*\*Python\*\*

\* \*\*Pandas\*\*

\* \*\*Groq API\*\*

\* \*\*Streamlit\*\*

\* \*\*python-dotenv\*\*



\## 📁 Project Structure



```text

AI\_Customer\_Support\_Analyzer/

│

├── .env

├── .gitignore

├── README.md

├── requirements.txt

│

├── data/

│   └── support\_tickets.csv

│

└── app/

&#x20;   ├── app.py

&#x20;   ├── ai\_analyzer.py

&#x20;   ├── data\_loader.py

&#x20;   │

&#x20;   └── tests/

&#x20;       ├── test\_data\_loader.py

&#x20;       ├── test\_analysis.py

&#x20;       └── test\_end\_to\_end.py

```



\## ⚙️ Installation



Clone the project and navigate to the project directory.



Install the required packages:



```bash

pip install -r requirements.txt

```



Create a `.env` file in the project root:



```text

GROQ\_API\_KEY=your\_groq\_api\_key

```



Do not commit the `.env` file to GitHub.



\## ▶️ Run the Application



Navigate to the application directory:



```bash

cd app

```



Run Streamlit:



```bash

streamlit run app.py

```



The application will open in your browser.



\## 💬 Example Questions



```text

How many unresolved tickets are there?

```



```text

Which category has the most tickets?

```



```text

What is the average response time for technical tickets?

```



```text

How many unresolved technical tickets were created in February 2024?

```



```text

Show me all unresolved technical tickets created in February 2024.

```



```text

What are the most common issues in technical tickets in February 2024?

```



```text

Which technical tickets had the highest response times in February 2024?

```



```text

Which month had the most unresolved tickets?

```



\## 🧠 Key Design Principle



The project follows a simple rule:



> \*\*Python calculates. The LLM communicates.\*\*



For example:



```text

User:

How many unresolved technical tickets were created in February 2024?



Python:

Category = Technical

Status = Unresolved

Month = February 2024



Pandas:

12 matching tickets



Groq:

Converts the result into a clear natural-language answer.

```



This approach improves reliability because the numerical result comes from the dataset rather than from the language model.



\## 📈 Dashboard



The Streamlit dashboard provides:



\* Total ticket count

\* Open ticket count

\* Unresolved ticket count

\* Average response time

\* Tickets by category

\* Tickets by priority

\* Tickets by status

\* Customer rating distribution

\* Agent performance

\* Recent support tickets

\* Dataset summary



\## 🔐 Security



API credentials are stored in environment variables.



The project uses:



```text

.env

```



for the Groq API key, while `.gitignore` prevents the file from being committed.



\## 🎯 Project Objective



The objective of this project is to build a practical AI-powered analytics application that combines:



\* Natural-language query understanding

\* Structured data processing

\* LLM integration

\* Data filtering

\* Statistical analysis

\* Interactive visualization



The project demonstrates how traditional Python data analysis and large language models can work together in an AI application.



\## 👨‍💻 Author



\*\*Sanjay Chandiran\*\*



B.Tech – Artificial Intelligence \& Data Science



Skills demonstrated in this project:



\*\*Python | Pandas | SQL | AI/ML | LLMs | Data Analysis | Streamlit | API Integration\*\*



