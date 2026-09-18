# 🛒 ShopGraph — Knowledge Graph Based Product Recommendation System

ShopGraph is a **Knowledge Graph based Product Recommendation System** that recommends relevant products by understanding relationships between products, categories, features, brands, and use cases.

Unlike a basic recommendation system that relies only on product similarity, ShopGraph uses a **Knowledge Graph + relationship-aware candidate generation + weighted recommendation scoring** to produce recommendations that are both relevant and explainable.

🚀 **[Live Demo](https://shopgraph-frontend.onrender.com)**

---

## 🚀 Project Overview

When a user selects a product, ShopGraph:

1. Finds the selected product in the Knowledge Graph.
2. Traverses related products through graph relationships.
3. Generates recommendation candidates.
4. Compares product features, categories, use cases, and relationships.
5. Calculates a recommendation score.
6. Ranks the candidates.
7. Provides understandable reasons for each recommendation.

### Example

Suppose the user selects:

> **Dell Inspiron 15**

The Knowledge Graph may contain relationships such as:

```text
Dell Inspiron 15
│
├── BELONGS_TO ──> Laptop
├── MADE_BY ─────> Dell
├── HAS_FEATURE ─> USB-C
├── HAS_FEATURE ─> Bluetooth
├── USED_FOR ────> Programming
│
├── COMPATIBLE_WITH ──> Dell USB-C Hub
├── ACCESSORY ────────> Dell Laptop Stand
└── WORKS_WITH ───────> Dell 24 inch Monitor
```

Based on these relationships, ShopGraph can recommend products such as:

* Dell USB-C Hub
* Dell Laptop Stand
* Dell 24 inch Monitor
* Logitech MX Master 3S
* Samsung T7 SSD 1TB

The system also explains **why** a product was recommended.

---

# 🎯 Objectives

The main objectives of ShopGraph are:

* Build a structured Product Knowledge Graph.
* Represent relationships between products and product attributes.
* Generate recommendation candidates using graph traversal.
* Calculate transparent recommendation scores.
* Rank products based on multiple factors.
* Provide explanations for recommendations.
* Expose the recommendation engine through REST APIs.
* Provide a modern web interface for users.
* Deploy the complete system using cloud services.

---

# 🧠 Why a Knowledge Graph?

Traditional recommendation systems often depend mainly on:

* Product similarity
* User ratings
* Purchase history
* Collaborative filtering

ShopGraph focuses on **explicit relationships between entities**.

For example:

```text
Laptop
   │
   ├── has feature → USB-C
   │
   ├── used for → Programming
   │
   └── compatible with → USB-C Hub
```

This makes it possible to understand not only that two products are similar, but also **how they are related**.

---

# 🏗️ System Architecture

```text
                    ┌───────────────────────────┐
                    │       React Frontend      │
                    │     Vite + Tailwind CSS   │
                    └─────────────┬─────────────┘
                                  │
                                  │ REST API
                                  ▼
                    ┌───────────────────────────┐
                    │       FastAPI Backend     │
                    │          Python            │
                    ├───────────────────────────┤
                    │ Candidate Generation      │
                    │ Recommendation Scoring    │
                    │ Explanation Generation    │
                    └─────────────┬─────────────┘
                                  │
                                  │ Neo4j Driver
                                  ▼
                    ┌───────────────────────────┐
                    │        Neo4j Graph        │
                    │         Database           │
                    ├───────────────────────────┤
                    │ Products                   │
                    │ Categories                 │
                    │ Features                   │
                    │ Brands                     │
                    │ Use Cases                  │
                    │ Relationships              │
                    └───────────────────────────┘
```

---

# 🛠️ Technology Stack

## Backend

* Python
* FastAPI
* Neo4j
* Neo4j Python Driver
* Cypher
* Pandas
* Uvicorn
* Python-dotenv

## Frontend

* React.js
* Vite
* JavaScript
* Tailwind CSS
* Axios
* Lucide React

## Database

* Neo4j

## Development Tools

* Git
* GitHub
* VS Code
* Postman
* Neo4j Browser

## Deployment

* Vercel — Frontend
* Render — Backend
* Neo4j Aura — Knowledge Graph Database

---

# 📊 Knowledge Graph Model

ShopGraph uses the following main node types.

## Nodes

```text
Product
Category
Feature
Brand
UseCase
```

## Relationships

```text
Product ──BELONGS_TO──────> Category

Product ──MADE_BY─────────> Brand

Product ──HAS_FEATURE─────> Feature

Product ──USED_FOR────────> UseCase

Product ──COMPATIBLE_WITH─> Product

Product ──ACCESSORY───────> Product

Product ──WORKS_WITH──────> Product

Product ──SIMILAR_TO──────> Product
```

---

# 🗃️ Example Knowledge Graph

For example:

```text
                 ┌──────────────┐
                 │    Laptop    │
                 └──────┬───────┘
                        │
                   BELONGS_TO
                        │
                        ▼
              ┌──────────────────┐
              │ Dell Inspiron 15 │
              └──────────────────┘
                 │      │      │
          HAS_FEATURE     │    USED_FOR
                 │       │      │
                 ▼       │      ▼
              USB-C      │  Programming
                         │
                  COMPATIBLE_WITH
                         │
                         ▼
                ┌─────────────────┐
                │ Dell USB-C Hub  │
                └─────────────────┘
```

This graph structure allows the recommendation engine to use multiple paths to identify relevant products.

---

# 📦 Sample Products

The current dataset contains products such as:

### Laptops

* Dell Inspiron 15
* HP Pavilion 15
* Lenovo IdeaPad Slim 5

### Mice

* Logitech MX Master 3S
* Logitech M331

### Keyboards

* Keychron K2
* Logitech K380

### Accessories

* Dell USB-C Hub
* Anker USB-C Hub
* Dell Laptop Stand
* Portronics Laptop Stand
* Dell Laptop Bag
* HP Laptop Backpack

### Monitors

* LG 24 inch Monitor
* Dell 24 inch Monitor

### Headphones

* Sony WH-1000XM5
* JBL Tune 770NC

### Storage

* Samsung T7 SSD 1TB
* WD My Passport 1TB

### Webcam

* Logitech C920 Webcam

---

# 🔍 Recommendation Pipeline

The recommendation process follows these stages:

```text
User Selects Product
        │
        ▼
Find Product in Neo4j
        │
        ▼
Generate Candidate Products
        │
        ▼
Calculate Relationship Match
        │
        ▼
Calculate Feature Compatibility
        │
        ▼
Calculate Category Match
        │
        ▼
Calculate Use Case Match
        │
        ▼
Calculate Similarity
        │
        ▼
Calculate Final Score
        │
        ▼
Rank Candidates
        │
        ▼
Generate Explanation
        │
        ▼
Return Recommendations
```

---

# 🧮 Recommendation Scoring

ShopGraph uses a weighted scoring model.

```text
Final Score =
    0.40 × Relationship Match
  + 0.25 × Feature Compatibility
  + 0.15 × Category Match
  + 0.10 × Use Case Match
  + 0.10 × Similarity
```

The final score is normalized to a range of:

```text
0 – 100
```

### Components

| Component             | Weight | Purpose                               |
| --------------------- | -----: | ------------------------------------- |
| Relationship Match    |    40% | Measures direct graph relationships   |
| Feature Compatibility |    25% | Compares important product features   |
| Category Match        |    15% | Checks product category compatibility |
| Use Case Match        |    10% | Compares intended usage               |
| Similarity            |    10% | Measures overall product similarity   |

The score is a **recommendation score**, not a probability.

---

# 💡 Example Recommendation

Input:

```text
Dell Inspiron 15
```

Possible output:

```json
{
  "product": "Dell USB-C Hub",
  "score": 91.5,
  "reasons": [
    "Compatible with Dell Inspiron 15",
    "Both products support USB-C",
    "Useful for office and work-from-home scenarios"
  ]
}
```

Another recommendation:

```json
{
  "product": "Dell Laptop Stand",
  "score": 82.4,
  "reasons": [
    "Accessory for Dell Inspiron 15",
    "Suitable for office work",
    "Supports work-from-home use"
  ]
}
```

---

# 🔌 Backend API

The FastAPI backend exposes REST endpoints.

## Health Check

```http
GET /
```

Example:

```text
http://127.0.0.1:8000/
```

---

## Get All Products

```http
GET /products
```

Example:

```text
http://127.0.0.1:8000/products
```

---

## Get Product Details

```http
GET /products/{product_name}
```

Example:

```text
GET /products/Dell%20Inspiron%2015
```

---

## Get Recommendations

```http
GET /recommend/{product_name}?top_k=5
```

Example:

```text
GET /recommend/Dell%20Inspiron%2015?top_k=5
```

The API returns ranked recommendation candidates with their scores and explanations.

---

# 🎨 Frontend

The frontend provides a modern interface for interacting with ShopGraph.

Main features include:

* Product selection
* Recommendation generation
* Recommendation cards
* Recommendation scores
* Explanation of recommendations
* Knowledge Graph visualization
* Loading states
* Error handling
* Responsive design

### User Flow

```text
Open ShopGraph
      │
      ▼
Select Product
      │
      ▼
Click "Get Recommendations"
      │
      ▼
Frontend calls FastAPI
      │
      ▼
FastAPI queries Neo4j
      │
      ▼
Recommendation engine calculates scores
      │
      ▼
Results returned to React
      │
      ▼
Recommendations displayed
```

---

# 📁 Project Structure

```text
ShopGraph/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── kg_loader.py
│   │   ├── candidate_generator.py
│   │   ├── recommender.py
│   │   └── explanation.py
│   │
│   ├── scripts/
│   │   ├── setup_database.py
│   │   ├── load_kg.py
│   │   └── test_recommendation.py
│   │
│   ├── tests/
│   │   ├── test_database.py
│   │   ├── test_recommender.py
│   │   └── test_api.py
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── data/
│   ├── products.csv
│   ├── categories.csv
│   ├── features.csv
│   ├── brands.csv
│   ├── use_cases.csv
│   └── relationships.csv
│
├── cypher/
│   ├── 01_constraints.cypher
│   ├── 02_create_nodes.cypher
│   ├── 03_create_relationships.cypher
│   ├── 04_sample_queries.cypher
│   └── 05_visualization.cypher
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── ProductSelector.jsx
│   │   │   ├── RecommendationCard.jsx
│   │   │   ├── RecommendationGrid.jsx
│   │   │   ├── ScoreBadge.jsx
│   │   │   ├── ExplanationPanel.jsx
│   │   │   ├── KnowledgeGraph.jsx
│   │   │   ├── LoadingState.jsx
│   │   │   └── EmptyState.jsx
│   │   │
│   │   ├── pages/
│   │   │   └── Home.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── .env.example
│
├── .gitignore
├── README.md
└── requirements.txt
```

> The exact file structure may vary slightly depending on the current implementation.

---

# ⚙️ Local Setup

## Prerequisites

Install the following:

* Python 3.10+
* Node.js 18+
* npm
* Neo4j Desktop or Neo4j Aura
* Git

---

# 1. Clone the Repository

```bash
git clone https://github.com/Raghava-2812/ShopGraph.git
```

Move into the project:

```bash
cd ShopGraph
```

---

# 2. Configure Neo4j

Start your local Neo4j database or create a Neo4j Aura database.

Example local configuration:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

For Neo4j Aura, use the URI provided by Aura:

```env
NEO4J_URI=neo4j+s://your-database.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

Create:

```text
backend/.env
```

Do not commit this file to GitHub.

---

# 3. Setup Python Backend

Open a terminal in the project root:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```cmd
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 4. Load the Knowledge Graph

If the project uses the Python KG loader:

```bash
python scripts/load_kg.py
```

This loads the product data and relationships into Neo4j.

You can then inspect the graph using Neo4j Browser.

---

# 5. Start the Backend

From the project root:

```cmd
cd ..
python -m uvicorn backend.app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 6. Start the Frontend

Open another terminal.

```cmd
cd frontend
```

Install dependencies:

```cmd
npm install
```

Create:

```text
frontend/.env
```

with:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the development server:

```cmd
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🔐 Environment Variables

## Backend

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

## Frontend

```env
VITE_API_URL=http://127.0.0.1:8000
```

Never commit real passwords, API keys, or secrets.

---

# 🧪 Testing

Run backend tests with:

```bash
pytest
```

You can also test the API using:

* Swagger UI
* Postman
* Browser
* React frontend

Example:

```text
GET /products
```

and:

```text
GET /recommend/Dell%20Inspiron%2015?top_k=5
```

---

# 🌐 Deployment

ShopGraph can be deployed using:

```text
Frontend  → Vercel
Backend   → Render
Database  → Neo4j Aura
```

Production architecture:

```text
                         Internet
                            │
                            ▼
                  ┌──────────────────┐
                  │ React + Vite     │
                  │     Vercel       │
                  └────────┬─────────┘
                           │ HTTPS
                           ▼
                  ┌──────────────────┐
                  │ FastAPI + Python │
                  │     Render       │
                  └────────┬─────────┘
                           │
                           │ Neo4j Driver
                           ▼
                  ┌──────────────────┐
                  │    Neo4j Aura    │
                  │ Knowledge Graph  │
                  └──────────────────┘
```

### Backend Start Command

For Render:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend

Set the Vercel environment variable:

```env
VITE_API_URL=https://your-backend-url.onrender.com
```

Update FastAPI CORS configuration to allow the deployed frontend URL.

---

# 🔒 Security Considerations

ShopGraph follows basic application security practices:

* Secrets stored in environment variables.
* `.env` excluded from Git.
* API credentials are not hard-coded.
* CORS configured for frontend communication.
* Neo4j credentials are not exposed to the frontend.
* Database access is performed by the backend.
* Frontend communicates with the backend through REST APIs.

---

# 📈 Future Improvements

Possible future improvements include:

* User-specific recommendation history.
* Collaborative filtering.
* Purchase history based recommendations.
* More advanced graph traversal.
* Graph embeddings.
* Semantic similarity using transformer models.
* Vector database integration.
* Personalized recommendation profiles.
* Real-time recommendation updates.
* Larger product knowledge graphs.
* Recommendation feedback and evaluation metrics.
* Authentication and user accounts.
* Admin dashboard for Knowledge Graph management.

---

# 🎓 Project Highlights

ShopGraph demonstrates the integration of:

```text
Knowledge Graphs
        +
Graph Database
        +
Recommendation Algorithms
        +
REST APIs
        +
Modern Web Development
```

The project combines **Neo4j graph relationships** with a transparent weighted scoring mechanism to produce recommendations that can be explained to users.

---

# 📌 Key Learning Outcomes

Through this project, the following concepts are demonstrated:

* Knowledge Graph modeling
* Neo4j database design
* Cypher queries
* Graph traversal
* Candidate generation
* Recommendation scoring
* Explainable recommendations
* REST API development
* FastAPI
* React
* Vite
* Tailwind CSS
* API integration
* Environment configuration
* Git/GitHub
* Cloud deployment

---

# 👨‍💻 Author

**Ch. Raghava**

B.Tech Computer Science and Engineering

GitHub:
https://github.com/Raghava-2812

---

# 📄 License

This project is intended for educational and academic purposes.
