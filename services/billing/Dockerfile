FROM python:3.11-slim AS builder
WORKDIR /build
COPY billing/app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN pip uninstall -y setuptools wheel
WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY billing/app/ .
COPY shared/ /app/shared/
RUN chown -R appuser:appuser /app
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 8003
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
