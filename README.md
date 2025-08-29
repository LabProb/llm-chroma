
```
### Install
```bash
make init        # create .venv install prod + dev dependencies
make venv        # create virtual environment
make install     # install prod
make install-dev # install prod + dev dependencies
make run         # run FastAPI with autoreload
```
### Launch
```bash
uvicorn app.main:app --reload
```
### Testing
``` bash
make test       # Run tests
make lint       # Check style (ruff)
make format     # Autoformatting
make coverage   # Coverage report
make check      # Run lint, test, and coverage
```

### Clean environment
``` bash
make clean      # Clean .pyc, __pycache__, .coverage
```

### Help
``` bash
make help       # Show help message
```

### Structure
```
├── app
│   ├── config.py
│   ├── llm
│   │   ├── llama.py
│   │   └── llama_wrapper.py
│   ├── main.py
│   ├── routes
│   │   ├── generate.py
│   │   └── ping.py
│   └── services
│       ├── generator.py
│       └── rag.py
├── chroma_store
├── frontend
│   ├── static
│   │   └── style.css
│   └── templates
│       └── index.html
├── Makefile
├── models
├── pytest.ini
├── README.md
├── requirements-dev.txt
├── requirements.txt
└── tests
    ├── test_generate.py
    └── test_ping.py

```
### Stack
```
Python 3.12
FastAPI
llama-cpp-python
Pytest + Coverage
Ruff
```