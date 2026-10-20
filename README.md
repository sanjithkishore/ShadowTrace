# 🔍 ShadowTrace

### Find the bug. Understand the cause. Discover the fix.

**ShadowTrace is a semantic bug-search application that helps developers discover relevant programming errors and their solutions using AI-powered vector search.**

Instead of relying only on exact keyword matches, ShadowTrace uses text embeddings and Qdrant to find programming errors with similar meanings, even when users describe them differently.

Users can describe a programming problem in natural language and retrieve related bug records containing explanations, root causes, suggested solutions, and example code.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Database Design](#-database-design)
- [Installation and Setup](#-installation-and-setup)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Example Usage](#-example-usage)
- [Performance Considerations](#-performance-considerations)
- [Limitations](#-limitations)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

Programming errors are a common part of software development. Developers frequently encounter errors whose descriptions differ from the wording used in existing documentation or solutions.

Traditional keyword-based searches may fail to retrieve relevant information when the user's description and the stored error record use different terminology.

ShadowTrace addresses this problem through **semantic search**.

It converts programming-error descriptions and user queries into numerical vector representations called embeddings. Qdrant compares these vectors and retrieves records that are semantically similar to the query.

The application then presents the matching records through a web interface.

### Project Goals

- Make programming-error searches more intuitive.
- Retrieve relevant bugs using natural-language descriptions.
- Help developers understand the causes of common errors.
- Provide suggested solutions and illustrative code examples.
- Demonstrate the practical use of vector databases in an application.

---

## ❓ Problem Statement

Developers often search for programming solutions using error messages, symptoms, or descriptions of unexpected behaviour.

However, two descriptions of the same underlying problem may use different words.

For example:

**Stored description:**

> The program crashes when accessing a property of an object that has not been initialized.

**User query:**

> Why does my Java application fail when I try to use an object that has no value?

A conventional exact-keyword search may not recognise the relationship between these descriptions.

ShadowTrace uses semantic similarity to identify potentially relevant records based on the meaning of the text rather than relying exclusively on exact word matches.

---

## ✨ Features

### 1. Semantic Bug Search

Search for programming errors using natural-language descriptions.

The application converts the query into an embedding and retrieves similar records from Qdrant.

### 2. Multi-Language Search

Search the sample bug collection across supported programming languages:

- Java
- Python
- C
- C++
- JavaScript

The available results depend on the records stored in the database.

### 3. Similarity Scores

Each search result includes a similarity score indicating how closely its vector matches the query vector.

These scores help compare the retrieved records but do not represent the probability that a solution is correct.

### 4. Root Cause Explanations

Each bug record contains an explanation of the underlying cause of the error.

This helps users understand why the problem may occur rather than simply recognising its name.

### 5. Suggested Solutions

The application presents possible fixes associated with the retrieved bug records.

Users should verify that a suggested fix applies to their specific code and environment.

### 6. Example Code

Where available, bug records include illustrative code demonstrating a solution or the relevant programming concept.

### 7. Interactive Web Interface

The React frontend provides:

- A programming-error search field.
- A programming-language selector.
- Search suggestions.
- Search result cards.
- Similarity scores.
- Root cause summaries.
- Detailed solution views.

### 8. REST API

FastAPI connects the frontend to the Python search engine and provides endpoints for health checks and semantic searches.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| React | Builds the user interface |
| Vite | Frontend development server and build tooling |
| JavaScript | Frontend application logic |
| HTML and CSS | Page structure and styling |
| Python | Backend application logic |
| FastAPI | Provides the REST API |
| Uvicorn | Runs the FastAPI application |
| Sentence Transformers | Converts text into vector embeddings |
| `all-MiniLM-L6-v2` | Pretrained sentence-embedding model |
| Qdrant | Stores vectors and performs similarity searches |
| Git | Version control |
| GitHub | Source-code hosting |

---

## 🏗️ System Architecture

ShadowTrace follows a frontend-backend architecture.

```text
                  ┌──────────────────────┐
                  │        USER          │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │    React Frontend    │
                  │                      │
                  │ Search Input         │
                  │ Language Selection   │
                  │ Results and Details  │
                  └──────────┬───────────┘
                             │
                       HTTP Request
                             │
                             ▼
                  ┌──────────────────────┐
                  │     FastAPI API      │
                  │                      │
                  │ Request Validation   │
                  │ Search Endpoint      │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Search Engine      │
                  │                      │
                  │ Sentence Transformer │
                  │ Query Embedding      │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Qdrant Database    │
                  │                      │
                  │ Vector Storage       │
                  │ Similarity Search    │
                  │ Payload Filtering    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Matching Bug Records │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │    React Results     │
                  └──────────────────────┘
```

### Architecture Components

**Frontend:** Collects the user's query and displays the retrieved bug records.

**API layer:** Validates requests and passes the query to the search engine.

**Embedding model:** Converts text into a numerical vector representation.

**Qdrant:** Stores the vectors and associated bug information and retrieves similar records.

**Payload:** Contains the descriptive information associated with each vector, including the title, language, cause, solution, and example code.

---

## ⚙️ How It Works

ShadowTrace uses the following workflow.

### Step 1: Prepare the Dataset

Programming-error records are maintained in `backend/bugs.json`.

Each record contains descriptive information about a programming error and its solution.

### Step 2: Generate Embeddings

The Sentence Transformers model converts the text associated with each bug into a numerical vector.

The model used by the initial implementation is:

`all-MiniLM-L6-v2`

### Step 3: Store Vectors in Qdrant

The application stores each vector in a Qdrant collection named:

`shadowtrace_bugs`

The associated bug information is stored as the point's payload.

### Step 4: Accept a Search Query

The user enters a programming problem through the React interface.

The frontend sends the query and selected programming language to FastAPI.

### Step 5: Generate the Query Embedding

The backend converts the user's description into a vector using the same embedding model.

Using the same model for stored descriptions and search queries keeps their vector representations compatible.

### Step 6: Retrieve Similar Records

Qdrant compares the query vector with stored vectors using cosine similarity.

If a language is selected, the search can also filter records using the payload's language field.

### Step 7: Display Results

The backend returns the matching records as JSON.

React displays the results, including their titles, languages, similarity scores, root causes, and suggested solutions.

---

## 📂 Project Structure

The project is organised into frontend and backend directories.

```text
ShadowTrace/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── bugs.json
│   ├── main.py
│   ├── search_engine.py
│   ├── requirements.txt
│   └── qdrant_storage/
│
├── .gitignore
└── README.md
```

**Note:** The `qdrant_storage/` directory is generated locally and should not be committed to GitHub. Qdrant can recreate its local collection from the dataset during initialisation.

The structure above describes the intended core files. Optional directories and generated files may vary as development progresses.

---

## 🗄️ Database Design

ShadowTrace uses Qdrant as its vector database.

Unlike a conventional relational database that primarily retrieves records using structured conditions and indexes, Qdrant is designed to retrieve vectors based on similarity.

### Collection

The initial implementation uses the collection:

`shadowtrace_bugs`

### Vector Configuration

| Property | Configuration |
|---|---|
| Collection name | `shadowtrace_bugs` |
| Vector representation | Dense vectors |
| Embedding model | `all-MiniLM-L6-v2` |
| Vector dimensions | 384 |
| Similarity metric | Cosine similarity |
| Record identifier | Bug ID |
| Metadata storage | Qdrant payload |

### Payload Structure

Each Qdrant point contains a vector and a payload with information such as:

| Field | Description |
|---|---|
| `id` | Unique bug identifier |
| `title` | Name of the error |
| `language` | Programming language |
| `category` | Error category |
| `description` | Description of the problem |
| `root_cause` | Explanation of the cause |
| `solution` | Suggested fix |
| `example` | Illustrative code |

### Example Record

```json
{
  "id": 1,
  "title": "NullPointerException",
  "language": "Java",
  "category": "Runtime Error",
  "description": "The program crashes when accessing a property of an object that has not been initialized.",
  "root_cause": "The object reference is null when the program tries to access one of its fields or methods.",
  "solution": "Initialize the object before accessing its properties or check whether the reference is null.",
  "example": "if (user != null) {\n    System.out.println(user.getName());\n}"
}
```

### Indexing and Filtering

The initial implementation creates payload indexes for:

- `language`
- `category`

These indexes support filtering records using structured metadata.

### Why Qdrant?

Qdrant is suitable for this application because it provides:

- Vector storage.
- Similarity-based retrieval.
- Metadata filtering.
- Payload storage alongside vectors.
- Local development without requiring a separate database server.

---

## 🚀 Installation and Setup

Follow these instructions to run ShadowTrace locally.

### Prerequisites

Install the following tools:

- Git
- Node.js and npm
- Python
- A code editor such as Visual Studio Code

An internet connection is required to download the pretrained embedding model if it is not already cached.

### 1. Clone the Repository

Replace the example URL with your actual GitHub repository URL.

```bash
git clone https://github.com/YOUR-USERNAME/ShadowTrace.git
cd ShadowTrace
```

### 2. Set Up the Python Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell, activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can invoke the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Otherwise, install the dependencies using:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Start the Backend

From the `backend` directory, run:

```bash
python -m uvicorn main:app --reload
```

The backend should become available at:

`http://127.0.0.1:8000`

FastAPI's interactive documentation is available at:

`http://127.0.0.1:8000/docs`

Keep the backend terminal running.

### 4. Set Up the Frontend

Open a second terminal.

Navigate to the frontend directory from the project root:

```bash
cd frontend
```

Install the frontend dependencies:

```bash
npm install
```

Start the React development server:

```bash
npm run dev
```

Vite will display the local development address, usually:

`http://localhost:5173`

Open the displayed address in your browser.

Keep both the frontend and backend servers running while using the application.

---

## ▶️ Running the Application

Once both servers are running:

1. Open the ShadowTrace website in your browser.
2. Enter a programming error or describe the problem.
3. Select a programming language or choose all languages.
4. Click **Find Solutions**.
5. Review the retrieved bug records.
6. Open a result to view its root cause, suggested solution, and example code.

### Example Search

**Query:**

```text
My Java program crashes when I try to access an object that has not been initialized.
```

**Language:**

```text
Java
```

A relevant result may include:

- Error: `NullPointerException`
- Cause: Accessing a null object reference.
- Solution: Initialise the object or check whether the reference is null.
- Example: A null-check before accessing the object's properties.

The actual results depend on the dataset and the vector similarity ranking.

---

## 🔌 API Endpoints

The initial backend exposes the following endpoints.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Returns a welcome message and API status |
| `GET` | `/health` | Checks backend health |
| `POST` | `/api/search` | Searches for semantically similar bug records |

### Health Check

**Request:**

```http
GET /health
```

**Example response:**

```json
{
  "status": "healthy"
}
```

### Semantic Search

**Request:**

```http
POST /api/search
Content-Type: application/json
```

**Example request body:**

```json
{
  "query": "My Python program accesses an element outside the list.",
  "language": "Python",
  "limit": 5
}
```

**Example response structure:**

```json
{
  "query": "My Python program accesses an element outside the list.",
  "language": "Python",
  "count": 1,
  "results": [
    {
      "id": 3,
      "title": "IndexError: List Index Out of Range",
      "language": "Python",
      "category": "Runtime Error",
      "description": "A Python program attempts to retrieve an element from a list using an invalid index.",
      "root_cause": "The list is shorter than expected or the program calculates an invalid index.",
      "solution": "Check the list length and validate the index before accessing the element.",
      "example": "if 0 <= index < len(items):\n    print(items[index])",
      "score": 0.85
    }
  ]
}
```

**Note:** The result above is illustrative. The actual result count, payload, and similarity score depend on the records stored in Qdrant and the user's query.

### Interactive API Documentation

Visit:

`http://127.0.0.1:8000/docs`

This page allows you to inspect the available endpoints and submit test requests.

---

## 📊 Performance Considerations

Search performance depends on several factors.

### 1. Embedding Generation

The embedding model must convert the query into a vector before searching.

The first execution may take longer because the model needs to load into memory.

### 2. Dataset Size

The number of stored vectors affects retrieval work and storage requirements.

Larger collections may require additional tuning depending on the workload.

### 3. Vector Indexing

Qdrant uses vector indexing techniques to support similarity search. Its indexing configuration and collection size can affect retrieval latency.

### 4. Payload Filtering

Filtering by programming language or category narrows the records eligible for retrieval.

Payload indexes can help support these filtered searches.

### 5. Query Quality

A clear, descriptive query may retrieve more relevant results than a vague or ambiguous query.

### 6. Evaluation

Similarity scores alone are insufficient to establish search quality.

A more complete evaluation should use representative test queries and assess whether the expected bug records appear among the top results.

No formal benchmark results are claimed for the current implementation.

---

## ⚖️ Limitations

ShadowTrace is an early-stage project and has several limitations.

- **Limited dataset:** Search quality depends on the number and quality of available bug records.
- **Retrieval rather than diagnosis:** The application retrieves existing records; it does not independently debug arbitrary source code.
- **Similarity is not correctness:** A high similarity score does not guarantee that the retrieved solution applies to the user's problem.
- **Embedding limitations:** Similarity depends on the pretrained embedding model's representation of the text.
- **No guaranteed solution:** A relevant record may not exist in the current dataset.
- **Local deployment:** The development configuration is designed for local use and requires additional configuration before public deployment.

---

## 🔮 Future Improvements

The following improvements are potential future development goals.

### Dataset Improvements

- Expand the bug dataset with more programming errors.
- Add more detailed explanations and examples.
- Validate records for consistency and accuracy.

### Search Improvements

- Evaluate different embedding models.
- Compare embedding strategies.
- Test search quality using a collection of representative queries.
- Tune result limits and similarity thresholds based on evaluation.
- Improve filtering and result ranking.

### Application Improvements

- Add a form for contributing new bug records.
- Implement controlled create, update, and delete operations.
- Add automated tests for the API and frontend.
- Improve accessibility and responsive design.
- Add a genuine backend health indicator.

### Deployment

- Deploy the frontend and backend.
- Configure persistent database storage.
- Use environment variables for deployment-specific configuration.
- Add authentication and protection for database modification operations.
- Configure HTTPS and appropriate security controls.

These items describe planned improvements and are not claims that the features are already implemented.

---

## 🤝 Contributing

Contributions and suggestions are welcome.

If you would like to improve ShadowTrace:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Test the changes locally.
5. Submit a pull request describing the improvement.

For dataset contributions, ensure that error descriptions and suggested solutions are accurate, understandable, and appropriately sourced.

---

## 📄 License

No license has been selected for this project yet.

A license can be added after choosing the terms under which others may use, modify, and distribute the code.

---

## 👨‍💻 Project Information

**Project:** ShadowTrace

**Category:** Database Systems / Semantic Search

**Primary Database:** Qdrant

**Backend:** Python and FastAPI

**Frontend:** React and Vite

**Embedding Model:** Sentence Transformers — `all-MiniLM-L6-v2`

ShadowTrace is a learning and portfolio project exploring the practical use of vector databases and semantic search in a developer-focused application.

---

*ShadowTrace — Find the bug. Understand the cause. Discover the fix.*