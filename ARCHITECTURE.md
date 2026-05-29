# Architecture Overview

This document provides an architecture overview of the conyag-max project.

## System Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        UI["User Interface"]
        CLI["Command Line Interface"]
    end
    
    subgraph API["API Layer"]
        REST["REST API"]
        GraphQL["GraphQL API"]
    end
    
    subgraph Business["Business Logic Layer"]
        Services["Core Services"]
        Processing["Data Processing"]
        Validation["Validation Layer"]
    end
    
    subgraph Data["Data Layer"]
        DB[(Database)]
        Cache["Cache Layer"]
        FileStorage["File Storage"]
    end
    
    subgraph External["External Services"]
        ThirdParty["Third-party APIs"]
        Analytics["Analytics"]
    end
    
    UI -->|HTTP/WS| REST
    CLI -->|gRPC| REST
    REST --> Services
    GraphQL --> Services
    Services --> Processing
    Processing --> Validation
    Validation --> DB
    Validation --> Cache
    Services --> FileStorage
    Services --> ThirdParty
    Services --> Analytics
```

## Component Interaction

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Service
    participant DB
    
    User->>API: Request
    API->>Service: Process Request
    Service->>DB: Query/Update Data
    DB-->>Service: Response
    Service-->>API: Result
    API-->>User: Response
```

## Data Flow

```mermaid
graph LR
    Input["Input Data"] --> Transform["Transformation"]
    Transform --> Validate["Validation"]
    Validate --> Process["Processing"]
    Process --> Output["Output Data"]
    Process -.->|Error| ErrorHandler["Error Handler"]
    ErrorHandler -.-> Output
```

---

**Last Updated:** 2026-05-29

For more information about this project, see the main README.
