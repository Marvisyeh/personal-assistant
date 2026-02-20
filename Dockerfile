# Stage 1: Base Image
FROM python:3.12-slim AS base

WORKDIR /app
COPY . .

RUN pip install uv \
  && uv pip install --system . \
  && rm -rf /root/.cache /usr/local/bin/uv /usr/local/lib/python3.12/site-packages/uv*

  
# Stage 3: Production Image
FROM python:3.12-slim AS prod

WORKDIR /app
COPY --from=base /usr/local /usr/local
COPY --from=base /app /app

EXPOSE 8000

# Run from app/src so imports (api, config, core) resolve; main.py defines app
WORKDIR /app/app/src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# Stage 2: Development Image
FROM base AS dev

RUN pip install uv
# RUN uv pip install --system --group dev