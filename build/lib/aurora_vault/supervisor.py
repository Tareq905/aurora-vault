import importlib.resources

def stream_vault_data():
    try:
        path = importlib.resources.files('aurora_vault.assets').joinpath('datasets.txt')

        with path.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    yield line

    except Exception as e:
        print(f"◌ Supervisor Error: {e}")