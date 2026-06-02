# SEO Crawler

## Overview
A full-stack SEO crawler that crawls websites, extracts SEO metadata, stores crawl results in a database, and provides a React dashboard for monitoring crawl jobs.

## Features
- Crawl websites
- robots.txt support
- Job queue
- Progress tracking
- Results table
- Sortable results
- Metrics tracking
- Database storage

## Tech Stack
Frontend:
- React
- TypeScript
- Axios

Backend:
- FastAPI
- Python

Database:
- SQLite / NeonDB

## Setup

### Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

### Frontend
cd frontend
npm install
npm run dev

## API Endpoints
POST /jobs
GET /jobs/{id}
GET /jobs/{id}/pages
POST /process-next-job
GET /metrics

## Design Patterns Used

### Queue Pattern
Jobs are placed into a queue and processed asynchronously.

### Separation of Concerns
Crawler logic, database logic, and API logic are separated into different modules.

### Data Access Layer
Database operations are encapsulated inside database.py.

## Graph Traversal
The crawler uses Breadth First Search (BFS).

Steps:
1. Start from root URL.
2. Visit page.
3. Extract links.
4. Add unseen links to queue.
5. Continue until page limit is reached.
