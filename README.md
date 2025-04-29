[![CI](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/ci.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/ci.yml)
[![CD](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/cd.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/cd.yml)
[![log github events](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/event-logger.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-lastone/actions/workflows/event-logger.yml)

# Final Project

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

## Introduction
Geometric Journal is a Flask-based web application for journaling and visualizing your travels on an interactive map. We integrate the Google Maps API to power location search, autocomplete suggestions, and reverse geocoding—allowing users to easily find places by name or address.

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

- Docker installed on your system
- Python 3.9+ for local development (optional - containers include Python)

## Setup

1. Install Docker and Docker Compose
2. Clone this repository
3. Run `docker-compose up --build`
4. Go to http://localhost:5001

## Configuration

- MongoDB runs on port 27017
- Web app runs on port 5001