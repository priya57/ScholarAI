# ScholarAI Test Suite Documentation

## Overview

Comprehensive test suite for the ScholarAI RAG system covering unit tests, integration tests, API tests, CLI tests, and performance tests.

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Shared fixtures and configuration
├── test_document_processor.py     # Document processing tests
├── test_vector_store.py           # Vector store tests
├── test_rag_engine.py             # RAG engine tests
├── test_api.py                    # API endpoint tests
├── test_cli.py                    # CLI functionality tests
├── test_integration.py            # End-to-end integration tests
└── test_performance.py            # Performance and load tests
```

## Installation

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

## Running Tests

### Quick Start

Run all tests:
```bash
python run_tests.py all
```

### Test Categories

**Unit Tests** - Test individual components in isolation:
```bash
python run_tests.py unit
```

**Integration Tests** - Test component interactions:
```bash
python run_tests.py integration
```

**API Tests** - Test REST API endpoints:
```bash
python run_tests.py api
```

**CLI Tests** - Test command-line interface:
```bash
python run_tests.py cli
```

**Performance Tests** - Test system performance and scalability:
```bash
python run_tests.py performance
```

**Fast Tests** - Run all tests except performance tests:
```bash
python run_tests.py fast
```

**Coverage Report** - Run tests with code coverage:
```bash
python run_tests.py coverage
```

### Using pytest Directly

Run specific test file:
```bash
pytest tests/test_document_processor.py -v
```

Run specific test:
```bash
pytest tests/test_document_processor.py::TestDocumentProcessor::test_init -v
```

Run tests matching pattern:
```bash
pytest -k "metadata" -v
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## Test Coverage

### Document Processor Tests (test_document_processor.py)

- ✅ Initialization with custom parameters
- ✅ Metadata extraction for placement papers
- ✅ Metadata extraction for mock tests
- ✅ Metadata extraction for learning materials
- ✅ Text extraction from TXT files
- ✅ Text extraction from RTF files (with/without library)
- ✅ Text extraction from images (with/without OCR)
- ✅ Document processing for supported formats
- ✅ Error handling for unsupported formats
- ✅ Directory processing with multiple files
- ✅ Error handling during directory processing
- ✅ Chunk metadata consistency

### Vector Store Tests (test_vector_store.py)

- ✅ Initialization and configuration
- ✅ Adding documents (empty list, success cases)
- ✅ Similarity search with/without filters
- ✅ Filtering by document type
- ✅ Filtering by company
- ✅ Filtering by subject
- ✅ Filtering by difficulty
- ✅ Getting available filters
- ✅ Collection count operations
- ✅ Collection deletion and reset
- ✅ Error handling

### RAG Engine Tests (test_rag_engine.py)

- ✅ Initialization with custom models
- ✅ Query with empty documents
- ✅ Query with documents (success cases)
- ✅ Confidence level calculation
- ✅ Error handling during queries
- ✅ Getting relevant documents
- ✅ Updating retriever configuration
- ✅ Content preview truncation
- ✅ Prompt template formatting

### API Tests (test_api.py)

- ✅ Health check endpoint
- ✅ Query endpoint (success/error)
- ✅ Filtered query endpoint
- ✅ Get available filters
- ✅ Search documents
- ✅ Upload documents (success/error)
- ✅ Upload directory (background task)
- ✅ Reset vector store
- ✅ Generate mock test
- ✅ Submit test
- ✅ Get student performance
- ✅ Document preview
- ✅ AI search assistant
- ✅ Mobile chat interface

### CLI Tests (test_cli.py)

- ✅ Component initialization
- ✅ Document ingestion (success/error)
- ✅ System queries
- ✅ System reset (confirmed/cancelled)
- ✅ Statistics display
- ✅ Command-line argument parsing
- ✅ Help functionality

### Integration Tests (test_integration.py)

- ✅ Complete document processing pipeline
- ✅ End-to-end RAG pipeline
- ✅ Document filtering integration
- ✅ Error handling across components
- ✅ Metadata consistency
- ✅ Chunking consistency
- ✅ Company detection
- ✅ Subject detection

### Performance Tests (test_performance.py)

- ✅ Document processing performance
- ✅ Chunking performance
- ✅ Vector store operations performance
- ✅ RAG query performance
- ✅ Concurrent document processing
- ✅ Memory usage monitoring
- ✅ Large query response time
- ✅ Metadata extraction performance
- ✅ Stress test with concurrent queries

## Test Fixtures

### Common Fixtures (conftest.py)

- `temp_dir` - Temporary directory for test files
- `sample_pdf_path` - Sample PDF file
- `sample_txt_path` - Sample text file
- `mock_openai_api_key` - Mock API key
- `document_processor` - DocumentProcessor instance
- `mock_vector_store_manager` - Mocked VectorStoreManager
- `mock_rag_engine` - Mocked RAGEngine

## Mocking Strategy

Tests use mocking to:
- Avoid external API calls (OpenAI)
- Isolate component testing
- Speed up test execution
- Ensure deterministic results

Key mocked components:
- OpenAI API (ChatOpenAI, OpenAIEmbeddings)
- ChromaDB (PersistentClient, Chroma)
- File system operations (when appropriate)

## Performance Benchmarks

Expected performance metrics:

| Operation | Target | Metric |
|-----------|--------|--------|
| Document Processing | > 1 doc/sec | 50 documents |
| Chunking | > 5 chunks/sec | Large documents |
| Vector Store Addition | < 10 sec | 100 documents |
| Search Operations | < 0.5 sec | Single search |
| RAG Query | < 2 sec | Single query |
| Concurrent Queries | > 2 queries/sec | 50 concurrent |
| Metadata Extraction | > 50/sec | 500 extractions |

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: python run_tests.py coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies
3. **Cleanup**: Use fixtures for setup/teardown
4. **Assertions**: Clear and specific assertions
5. **Documentation**: Document complex test scenarios
6. **Performance**: Keep tests fast (< 1 sec per test)
7. **Coverage**: Aim for > 80% code coverage

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

**Fixture Not Found**:
- Check conftest.py is present
- Verify fixture scope

**Slow Tests**:
- Use mocking for external calls
- Run fast tests: `python run_tests.py fast`

**Coverage Not Generated**:
```bash
# Install coverage plugin
pip install pytest-cov
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain > 80% coverage
4. Add integration tests for new features
5. Update this documentation

## Test Metrics

Run tests and generate metrics:

```bash
# Generate coverage report
python run_tests.py coverage

# View HTML report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

## Future Enhancements

- [ ] Add mutation testing
- [ ] Add property-based testing (Hypothesis)
- [ ] Add contract testing for API
- [ ] Add visual regression tests
- [ ] Add security testing (SAST)
- [ ] Add load testing with Locust
- [ ] Add E2E tests with Selenium

## Support

For test-related issues:
1. Check test logs for detailed errors
2. Run individual test files for isolation
3. Use `-v` flag for verbose output
4. Use `--tb=long` for full tracebacks

## License

Tests are part of the ScholarAI project and follow the same MIT License.