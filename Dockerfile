FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt && pip cache purge

ARG PORT
EXPOSE ${PORT:-80}

CMD streamlit run --server.port ${PORT:-80} app.py