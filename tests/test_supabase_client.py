import sys
import types
import importlib


class FakeClient:
    def __init__(self):
        self.auth = object()
        self.table = object()
        self.storage = object()


def reset_supabase_singletons(module):
    module._supabase_client = None
    module._supabase_admin_client = None


def _import_sc_with_fake_config(monkeypatch, fake_cfg):
    monkeypatch.setitem(sys.modules, "app.core.config", fake_cfg)
    if "app.utils.supabase_client" in sys.modules:
        del sys.modules["app.utils.supabase_client"]
    import app.utils.supabase_client as sc
    return sc


def test_get_supabase_client_initializes_with_env(monkeypatch):
    # Install a fake lightweight config module to avoid importing heavy settings
    fake_cfg = types.ModuleType("app.core.config")
    fake_cfg.get_supabase_url = lambda: "https://example.supabase.co"
    fake_cfg.get_supabase_anon_key = lambda: "anon-key"
    fake_cfg.get_supabase_service_key = lambda: "service-key"
    sc = _import_sc_with_fake_config(monkeypatch, fake_cfg)

    reset_supabase_singletons(sc)

    created = {}

    def fake_create_client(url, key):
        created["url"] = url
        created["key"] = key
        return FakeClient()

    monkeypatch.setattr(sc, "create_client", fake_create_client)

    client1 = sc.get_supabase_client()
    client2 = sc.get_supabase_client()

    assert isinstance(client1, FakeClient)
    assert client1 is client2  # singleton
    assert created == {
        "url": "https://example.supabase.co",
        "key": "anon-key",
    }


def test_get_supabase_admin_client_initializes_with_env(monkeypatch):
    fake_cfg = types.ModuleType("app.core.config")
    fake_cfg.get_supabase_url = lambda: "https://example.supabase.co"
    fake_cfg.get_supabase_anon_key = lambda: "anon-key"
    fake_cfg.get_supabase_service_key = lambda: "service-key"
    sc = _import_sc_with_fake_config(monkeypatch, fake_cfg)

    reset_supabase_singletons(sc)

    created = {}

    def fake_create_client(url, key):
        created["url"] = url
        created["key"] = key
        return FakeClient()

    monkeypatch.setattr(sc, "create_client", fake_create_client)

    client1 = sc.get_supabase_admin_client()
    client2 = sc.get_supabase_admin_client()

    assert isinstance(client1, FakeClient)
    assert client1 is client2  # singleton
    assert created == {
        "url": "https://example.supabase.co",
        "key": "service-key",
    }


def test_missing_env_for_client_raises_value_error(monkeypatch):
    fake_cfg = types.ModuleType("app.core.config")
    fake_cfg.get_supabase_url = lambda: ""
    fake_cfg.get_supabase_anon_key = lambda: ""
    fake_cfg.get_supabase_service_key = lambda: "service-key"
    sc = _import_sc_with_fake_config(monkeypatch, fake_cfg)

    reset_supabase_singletons(sc)

    try:
        sc.get_supabase_client()
        assert False, "Expected ValueError for missing URL/anon key"
    except ValueError as e:
        assert "must be configured" in str(e)


def test_missing_env_for_admin_client_raises_value_error(monkeypatch):
    fake_cfg = types.ModuleType("app.core.config")
    fake_cfg.get_supabase_url = lambda: ""
    fake_cfg.get_supabase_anon_key = lambda: "anon-key"
    fake_cfg.get_supabase_service_key = lambda: ""
    sc = _import_sc_with_fake_config(monkeypatch, fake_cfg)

    reset_supabase_singletons(sc)

    try:
        sc.get_supabase_admin_client()
        assert False, "Expected ValueError for missing URL/service role key"
    except ValueError as e:
        assert "must be configured" in str(e)


def test_auth_database_storage_accessors(monkeypatch):
    fake_cfg = types.ModuleType("app.core.config")
    fake_cfg.get_supabase_url = lambda: "https://example.supabase.co"
    fake_cfg.get_supabase_anon_key = lambda: "anon-key"
    fake_cfg.get_supabase_service_key = lambda: "service-key"
    sc = _import_sc_with_fake_config(monkeypatch, fake_cfg)

    reset_supabase_singletons(sc)

    fake = FakeClient()

    def fake_create_client(url, key):
        return fake

    monkeypatch.setattr(sc, "create_client", fake_create_client)

    # Prime the singleton
    _ = sc.get_supabase_client()

    assert sc.get_auth_client() is fake.auth
    assert sc.get_database_client() is fake.table
    assert sc.get_storage_client() is fake.storage


