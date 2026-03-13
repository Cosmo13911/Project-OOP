FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server.py .

# copy all files
COPY . .

#ren mcp server
CMD ["python", "mcp_server.py"]