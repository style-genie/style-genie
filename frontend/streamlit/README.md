# :wrench: Developer Guide


### Evaluate dependencies
```shell
(ls .env.local && echo 'INFO: Found .env.local') || echo 'CRITICAL: Missing .env.local'
(ls requirements.txt && echo 'INFO: Found requirements.txt') || echo 'CRITICAL: Missing requirements.txt'
```

### Create Python environment and install dependencies
```shell
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### Start the Streamlit app

```shell
python3 -m streamlit run src/app.py --server.port 8080 --server.address 0.0.0.0
```
