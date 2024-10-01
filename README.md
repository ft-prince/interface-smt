
---

# Interface With Machine

This project provides an interface to interact with machines via a web-based application. It allows users to control and monitor various machine operations, manage media files, and configure process settings using a user-friendly interface.

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Running Daphne for ASGI](#running-daphne-for-asgi)
5. [Technologies Used](#technologies-used)
6. [Contributing](#contributing)
7. [License](#license)
8. [Contact](#contact)

## Introduction

The **Interface With Machine** project is designed to provide an efficient interface for interacting with various machine operations, allowing media management, process control, and real-time data visualization. This system can handle multiple media files (PDFs, videos) for the machine stations and provides sliders for media presentation.

## Features

- Control machine media (PDF and video) via an interface.
- Manage machine stations and associated media.
- Configure settings for media sliders and process information.
- Real-time data interaction and monitoring.
- **Manage Fixture Cleaning Records (Create, Update, Delete, View).**
- **Manage Rejection Sheets.**
- **Track Soldering Bit Records.**

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ft-prince/InterfaceWithMachine.git
   cd InterfaceWithMachine
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser to access the admin interface:
   ```bash
   python manage.py createsuperuser
   ```

## Running Daphne for ASGI

To run the project using `daphne`, follow these steps:

1. Open your terminal and navigate to the project root.

2. Use the following command to run `daphne` with the specified host and port:

   ```bash
   daphne -b 127.0.0.1 -p 8000 sopdisplay_core.asgi:application
   ```

This will launch the interface on your local machine, making it accessible at `http://127.0.0.1:8000`.

## Technologies Used

- **Django** - Python Web Framework
- **Daphne** - ASGI Server
- **Python** - Backend Development
- **HTML/CSS/JavaScript** - Frontend Technologies
- **SQLite** - Default Database (can be replaced with other DBs like PostgreSQL)

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request to help improve this project.

## License

This project is licensed under the Renata License.

## Contact

For any inquiries, feel free to reach out at:

- **Email:** [Reanataiot.com]
- **GitHub:** [ft-prince](https://github.com/ft-prince)

---
