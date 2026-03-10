# CRM GraphQL Neo4j API

A production-ready CRM (Customer Relationship Management) backend powered by **GraphQL** and **Neo4j Graph Database**. This project demonstrates how to model complex business relationships (Accounts, Contacts, Leads, Deals) as a graph and expose them through a flexible GraphQL API.

## 🚀 Key Features

- **Graph Data Modeling**: Leverages Neo4j to handle complex relationships natively.
- **GraphQL API**: Provides a single endpoint to fetch related data in a single request.
- **Dual Implementation**:
  - **Python Stack**: FastAPI + Strawberry GraphQL.
  - **Node.js Stack**: Apollo Server + `@neo4j/graphql` library.
- **Sales Analytics**: Built-in logic for Sales Dashboard metrics (Pipeline Value, Forecast, Conversion Rates).
- **Automated Schema**: Direct mapping from GraphQL types to Neo4j nodes and relationships.

## 🛠️ Tech Stack

### Database
- **Neo4j**: Graph database for storing CRM entities and their relationships.
- **Cypher**: Query language for complex graph traversals.

### Backend (Python)
- **FastAPI**: Modern, fast (high-performance) web framework.
- **Strawberry GraphQL**: Python library for building GraphQL APIs.
- **Neo4j Python Driver**: Official driver for database connectivity.

### Backend (Node.js)
- **Apollo Server**: Industry-standard GraphQL server.
- **@neo4j/graphql**: Official library for auto-generating Cypher from GraphQL.
- **neo4j-driver**: JavaScript driver for Neo4j.

## 📂 Project Structure

```text
.
├── src/
│   └── schema.js        # Node.js GraphQL TypeDefs and Resolvers
├── index.js             # Node.js Server entry point
├── main.py              # Python FastAPI entry point
├── schema.py            # Python GraphQL Schema and Logic
├── database.py          # Neo4j Driver configuration (Python)
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
└── test-db.js           # Database connectivity tests
```

## 🚀 Getting Started

### 1. Prerequisites
- [Neo4j AuraDB](https://neo4j.com/cloud/aura/) (Free tier) or Neo4j Desktop installed locally.
- Python 3.9+
- Node.js 18+

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
PORT=4000
```

### 3. Setup - Python Version
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```
Access the GraphQL playground at `http://localhost:4000/graphql`.

### 4. Setup - Node.js Version
```bash
# Install dependencies
npm install

# Run the server
npm start
```
Access the Apollo Sandbox at `http://localhost:4000`.

## 📊 Data Model

- **Account**: Organizations or companies.
- **Contact**: Individual people belonging to an Account.
- **Lead**: Potential sales opportunities derived from Contacts.
- **Deal**: Commercial agreements generated from Leads.
- **Stage**: Sales pipeline stages (e.g., Prospecting, Negotiation, Closed Won).
- **Activity**: Interactions like calls, emails, or meetings.

## 🔍 Example Queries and Mutations

### 1. Sales Dashboard Analytics
Fetch a summary of your sales pipeline:
```graphql
query GetSalesDashboard {
  salesDashboard {
    totalDealsValue
    forecastedValue
    conversionRate
  }
}
```

### 2. Create an Account (Org)
```graphql
mutation CreateNewAccount {
  createAccount(name: "Acme Corp", industry: "Technology") {
    id
    name
    industry
  }
}
```

### 3. Fetch Accounts with Contacts
Get all accounts and their linked personnel:
```graphql
query GetAccountsAndContacts {
  accounts {
    name
    industry
    contacts {
        name
        email
        position
    }
  }
}
```

### 4. Create a Contact & Link to Account
```graphql
mutation CreateContact {
  createContact(
    name: "John Doe", 
    email: "john@acme.com", 
    accountId: "REPLACE_WITH_ACCOUNT_ID", 
    position: "CTO"
  ) {
    id
    name
    email
  }
}
```

> **Note**: Field names might vary slightly between Python (`name`) and Node.js (`firstName`, `lastName`) implementations.

## 🤝 Contributing
Feel free to fork this project and submit PRs for any improvements or additional CRM features!
