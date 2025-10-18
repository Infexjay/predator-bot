# Predator Trading Bot

This repository contains the source code for the Predator Trading Bot, a full-stack trading application with a React frontend, FastAPI backend, and Supabase for the database and authentication.

## Architecture

- **Frontend**: React, Vite, TailwindCSS, shadcn/ui
- **Backend**: FastAPI, Python
- **Database**: Supabase (PostgreSQL)

## Getting Started

### Prerequisites

- Node.js and npm (or yarn)
- Python 3.8+ and pip
- Docker (optional, for containerized deployment)

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file and add your Supabase credentials:
    ```
    SUPABASE_URL="your-supabase-url"
    SUPABASE_KEY="your-supabase-key"
    ```
4.  Train the machine learning model by running the training script:
    ```bash
    python train_model.py
    ```
    *This will fetch the latest market data, train the model, and create an `xgboost_model.json` file in the `backend` directory.*

5.  Start the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```

### Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install the required Node.js packages:
    ```bash
    npm install
    ```
3.  Install `tailwindcss` and its peer dependencies, then generate your `tailwind.config.js` and `postcss.config.js` files:
    ```bash
    npm install -D tailwindcss postcss autoprefixer
    npx tailwindcss init -p
    ```
    *Note: The `frontend/src/index.css` file has already been configured with the necessary Tailwind directives.*
4.  (Optional) Initialize `shadcn/ui` to add new components:
    ```bash
    npx shadcn-ui@latest init
    ```
5.  Start the Vite development server:
    ```bash
    npm run dev
    ```

## Deployment

- The frontend is intended to be deployed on Vercel.
- The backend is intended to be deployed on Koyeb.