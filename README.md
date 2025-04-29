[![CI](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/ci.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/ci.yml)
[![CD](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/cd.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/cd.yml)
[![log github events](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/event-logger.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/event-logger.yml)

# Final Project

## Introduction
Geographic Journal is a Flask-based web application for journaling and visualizing your travels on an interactive map. We integrate the Google Maps API to power location search, autocomplete suggestions, and reverse geocoding—allowing users to easily find places by name or address.

Users can:

- **Log** places they’ve visited with date, name, address, companions, category, rating (including half-star increments), and a review.
- **Browse** all entries on an interactive map or in a recent-entries list, clicking markers to reveal detailed information.
- **Edit & Delete** existing entries as needed.

## Deploy Site

http://69.55.54.82:5001/ 

## Team

- [Jinzhi Cao](https://github.com/eth3r3aI)

- [Lan Yao](https://github.com/ziiiimu)

- [Lauren Zhou](https://github.com/laurenlz)

- [Lily Fu](https://github.com/fulily0325)

## Container Images
- [Web-App](https://hub.docker.com/r/eth3r3ai/lastone)
- MongoDB: Hosted on Mongo Atlas.

## System Requirements

- **Python**: 3.10 or higher
- **Docker**: Latest stable version
- **Docker Compose**: Included with Docker Desktop or install separately
- **MongoDB**: 
  - Local instance (via Docker) or 
  - MongoDB Atlas cluster (for cloud deployment)

## Prerequisites

- MongoDB setup locally / cloud
- Google Cloud API set up

## Setup

1. Install Docker and Docker Compose
2. Clone this repository
3. Paste the connection string we've sent you over Discord, or set up your own database using Mongo Atlas and copy your connection string into a .env file in the web-app folder with the following format:
```
MONGO_DBNAME=geometric_journal_db
MONGO_URI=your_mongodb_uri
SECRET_KEY='12345'
GOOGLE_MAP_API_KEY=your_google_cloud_api_key
```
3. Run `docker-compose up --build`
4. Go to http://localhost:5001

## Tests
1. Create a new folder under root folder named `env
2. Within that folder, enter for the test env that we lrovide, or enter your own credentials
```
MONGO_DBNAME=test
TEST_MONGO_URI=your_mongodb_uri
SECRET_KEY='12345'
GOOGLE_MAP_API_KEY=your_google_cloud_api_key
```
```
2. Run the following commands in the root directory
```
pip install -e .
pytest -v app/tests
```

## Configuration

- MongoDB runs on port 27017
- Web app runs on port 5001