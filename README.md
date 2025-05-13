# Grocery Store Microservices Application

## Overview

This project is a containerized microservices-based grocery store system. It consists of five independent microservices responsible for various functionalities such as user management, product storage, ordering, product search, and logging. Each microservice has its own database (SQLite) and communicates with other services using HTTP requests. The system is built to be scalable, secure, and modular, using Docker for containerization and JWT for user authentication.

## Features

- **Microservices**: The system is split into five microservices:
  1. **User Management**: Handles user registration, authentication, and role-based access control.
  2. **Product Storage**: Manages product information, such as adding, editing, and deleting products.
  3. **Ordering**: Handles the creation and management of customer orders.
  4. **Product Search**: Provides search functionality for products based on user queries.
  5. **Logging**: Logs key system events for monitoring and debugging purposes.

- **Containerization**: All services are containerized using Docker for easy deployment and scalability.
- **Authentication**: Secure user authentication using JWT tokens. Roles are defined for store employees and customers, controlling access to various parts of the system.
- **Database**: Each microservice manages its own SQLite database to maintain data isolation and ensure scalability.

## Technologies Used

- **Python** (Flask): For building the microservices.
- **Docker**: For containerization of each microservice.
- **SQLite**: For lightweight, file-based database management for each microservice.
- **JWT (JSON Web Tokens)**: For secure user authentication and role-based access control.
- **Docker Compose**: To manage multiple containers and their interconnections.
