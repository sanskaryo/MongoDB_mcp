# 🍽️ MongoDB Analytics Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.127+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-19.2+-61DAFB.svg" alt="React">
  <img src="https://img.shields.io/badge/MongoDB-Latest-47A248.svg" alt="MongoDB">
  <img src="https://img.shields.io/badge/MCP-FastMCP-purple.svg" alt="MCP">
</p>

A powerful full-stack analytics platform for restaurant/hotel management using **FastAPI**, **LangGraph**, **FastMCP (Model Context Protocol)**, and **React**. Ask natural language questions and get intelligent insights from your MongoDB data with AI-powered analytics and chart generation.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language Queries** | Ask questions like "What are the top selling items?" or "Show me revenue trends" |
| 🔧 **19+ MCP Tools** | Comprehensive analytics tools for revenue, customers, menu, orders, and operations |
| 🤖 **LangGraph Agent** | Intelligent AI orchestration using Google Gemini 3 Flash |
| 📊 **Chart Generation** | Automatic visualization of data with Matplotlib & Seaborn |
| ⚡ **Real-time Analytics** | Direct MongoDB connection for live data insights |
| 🎨 **Modern React UI** | Beautiful chat interface with Markdown support |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                            │
│                    (Vite + React 19.2)                          │
│                      Port: 5173                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/REST
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Server                               │
│              (REST API + LangGraph Agent)                       │
│                      Port: 8001                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              LangGraph Agent (Gemini 3)                  │   │
│  │         - Natural Language Processing                    │   │
│  │         - Tool Selection & Orchestration                 │   │
│  │         - Response Generation                            │   │
│  └────────────────────────┬────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │ MCP Protocol (Streamable HTTP)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastMCP Server                              │
│                  (Model Context Protocol)                        │
│                      Port: 8000                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    19+ MCP Tools                         │   │
│  │  - mongodb_query, mongodb_aggregate, mongodb_insert     │   │
│  │  - get_revenue_analytics, get_customer_insights         │   │
│  │  - get_menu_performance, generate_chart, etc.           │   │
│  └────────────────────────┬────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │ PyMongo
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MongoDB                                   │
│                 (restaurant_analytics DB)                        │
│                     Port: 27017                                  │
│  Collections: orders, customers, menu_items, delivery_details   │
│               users, audit_logs, inventory, feedback, staff     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
MongoDB_mcp/
├── main_dir/                      # Main application directory
│   ├── server.py                  # MCP Server entry point
│   ├── seed_db.py                 # Database seeding script
│   ├── requirements.txt           # Python dependencies
│   ├── api_server/                # FastAPI Application
│   │   ├── fastapi_server.py      # REST API server (Port 8001)
│   │   ├── agents/
│   │   │   └── langgraph_agent.py # LangGraph + Gemini Agent
│   │   └── helpers/
│   │       └── chart_generator.py # Chart generation utilities
│   └── mcp_server/                # MCP Server Components
│       ├── tools/                 # 19+ MCP Tool implementations
│       ├── models/                # Pydantic data models
│       └── utils/                 # Database client & utilities
├── frontend/
│   └── mongo_mcp_frontend/        # React Frontend (Vite)
│       ├── src/
│       │   ├── App.js             # Main chat interface
│       │   └── index.js           # React entry point
│       └── package.json
├── data/                          # Sample JSON datasets
├── Database_query/                # Educational MongoDB examples
│   └── mongodb_concepts/          # Query patterns & concepts
├── pyproject.toml                 # Project configuration
├── Dockerfile                     # Container configuration
└── ARCHITECTURE.md                # Detailed architecture docs
```

---

## 🔧 Available MCP Tools

### Core MongoDB Operations
| Tool | Description |
|------|-------------|
| `mongodb_query` | Execute find queries on any collection |
| `mongodb_aggregate` | Run aggregation pipelines |
| `mongodb_insert` | Insert new documents |
| `mongodb_update` | Update existing documents |
| `mongodb_get_collections` | List all available collections |
| `mongodb_describe_collection` | Get collection schema and stats |

### Revenue & Analytics
| Tool | Description |
|------|-------------|
| `get_revenue_analytics` | Comprehensive revenue insights |
| `get_revenue_by_date` | Revenue for specific date ranges |
| `get_menu_revenue` | Revenue breakdown by menu items |
| `quick_stats` | Quick overview of key metrics |

### Customer Intelligence
| Tool | Description |
|------|-------------|
| `get_customer_insights` | Deep customer behavior analysis |
| `get_customer_segments` | Customer segmentation data |

### Operations & Orders
| Tool | Description |
|------|-------------|
| `get_order_status` | Order status distribution |
| `get_order_types` | Order type breakdown (dine-in, delivery, etc.) |
| `get_operational_metrics` | Operational performance metrics |
| `search_orders` | Search orders by various criteria |

### Menu & Visualization
| Tool | Description |
|------|-------------|
| `get_menu_performance` | Menu item performance analysis |
| `generate_chart` | Create visualizations from data |
| `get_data_range` | Check available data date ranges |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** (recommended) or 3.11+
- **Node.js 18+** & npm
- **MongoDB** (running on `localhost:27017`)
- **Google API Key** (for Gemini 3 Flash)

### 1. Clone & Setup Environment

```bash
git clone https://github.com/sanskaryo/MongoDB_mcp.git
cd MongoDB_mcp
```

### 2. Backend Setup

```bash
# Navigate to main directory
cd main_dir

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env

# Seed the database with sample data
python seed_db.py
```

### 3. Start the Servers

**Terminal 1 - MCP Server (Port 8000):**
```bash
cd main_dir
python server.py
```

**Terminal 2 - API Server (Port 8001):**
```bash
cd main_dir/api_server
python fastapi_server.py
```

### 4. Frontend Setup

```bash
# In a new terminal
cd frontend/mongo_mcp_frontend

# Install dependencies
npm install

# Start development server (Port 5173)
npm run dev
```

### 5. Access the Application

Open your browser and navigate to: **http://localhost:5173**

---

## 💬 Example Queries

Try asking these questions in the chat interface:

```
📊 "What are the top 5 selling menu items?"
💰 "Show me revenue trends for the last 30 days"
👥 "What are my customer segments?"
📈 "Generate a chart showing order types distribution"
🍕 "Which menu category generates the most revenue?"
📦 "What's the status of pending orders?"
🔍 "Search for orders over $50"
📉 "Show me operational metrics for this month"
```

---

## 🐳 Docker Support

```bash
# Build the image
docker build -t mongodb-analytics-agent .

# Run with MongoDB
docker run -p 8000:8000 -p 8001:8001 \
  -e GOOGLE_API_KEY=your_key \
  -e MONGO_URI=mongodb://host.docker.internal:27017 \
  mongodb-analytics-agent
```

---

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google API key for Gemini 3 | ✅ Yes |
| `MONGO_URI` | MongoDB connection string | ❌ No (defaults to `localhost:27017`) |

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance REST API framework
- **FastMCP** - Model Context Protocol server implementation
- **LangGraph** - Agent orchestration and workflow management
- **LangChain** - LLM integration and tool management
- **Google Gemini 3 Flash** - AI model for natural language processing
- **PyMongo** - MongoDB driver for Python
- **Pandas** - Data manipulation and analysis
- **Matplotlib/Seaborn** - Chart and visualization generation

### Frontend
- **React 19.2** - Modern UI library
- **Vite 7** - Fast build tool and dev server
- **Axios** - HTTP client
- **React-Markdown** - Markdown rendering in chat
- **Lucide React** - Icon library

### Database
- **MongoDB** - NoSQL document database

---

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- [Database_query/mongodb_concepts/](Database_query/mongodb_concepts/) - MongoDB query examples and patterns

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Sanskar Yadav**
- GitHub: [@sanskaryo](https://github.com/sanskaryo)

---

<p align="center">
  Made with ❤️ using MongoDB, FastMCP, and AI
</p>
