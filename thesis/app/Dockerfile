# Stage 1: Install dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY app_requirements.txt ./
RUN pip install --no-cache-dir -r app_requirements.txt

# Stage 2: Copy dependencies and app source into the final image
FROM python:3.11-slim AS runtime
WORKDIR /app
# copy only Python packages
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
# copy source files - check .dockerignore for ignored files
COPY . . 

# set proper working directory
WORKDIR /app/Gregorian_chant_repertoire


EXPOSE 8000
CMD ["python", "Gregorian_chant_repertoire/manage.py", "runserver", "0.0.0.0:8000"]