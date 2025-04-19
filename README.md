# ModConnect - Social Media Platform

Welcome to **ModConnect**, a Django-based social media platform where users can create accounts, follow each other, post updates, and interact through likes and comments.

## Features

- User authentication and profile management
- Posting, liking, and commenting on posts
- Follow and unfollow users
- PostgreSQL for database management
- Docker for containerization
- Gunicorn as the WSGI server

## Tech Stack

- **Backend**: Django (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript, JQuery, AJAX
- **Deployment**: Docker, Gunicorn

---

## Getting Started

Follow these steps to set up the project locally.

### Prerequisites

Ensure you have the following installed:

- [Python 3.8+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Git](https://git-scm.com/)

---

### Installation

1. **Clone the Repository**  
   Clone the repository to your local machine:
   ```bash
   git clone https://github.com/gaurabn1/ModConnect.git
   cd ModConnect
   ```
   
2. **Set Up the Environment**  
   Create a .env file based on the .env.example file:
   ```bash
   cp .env.example .env
   ```
  
   The .env file will be automatically generated with the following content. Make sure to not modify it:
   ```bash  
    DB_NAME=your_db_name
    DB_USER=your_username
    DB_PASSWORD=your_password
    DB_HOST=postgres_mod
    DB_PORT=5432
    SECRET_KEY=your_secret_key_here
   ```

3. **Using Docker**  
   To run the project in a Docker container, use the following commands:
   ```bash
   docker-compose up --build
   ```
   
 Access the application at http://localhost:8000.

##Folder Structure
  ```
  ├── core/              # Core application logic
  ├── templates/         # HTML templates
  ├── static/            # Static assets (CSS, JS, images)
  ├── media/             # Media files (user uploads)
  ├── ModConnect/        # Main Django app
  ├── docker-compose.yml # Docker configuration
  ├── Dockerfile         # Docker image configuration
  ├── manage.py          # Django management script
  ├── requirements.txt   # Python dependencies
  ├── .env               # Environment variables
  └── venv/              # Virtual environment (not included in Git)
  ```
##Contributions

Contributions are welcome! Please open an issue or submit a pull request for any bugs or improvements.

## Contact

For questions or collaboration, feel free to reach out:

- **Author**: Gaurab Neupane
- **GitHub**: [gaurabn1](https://github.com/gaurabn1)

  
