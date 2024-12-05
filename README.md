# kanastra-challenge

## **Summary**
This project simulates the generation of invoices from a CSV file. It handles sending emails and generating invoices based on the data provided.

---

## **Pre-requisites**

Before running the project, ensure you have the following dependencies installed:

- **Python 3.10 or later**
- **Docker** and **Docker Compose**

We also recommend setting up a virtual environment on your local machine:

```bash
source path/to/your/venv/bin/activate
```

Then, install all required packages listed in `requirements.txt`:

```bash
pip install --no-cache-dir -r requirements.txt
```

---

## **Quick Start with Docker**

The easiest way to get the project running is by using Docker Compose. Follow these steps:

1. Clone the repository:

```bash
git clone git@github.com:rafaelandrade/kanastra-challenge.git
```

2. Start the application using Docker Compose:

```bash
docker-compose up --build
```

3. Access the application:

- Back-end: [http://localhost:8000](http://localhost:8000)

---

## **How to Test Locally**

We recommend using Postman or Insomnia to test the endpoints.

1. Send a POST request to the route:

```bash
http://0.0.0.0:8000/invoice/generate
```

2. In the body of the request, include the parameter `file`, which should be a CSV file.

---

## **Execute the Unittests Locally**

1. To execute the tests, run the script `run_tests.sh`:

```bash
./run_tests.sh
```

2. If the script is not executable, make it executable with the following command:

```bash
chmod +x run_tests.sh
```

---
