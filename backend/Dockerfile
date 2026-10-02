FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Build the model fresh with whatever scikit-learn version was just
# installed above -- guarantees the pickle always matches the library
# that will load it, instead of shipping a static file that can drift
# out of sync (see app/ml/build_model.py for why this matters).
RUN python app/ml/build_model.py

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
