# AI Stripper

You can find this tool online at [https://aistripper.nls.io](https://aistripper.nls.io)

This project consists of a Node.js/Vite/React frontend (`ui`) and a Python/Uvicorn fastapi backend (`api`).

## Prerequisites

*   Node.js (v22 or as specified in `.upsun/config.yaml`)
*   npm (or pnpm, as indicated by `ui/package.json`)
*   Python (v3.12 or as specified in `.upsun/config.yaml`)
*   pip
*   Upsun CLI (for deployment)
*   Access to a PostgreSQL database (for local API development)

## Project Structure

```
.
├── .upsun/               # Upsun configuration
│   └── config.yaml
├── api/                  # Python backend
│   ├── app.py            # Main application file
│   └── requirements.txt  # Python dependencies (YOU NEED TO CREATE THIS)
├── ui/                   # Node.js frontend
│   ├── src/
│   ├── public/
│   ├── dist/             # Build output
│   └── package.json
└── README.md
```

## Running Locally

### 1. API (Python Backend)

The API is a Python application using Uvicorn.

1.  **Navigate to the API directory:**
    ```bash
    cd api
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the API server:**
    The Upsun config uses `uvicorn app:app --port $PORT --workers 4`. Locally, you can run:
    ```bash
    uvicorn app:app --reload --port 8000 # Or any other port you prefer
    ```
    The API should now be running, typically at `http://localhost:8000`.

### 2. UI (Node.js Frontend)

The UI is a Node.js application built with Vite and React.

1.  **Navigate to the UI directory:**
    ```bash
    cd ui
    ```

2.  **Install dependencies:**
    Your `package.json` specifies `pnpm` as the package manager.
    ```bash
    pnpm install
    ```
    (If you prefer npm, you can use `npm install`, but `pnpm` is recommended based on your `package.json`)

3.  **Run the development server:**
    The `package.json` includes a `dev` script.
    ```bash
    pnpm run dev
    ```
    This will typically start a development server (e.g., `http://localhost:5173`).

4.  **For a production-like local serve (optional, mimics Upsun):**
    Upsun builds the UI and serves the static files.
    a.  **Build the project:**
        ```bash
        pnpm run build
        ```
        This command is `tsc -b && vite build` and will output files to the `ui/dist` directory.
    b.  **Serve the `dist` folder:**
        Upsun uses `http-server`. You might need to install it globally or as a dev dependency if you haven't already:
        ```bash
        npm install -g http-server  # Or pnpm add -D http-server
        ```
        Then serve the files:
        ```bash
        http-server dist/ --cors
        ```
        This will serve the UI, likely on `http://localhost:8080`.

## Deployment with Upsun

This project is configured for deployment on Upsun.

1.  **Ensure the Upsun CLI is installed and you are logged in.**
    ```bash
    upsun login
    ```

2.  **Link your local repository to an Upsun project (if not already done):**
    ```bash
    upsun project:set <PROJECT_ID>
    ```

3.  **Commit your changes:**
    ```bash
    git add .
    git commit -m "Configure for Upsun deployment"
    ```

4.  **Push to deploy:**
    ```bash
    upsun push
    ```
    Or, if you are working on a specific environment:
    ```bash
    git push upsun <branch_name>
    ```

Upsun will then follow the build and deploy hooks defined in `.upsun/config.yaml`:
*   **For the `api`:** It will run `pip install -r requirements.txt`. (The `alembic upgrade head` is currently commented out in the deploy hook).
*   **For the `ui`:** It will run `npm install`, `npm install -g http-server`, and `npm run build` (which is `tsc -b && vite build`).

The application will be accessible via the URLs defined in your Upsun project, corresponding to the routes in `.upsun/config.yaml`.