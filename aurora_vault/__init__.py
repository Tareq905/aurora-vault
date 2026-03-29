from .interface import print_signature, welcome_ui
from .engine import VaultEngine
from .config import ensure_dirs


def load():
    ensure_dirs()
    print_signature()

    engine = VaultEngine()

    # FORCE initialization (to ensure indexing runs)
    welcome_ui("Preparing large dataset...")
    engine.initialize()

    return engine