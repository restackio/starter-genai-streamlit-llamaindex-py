# GenAI Starter - Llamaindex - Streamlit - Restack

An example of how to deploy a [LLamaindex](https://www.llamaindex.ai/) application with [Streamlit](https://streamlit.io/) with Restack orchestration build with [Temporal](https://temporal.io).

---

# Start orchestator

python restack.py init

# Start with hot reloading

python restack.py dev

Streamlit frontend available at:
localhost:8501

Temporal orchestator available at:
localhost:8233

# Start without hot reloading

python restack.py up

# Stop

python restack.py down

---

# Run manually

## Run Temporal

brew install temporal
Start temporal server
temporal server start-dev

Temporal server available at:
localhost:8233

## Run Frontend

./frontend pip install -r requirements.txt && streamlit run frontend.py

Streamlit frontend available at:
localhost:8501

## Run Backend

./backend pip install -r requirements.txt && python backend.py
