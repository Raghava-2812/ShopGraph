# ShopGraph — Knowledge Graph Powered E-Commerce Recommendation System

> **A complete e-commerce website where product recommendations happen automatically as part of the shopping journey — powered by Neo4j Knowledge Graph.**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Architecture](#3-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Neo4j Graph Model](#5-neo4j-graph-model)
6. [User Behavior Model](#6-user-behavior-model)
7. [Recommendation Pipeline](#7-recommendation-pipeline)
8. [Scoring Formula](#8-scoring-formula)
9. [Personalization](#9-personalization)
10. [Explanation Generation](#10-explanation-generation)
11. [Database Architecture](#11-database-architecture)
12. [Frontend Architecture](#12-frontend-architecture)
13. [Backend Architecture](#13-backend-architecture)
14. [Installation](#14-installation)
15. [Running the Application](#15-running-the-application)
16. [Demo Workflow](#16-demo-workflow)
17. [API Documentation](#17-api-documentation)
18. [Testing](#18-testing)
19. [Future Improvements](#19-future-improvements)

---

## 1. Project Overview

**ShopGraph** is a Knowledge Graph-powered e-commerce recommendation system. Unlike traditional recommendation engines that rely on collaborative filtering or black-box ML models, ShopGraph uses a **Neo4j Knowledge Graph** to represent product relationships explicitly — and derives recommendations by traversing these relationships.

Every recommendation comes with a **transparent explanation** rooted in actual graph data.

---

## 2. Problem Statement

Traditional recommendation systems suffer from:
- **Black-box predictions** — users can't understand why they're seeing recommendations
- **Cold-start problems** — new products or users get poor recommendations
- **Static recommendations** — recommendations don't respond to what users are doing right now

ShopGraph solves this by:
- Encoding product domain knowledge as a **graph** (compatibility, accessories, features, use cases)
- Deriving recommendations by **graph traversal** — always explainable
- Tracking **real user behavior** (views, searches, cart, purchases) to personalize automatically

---

## 3. Architecture

```
                        SHOPGRAPH E-COMMERCE

                             User
                              │
               ┌──────────────┴──────────────┐
               ↓                             ↓
           Browse/Search               Login/Register
               │
               ↓
         Product Catalog (Neo4j)
               │
               ↓
         Product Details Page
               │
         ┌─────┴─────┐
         ↓           ↓
      VIEW Event   Add to Cart
         │           │
         └─────┬─────┘
               ↓
        User Behavior Layer (SQLite)
               │
        ┌──────┴───────┐
        ↓              ↓
    Application      Neo4j
    Database       Knowledge Graph
    (SQLite)          │
        │          ┌──┴──────────────┐
        └──────────┤                 │
                   ↓                 ↓
         User Behavior          Graph Traversal
         Analysis               (Cypher Queries)
                   │                 │
                   └────────┬────────┘
                            ↓
               Recommendation Engine
                            │
                 Candidate Generation
                            │
                   Feature Analysis
                            │
                 Relationship Analysis
                            │
                 User Behavior Scoring
                            │
                 Scoring + Ranking
                            │
                 Explanation Generation
                            ↓
              Personalized Recommendations
                            │
                            ↓
                        React UI

    ┌─────────────────────────────────────┐
    │ You May Also Like                   │
    │ Compatible Products                 │
    │ Recommended Accessories             │
    │ Complete Your Setup (Cart)          │
    │ Recommended for You (Home)          │
    └─────────────────────────────────────┘
```

---

## 4. Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, React Router v6, Axios, Tailwind CSS |
| Backend | Python, FastAPI, Pydantic |
| Knowledge Graph | Neo4j (AuraDB), Cypher, Neo4j Python Driver |
| Application Database | SQLite (via SQLAlchemy) |
| Authentication | JWT (python-jose), bcrypt (passlib) |

---

## 5. Neo4j Graph Model

```
(:Product)
    │
    ├── BELONGS_TO ────→ (:Category)
    ├── MADE_BY ────────→ (:Brand)
    ├── HAS_FEATURE ────→ (:Feature)
    ├── USED_FOR ───────→ (:UseCase)
    │
    ├── COMPATIBLE_WITH → (:Product)   [direct compatibility]
    ├── ACCESSORY ──────→ (:Product)   [accessories]
    ├── WORKS_WITH ─────→ (:Product)   [works together]
    └── SIMILAR_TO ─────→ (:Product)   [same type, alternatives]
```

### Node Types

| Node | Key Properties |
|------|---------------|
| Product | name, price, description |
| Category | name, description |
| Brand | name, country |
| Feature | name, description |
| UseCase | name, description |

### Sample Products

| Product | Category | Price |
|---------|----------|-------|
| Dell Inspiron 15 | Laptop | ₹55,000 |
| HP Pavilion 15 | Laptop | ₹52,000 |
| Lenovo IdeaPad Slim 5 | Laptop | ₹57,000 |
| Logitech MX Master 3S | Mouse | ₹9,000 |
| Keychron K2 | Keyboard | ₹7,500 |
| Dell USB-C Hub | USB Hub | ₹4,500 |
| LG 24 inch Monitor | Monitor | ₹15,000 |
| Sony WH-1000XM5 | Headphones | ₹29,000 |
| Samsung T7 SSD 1TB | Storage | ₹8,500 |
| Logitech C920 Webcam | Webcam | ₹7,000 |

---

## 6. User Behavior Model

User behavior is tracked in **SQLite** (not Neo4j) to keep product knowledge separate from application state.

### Event Types

| Event | Trigger | Signal Strength |
|-------|---------|-----------------|
| `VIEW` | Opening a product page | Weak |
| `SEARCH` | Searching products | Medium |
| `ADD_TO_CART` | Adding to cart | Strong |
| `WISHLIST` | Wishlisting a product | Strong |
| `PURCHASE` | Completing checkout | Very Strong |
| `REMOVE_FROM_CART` | Removing from cart | Negative signal |

### Behavior Recording

Events are recorded **automatically** — no user action required:

- Product page opens → `VIEW` event recorded
- Search performed → `SEARCH` event recorded  
- "Add to Cart" clicked → `ADD_TO_CART` event recorded
- Order placed → `PURCHASE` event recorded for each item

---

## 7. Recommendation Pipeline

```
User opens product page
          │
          ↓
    1. Validate product exists in Neo4j
          │
          ↓
    2. Candidate Generation (graph traversal)
          │
     ┌────┴──────────────────────────────┐
     ↓           ↓          ↓            ↓
  Direct      Shared    Shared        Same
  Relations   Features  Use Cases     Category
  (A→B)      (A→F←B)   (A→U←B)      (A→C←B)
     └────┬──────────────────────────────┘
          │
          ↓
    3. Score each candidate (5 dimensions)
          │
     ┌────┴────────────────────────────────┐
     ↓        ↓         ↓        ↓         ↓
  Relation  Feature  Category  UseCase  Similarity
  Score     Score    Score     Score    Score
  (40%)     (25%)    (15%)     (10%)    (10%)
     └────┬────────────────────────────────┘
          │
          ↓
    4. Apply Personalization Boost (optional)
          │
          ↓
    5. Sort by final score
          │
          ↓
    6. Generate explanations
          │
          ↓
    7. Return top-K with sections
          │
      ┌───┴────────────────────┐
      ↓          ↓              ↓
  You May    Compatible     Accessories
  Also Like  With
```

---

## 8. Scoring Formula

### Graph Score (transparent, no ML)

```
Final Score = (
    0.40 × Relationship Score
  + 0.25 × Feature Score
  + 0.15 × Category Score
  + 0.10 × Use Case Score
  + 0.10 × Similarity Score
) × 100
```

### Relationship Score
Based on the strongest direct relationship:
- `COMPATIBLE_WITH` → 1.0
- `ACCESSORY` → 1.0
- `WORKS_WITH` → 0.9
- `SIMILAR_TO` → 0.6
- No direct relationship → 0.0

### Feature Score
```
feature_score = min(shared_features / source_features, 1.0)
```

### Category Score
- Same category → 0.6 (alternatives)
- Different category → 0.0

### Use Case Score
```
use_case_score = min(shared_use_cases / source_use_cases, 1.0)
```

### Similarity Score
- SIMILAR_TO relationship exists → 1.0
- Otherwise → 0.0

---

## 9. Personalization

After the base graph score is computed, a **personalization boost** is applied based on user behavior:

```
Personalization Boost:
  +3   recently viewed this product
  +5   in same category as recently viewed product
  +8   matches recent search term
  +10  in user's wishlist

Final Personalized Score = min(Graph Score + Boost, 100)
```

Additionally:
- Already **purchased** products are excluded from recommendations
- Products currently **in cart** are excluded from "Complete Your Setup"
- **Time decay**: Behavior from the last 30 days is weighted equally (future improvement: decay by recency)

---

## 10. Explanation Generation

Every recommendation includes human-readable reasons derived from **actual graph data**:

```
Dell USB-C Hub
Score: 91.4

Why recommended:
✓ Directly compatible with Dell Inspiron 15
✓ Shares USB-C connectivity feature
✓ Useful for Office Work
✓ Useful for Work From Home
```

For personalized recommendations:
```
Logitech MX Master 3S
Score: 88.7 (boosted)

Why recommended:
✓ Similar to products you recently viewed
✓ Matches your recent search for 'laptop'
✓ Compatible with Dell Inspiron 15
✓ Wireless and Bluetooth enabled
✓ Useful for Programming
```

All reasons come from real graph relationships or real user behavior — **never fabricated**.

---

## 11. Database Architecture

Two separate databases serve different purposes:

### Neo4j (Knowledge Graph)
Stores **product knowledge**:
- Product nodes with properties
- Category, Brand, Feature, UseCase nodes
- All product relationships (COMPATIBLE_WITH, ACCESSORY, etc.)

### SQLite (Application Database)
Stores **application state**:

```
users
  id, name, email, password_hash, created_at

carts
  id, user_id, created_at, updated_at

cart_items
  id, cart_id, product_name, quantity, price, added_at

orders
  id, user_id, status, total_amount, shipping_*, created_at

order_items
  id, order_id, product_name, quantity, price

user_events
  id, user_id, event_type, product_name, search_query, created_at
```

---

## 12. Frontend Architecture

```
src/
├── context/
│   ├── AuthContext.jsx      # JWT auth state
│   └── CartContext.jsx      # Cart state + operations
├── pages/
│   ├── HomePage.jsx         # Home + personalized recs
│   ├── ProductsPage.jsx     # Product catalog + filters
│   ├── ProductDetailPage.jsx # Product + auto recommendations
│   ├── SearchPage.jsx       # Search + SEARCH event
│   ├── CartPage.jsx         # Cart + cart recommendations
│   ├── CheckoutPage.jsx     # Checkout + order creation
│   ├── OrdersPage.jsx       # Order history
│   ├── ProfilePage.jsx      # User profile
│   ├── LoginPage.jsx        # Login form
│   └── RegisterPage.jsx     # Register form
├── components/
│   ├── Navbar.jsx           # Top navigation + search
│   ├── ProductCard.jsx      # Product grid card
│   ├── RecommendationCard.jsx # Recommendation card with reasons
│   └── RecommendationSection.jsx # Section wrapper with loading
├── services/
│   └── api.js               # All Axios API calls
└── App.jsx                  # Router + providers
```

### Key Frontend Behaviors

| Action | What Happens Automatically |
|--------|---------------------------|
| Open product page | VIEW event recorded, recommendations fetched |
| Perform search | SEARCH event recorded |
| Click "Add to Cart" | ADD_TO_CART event recorded, cart updated |
| View cart | Cart recommendations fetched |
| Complete checkout | PURCHASE events recorded, cart cleared |

---

## 13. Backend Architecture

```
backend/app/
├── main.py                  # FastAPI app, router registration
├── config.py                # Environment variables
├── database.py              # Neo4j connection (preserved)
├── sqlite_db.py             # SQLite ORM models + init
├── auth.py                  # JWT utilities, bcrypt
├── recommender.py           # ProductRecommender (preserved)
├── candidate_generator.py   # Graph traversal (preserved)
├── explanation.py           # Reason generation (preserved)
├── kg_loader.py             # KG data loader (preserved)
└── routers/
    ├── auth.py              # /auth/register, /auth/login, /auth/me
    ├── products.py          # /products, /products/search, /categories
    ├── events.py            # /events
    ├── cart.py              # /cart, /cart/items
    ├── orders.py            # /orders
    └── recommendations.py   # /recommendations/*
```

---

## 14. Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Neo4j (AuraDB cloud or local)

### Clone / Navigate
```bash
cd d:\KG_Projects\Product_Recomm\ShopGraph
```

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment
```bash
# Copy .env.example to .env
copy .env.example .env

# Edit .env with your credentials:
# NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
# NEO4J_USERNAME=neo4j
# NEO4J_PASSWORD=your_password
# JWT_SECRET=your-secret-key
```

### Load Knowledge Graph
```bash
# From backend directory (with venv activated)
python scripts/load_kg.py
```

### Frontend Setup
```bash
cd ..\frontend
npm install
```

---

## 15. Running the Application

### Start Backend
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Access
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 16. Demo Workflow

Follow this exact sequence to demonstrate all features:

### Step 1 — Open the website
Navigate to `http://localhost:5173`

### Step 2 — Register/Login
- Click **Login** → use demo account or register
- Demo: `demo@shopgraph.com` / `demo123`

### Step 3 — Search
- Type `laptop` in the search bar
- **System records**: `SEARCH` event

### Step 4 — Open Dell Inspiron 15
- Click the product from search results
- **System records**: `VIEW` event automatically
- **System displays**: Recommendations automatically (no button needed)

### Step 5 — See automatic recommendations
```
You May Also Like
  HP Pavilion 15       Compatible With        Recommended Accessories
  Lenovo IdeaPad Slim  Dell USB-C Hub         Dell Laptop Stand
                       Anker USB-C Hub        Dell Laptop Bag
```

### Step 6 — Add to Cart
- Click **Add to Cart** on Dell Inspiron 15
- **System records**: `ADD_TO_CART` event

### Step 7 — View Cart
- Navigate to Cart
- **System displays**: "Complete Your Setup" recommendations

### Step 8 — Browse More
- Open Logitech MX Master 3S
- **System records**: `VIEW` event

### Step 9 — Home Page Personalization
- Navigate back to Home
- **"Recommended for You"** now reflects your browsing history

### Step 10 — Checkout
- Add a few items → Go to Cart → Checkout
- Fill shipping info → Place Order
- **System records**: `PURCHASE` events for all items

### Step 11 — Future Recommendations
- All future recommendations now factor in your purchase history
- Purchased products will not be recommended again

---

## 17. API Documentation

Full interactive docs at: `http://localhost:8000/docs`

### Authentication
```
POST /auth/register     Register new user
POST /auth/login        Login with email/password → JWT token
GET  /auth/me           Get current user (requires JWT)
```

### Products (Neo4j)
```
GET /products                  List all products
GET /products?category=Laptop  Filter by category
GET /products/search?q=laptop  Search products
GET /products/categories       List all categories
GET /products/{name}           Full product details + relationships
```

### Events (SQLite)
```
POST /events
Body: { "event_type": "VIEW", "product_name": "Dell Inspiron 15" }
Body: { "event_type": "SEARCH", "search_query": "laptop" }
```

### Recommendations (Neo4j + SQLite)
```
GET /recommendations                           Personalized (home page)
GET /recommendations/product/{name}            Product page recommendations
GET /recommendations/product/{name}?top_k=8   With custom count
GET /recommendations/cart                      Cart recommendations
```

### Cart (SQLite)
```
GET    /cart                  Get cart with items
POST   /cart/items            Add item to cart
PATCH  /cart/items/{id}       Update quantity
DELETE /cart/items/{id}       Remove item
DELETE /cart                  Clear cart
```

### Orders (SQLite)
```
POST /orders         Create order from cart (triggers PURCHASE events)
GET  /orders         List user's orders
GET  /orders/{id}    Get specific order
```

---

## 18. Testing

### Backend Tests
```bash
cd backend
venv\Scripts\activate
pytest tests/test_backend.py -v
```

Tests cover:
- API health check
- Auth (register, login, invalid credentials)
- Products (list, search, categories, not found)
- Events (recording, invalid types)
- Cart (add, update, remove)
- Orders (create, list)
- Full user flow (register → view → cart → checkout)
- Recommendation endpoints

### Frontend Build Check
```bash
cd frontend
npm run build
```

---

## 19. Future Improvements

| Improvement | Description |
|-------------|-------------|
| Time decay | Weight recent events more heavily than old ones |
| Wishlist feature | Allow users to save products |
| Rating system | Let users rate products for better signals |
| Collaborative filtering | Add "users like you also bought" using user similarity |
| Real-time updates | WebSocket push for live recommendations |
| A/B testing | Test different scoring weights |
| Neo4j user nodes | Store user behavior in Neo4j for graph-based collaborative filtering |
| Mobile app | React Native version |
| Payment gateway | Razorpay/Stripe integration |
| Email notifications | Order confirmation emails |

---

## Scoring Formula Reference

```
Graph Score = (
    0.40 × rel_score       # COMPATIBLE_WITH/ACCESSORY = 1.0, SIMILAR_TO = 0.6
  + 0.25 × feature_score   # shared_features / source_features
  + 0.15 × category_score  # same_category = 0.6
  + 0.10 × use_case_score  # shared_use_cases / source_use_cases
  + 0.10 × similarity_score # SIMILAR_TO exists = 1.0
) × 100

Personalization Boost:
  +3   recently viewed
  +5   same category as viewed
  +8   matches search term
  +10  wishlisted

Final Score = min(Graph Score + Boost, 100)
```

---

*Built with ❤️ using Neo4j Knowledge Graph + FastAPI + React*
