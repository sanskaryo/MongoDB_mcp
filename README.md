# MongoDB Analytics Agent

A full-stack application for restaurant analytics using FastAPI, LangGraph, FastMCP, and React.

## Project Structure

- `main/`: Backend (FastAPI, LangGraph, FastMCP)
- `frontend/mongo_mcp_frontend/`: Frontend (React + Vite)

## Prerequisites

1.  **Python 3.11+**
2.  **Node.js & npm**
3.  **MongoDB** (Running on `localhost:27017`)
4.  **Anthropic API Key** (Claude 3.5 Haiku)

## Setup Instructions

### 1. Backend Setup

1.  Navigate to the `main/` directory.
2.  Create a `.env` file based on `.env.example` and add your `ANTHROPIC_API_KEY`.
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Seed the database with sample data:
    ```bash
    python seed_db.py
    ```
5.  Run the FastAPI server:
    ```bash
    python main.py
    ```

### 2. Frontend Setup

1.  Navigate to `frontend/mongo_mcp_frontend/`.
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```

## Features

- **Natural Language Queries**: Ask questions like "What are the top selling items?"
- **MCP Tools**: 19+ specialized analytics tools (currently 3 implemented as a start).
- **LangGraph Orchestration**: Intelligent agent workflow using Claude 3.5.
- **Real-time Data**: Connects directly to MongoDB for live analytics.
