# DPAChain – Blockchain-based Thesis Authentication System

DPAChain is a proof-of-concept system developed as part of an engineering thesis at Warsaw University of Technology. It provides a decentralized way to verify the authenticity of diploma theses using blockchain technology.

The system stores thesis metadata in a distributed ledger backed by a custom blockchain with a Proof of Authority (PoA) consensus. It supports digital signatures, JWT-based verification, and peer-to-peer communication between academic institutions in the blockchain system -- to share blocks.

## 🛠️ Components

- **dpachain-api**: FastAPI-based backend with a custom blockchain and P2P communication layer.
- **dpachain-frontend**: Node.js + Express.js web frontend (available at `localhost:3000` or `3001`).
- **dpachain-app**: Tkinter-based desktop application for independent verification of JWT tokens.
- **docs/**: Thesis document (in Polish with the concept aviable in english), UML diagrams, and screenshots.

## 📦 Directory Structure

```
├── docker-compose.yml                # Default single-node system
├── docker-compose-second-node.yml   # Compose file for second node instance (to communicate with the first node)
├── docs/                             # Documentation, UML, thesis PDF (in Polish)
├── dpachain-api/                     # Backend API with custom blockchain
├── dpachain-app/                     # Desktop verifier app (Tkinter)
├── dpachain-frontend/                # Node.js web interface
└── README.md
```

## Prerequisites
To run the system, you need to have Docker and Docker Compose installed on your machine. You can find installation instructions for your operating system in the [Docker documentation](https://docs.docker.com/get-docker/).

The RSA keys are provided and stored in the `dpachain-api/signing_keys` directory. 


## 🚀 Running the System


To run the **first node** of the system, use the following command:

```bash
docker compose up --build
```
This command will build and start the backend API, frontend, and MongoDB database.
 
To run **second node** and test peer-to-peer communication:

```bash
docker compose -f docker-compose-second-node.yml up --build
```

- Frontends will be available at:
  - Node 1: [http://localhost:3000](http://localhost:3000)
  - Node 2: [http://localhost:3001](http://localhost:3001)

- Swagger API docs:
  - Node 1: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Node 2: [http://localhost:8001/docs](http://localhost:8001/docs)

🧠 The genesis block must be created via the Swagger interface before using the system - just use the /generate_genesis_block API endpoint.

## 📄 Thesis

The full engineering thesis (in Polish) can be found in:

```
docs/Projekt_dyplomowy_2_0-5.pdf
```

---

> This project was developed as part of a Computer Science engineering degree at Warsaw University of Technology. It demonstrates the feasibility of decentralized diploma verification using blockchain.
