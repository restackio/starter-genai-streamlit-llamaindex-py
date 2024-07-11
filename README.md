# GenAI Starter - Llamaindex - Streamlit - Restack

An example of how to deploy a [LLamaindex](https://www.llamaindex.ai/) application with [Streamlit](https://streamlit.io/) with Restack orchestration.

---

# Run locally

## Frontend

./frontend pip i && streamlit run frontend.py

Streamlit frontend available at:
localhost:8501

## Backend

Requirements

brew install temporal

Start temporal server
temporal server start-dev

Temporal server available at:
localhost:8233

./backend pip i && python backend.py

# Run in docker

docker compose up -d --build
Will start frontend, backend and temporal server

Streamlit frontendavailable at:
localhost:8501

Temporal server available at:
localhost:8233

### Deploy

Link to Restack deploy template
