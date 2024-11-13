Restaurant Website:

This project is a restaurant website built using Django Rest Framework (DRF). It consists of two main apps:

1. **Customer App**: Handles customer-related functionalities, including user registration, profiles, and orders.
2. **Control App**: Manages other aspects of the restaurant, such as menu items, reservations, and orders.

Features:

- **Customer Management**: Allows customers to register, log in, and manage their profiles.
- **Menu Management**: Admins can add, update, and delete menu items.
- **Order Processing**: Customers can place orders, and the system handles order statuses.
- **Reservations**: Customers can make and manage reservations.
- **Staff Management**: Admins can manage staff details and roles.
- **Authentication**: Secure authentication using JSON Web Tokens (JWT).

Usage:

- Access the API documentation at `http://127.0.0.1:8000/` after starting the server.
- Use the provided endpoints to interact with the customer and control apps.

Authentication:

- The project uses JWT (JSON Web Tokens) for authentication. Ensure to include the token in the Authorization header with each request.

Contributing:

- Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.
