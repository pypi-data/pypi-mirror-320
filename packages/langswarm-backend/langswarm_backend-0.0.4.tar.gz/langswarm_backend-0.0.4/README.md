# LangSwarm-Backend

LangSwarm-Backend is a lightweight, FastAPI-based backend designed to support LangSwarm's multi-agent ecosystem. It provides a scalable API layer and serves as the core integration point for managing and coordinating agent interactions.

## Features
- **FastAPI Framework**: High-performance API for seamless communication with LangSwarm agents.
- **Docker-Compatible**: Easily deployable as a container on local or cloud environments.
- **Scalable Architecture**: Built to run on Cloud Run or other serverless platforms for automatic scaling.
- **Multi-Agent Orchestration**: Handles API requests, message routing, and task execution for LangSwarm agents.

## Requirements
- Python 3.10 or higher
- Dependencies listed in `requirements.txt`

## Installation
Install LangSwarm-Backend and its dependencies via pip:
```bash
pip install langswarm-backend
```

## Usage

### Local Development
Run the backend locally:
```bash
python langswarm-backend/main.py
```
Access the API at `http://localhost:8080`.

### Deployment with Docker
Build and run the Docker container:
```bash
docker build -t langswarm-backend .
docker run -p 8080:8080 langswarm-backend
```

### Deployment on Cloud Run
1. Build the Docker image:
    ```bash
    docker build -t gcr.io/[PROJECT-ID]/langswarm-backend .
    ```
2. Push the image to Google Artifact Registry:
    ```bash
    docker push gcr.io/[PROJECT-ID]/langswarm-backend
    ```
3. Deploy to Cloud Run:
    ```bash
    gcloud run deploy langswarm-backend \
        --image gcr.io/[PROJECT-ID]/langswarm-backend \
        --region [REGION] \
        --platform managed \
        --allow-unauthenticated
    ```

## Environment Variables
- `APP_PORT`: Port to expose the backend (default: `8080`).
- Additional variables can be configured via `.env`.

## API Endpoints
### Example: Message Handling
- **POST `/send-message`**: Sends a message to the backend.
  ```json
  {
    "sender": "agent1",
    "content": "Hello, World!"
  }
  ```
- **GET `/get-messages`**: Retrieves all messages.

## Contributing
We welcome contributions to improve LangSwarm-Backend. To get started:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request for review.

## License
LangSwarm-Backend is licensed under the [MIT License](LICENSE).

## Support
For issues or questions, please open a GitHub issue or contact our team.
