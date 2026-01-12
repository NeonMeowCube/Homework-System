# Homework API

## Overview
This repository contains the Homework API, which is designed to manage and interact with homework data. The API is built using Flask and supports various endpoints for managing entries. Note that the API key upload functionality is still under development.

## Requirements
The following Python packages are required to run the API:

- Flask
- Flask-CORS
- TinyDB
- Gunicorn

You can install these dependencies using the `requirements.txt` file provided in the repository.

## Setup Instructions

### Step 1: Clone the Repository
Clone this repository to your local machine:
```bash
git clone <https://github.com/NeonMeowCube/Homework-UI.git>
cd Homework/Hw-API
```

### Step 2: Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Step 3: Run the API
You can run the API using Gunicorn. Gunicorn is a Python WSGI HTTP server for UNIX. It is a pre-fork worker model, which means it can handle multiple requests simultaneously.

Run the following command to start the server:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 api:app
```

- `-w 4`: Specifies the number of worker processes (adjust based on your system's resources).
- `-b 0.0.0.0:8000`: Binds the server to all network interfaces on port 8000.

### Step 4: Access the API
Once the server is running, you can access the API at:
```
http://localhost:8000
```

## Notes
- The API key upload functionality is still under development and will be available in a future update.
- Ensure that you have Python 3.10 installed on your system.
- Using nginx as an reverse proxy is recommeneded

## Future Updates
- Adding api key function to upload homework
- Adding support for image upload
- Adding support for admin page (some day)

## License
This project is licensed under the GPL v3.