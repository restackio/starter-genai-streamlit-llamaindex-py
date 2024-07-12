# GenAI Starter - Llamaindex - Streamlit - Restack

An example of how to deploy a [LLamaindex](https://www.llamaindex.ai/) application with [Streamlit](https://streamlit.io/) with Restack orchestration build with [Temporal](https://temporal.io).

---

# Run locally

python restack.py init
python restack.py dev

# Build and run in docker

python restack.py docker
python restack.py down

# Run locally individually

## Run temporal server

python restack.py init

## Or in terminal

brew install temporal
Start temporal server
temporal server start-dev

Temporal server available at:
localhost:8233

## Run Frontend

./frontend pip i && streamlit run frontend.py

Streamlit frontend available at:
localhost:8501

## Run Backend

./backend pip i && python backend.py
