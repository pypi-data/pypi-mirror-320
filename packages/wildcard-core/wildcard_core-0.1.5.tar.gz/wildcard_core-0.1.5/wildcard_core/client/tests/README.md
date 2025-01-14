# Tool Search Tests

This repository contains unit tests for parsing OpenAPI endpoints and generating readable schemas within the Tool Search module.

## Prerequisites

- Python 3.6 or higher
- `requests` library
- Other dependencies as specified in your project's `requirements.txt`

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-repo/tool_search.git
   cd tool_search
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Running the Tests

### 1. Parse All OpenAPI Endpoints

This test parses all OpenAPI endpoints and validates their readable schemas.

**Command:**

```bash
python3 -m wildcard_core.tool_search.tests.testParseOpenApi
```

**Usage:**

- Ensure that the test environment is properly configured.
- The test will automatically fetch and process all endpoints.

### 2. Parse a Single OpenAPI Endpoint by ID

This test parses a single OpenAPI endpoint identified by its endpoint ID.

**Command:**

```bash
python3 -m wildcard_core.tool_search.tests.testParseOpenApiById <endpoint_id> [<index_name>]
```

**Parameters:**

- `<endpoint_id>`: **(Required)** The ID of the endpoint to parse.
- `<index_name>`: **(Optional)** The name of the collection. If not provided, it defaults to the collection name set in the test environment.

**Example:**

```bash
python3 -m wildcard_core.tool_search.tests.testParseOpenApiById 12345 my_collection
```

## Notes

- Ensure that your configuration files and environment variables are set correctly before running the tests.
- Logging is configured to display informational messages. You can adjust the logging level in the test scripts if needed.

## Troubleshooting

- **Missing Dependencies:** If you encounter `ImportError`, make sure all dependencies are installed by running `pip install -r requirements.txt`.
- **Configuration Issues:** Verify that the `setup_test_environment` function in your test scripts is correctly setting up the necessary configurations.

## Contributing

Feel free to submit issues or pull requests for improvements and bug fixes.

## License

[MIT License](LICENSE)