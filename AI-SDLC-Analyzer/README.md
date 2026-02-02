# AI-SDLC-Analyzer

AI-SDLC-Analyzer is a .NET 9.0 project designed to analyze Software Development Life Cycle (SDLC) requirements using Machine Learning. It provides tools for semantic search and analysis of requirements against defined standards.

## Project Structure

The project follows a layered architecture:

- **src/API**: A Minimal API for exposing SDLC analysis services.
- **src/UI**: An ASP.NET Core MVC application providing a web interface.
- **src/Domain**: Contains core entities and interfaces.
- **src/Infrastructure.Data**: Data access implementation (e.g., repositories).
- **src/Infrastructure.Services**: Business logic and application services.
- **src/Infrastructure.Resource**: ML.NET integration, semantic search, and NLP processing.
- **ModelTraining**: A console application for training the ML.NET model.
- **tests**: Unit and integration tests for various components.

## Requirements

- [.NET 9.0 SDK](https://dotnet.microsoft.com/download/dotnet/9.0)
- IDE: Visual Studio 2022, JetBrains Rider, or VS Code with C# Dev Kit.

## Setup & Run

### 1. Restore Dependencies
```bash
dotnet restore
```

### 2. Train the Model (Optional)
If `src/Infrastructure.Resource/ml_model.zip` is missing or needs updating, run the ModelTraining project:
```bash
dotnet run --project ModelTraining/ModelTraining.csproj
```

### 3. Run the Web UI
```bash
dotnet run --project src/UI/UI.csproj
```
The UI should be available at `http://localhost:5000` or `https://localhost:5001` (check console output for exact ports).

### 4. Run the API
```bash
dotnet run --project src/API/API.csproj
```
The API documentation (OpenAPI) is typically available at `/openapi/v1.json` or through Swagger (if configured).

## Scripts & Commands

- **Build solution:** `dotnet build`
- **Run tests:** `dotnet test`
- **Watch UI for changes:** `dotnet watch run --project src/UI/UI.csproj`

## Environment Variables

Currently, the project uses default `appsettings.json` configurations.
- `ASPNETCORE_ENVIRONMENT`: Set to `Development` or `Production`.

TODO: Document specific environment variables for database connections or external AI services if added.

## Testing

Tests are located in the `tests/` directory.
- `tests/Domain.Tests`: Unit tests for domain logic.
- `tests/Infrastructure.Data.Tests`: Tests for data access.

Run all tests:
```bash
dotnet test
```

## License

TODO: Add license information.
