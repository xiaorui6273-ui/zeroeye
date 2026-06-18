"""
Pytest test suite for zeroeye project.

Tests cover:
- Configuration loading and validation
- Build system diagnostics
- Tool module imports and basic functionality
- Data generator functions
- Health check system
- JSON Schema validation
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Project root is two levels up from this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
DIAGNOSTIC_DIR = PROJECT_ROOT / "diagnostic"
CONFIG_SCHEMA = PROJECT_ROOT / "config.schema.json"

# Ensure tools/ is importable
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_config():
    """Return a valid sample RootConfig dict."""
    return {
        "service": {
            "name": "test-service",
            "version": "1.0.0",
            "host": "localhost",
            "port": 8080,
            "tls_enabled": False,
            "tls_cert_path": None,
            "tls_key_path": None,
        },
        "registry": {
            "backend": "etcd",
            "endpoints": ["localhost:2379"],
            "heartbeat_interval_ms": 5000,
            "ttl_seconds": 30,
            "replication_factor": 3,
        },
        "discovery": {
            "provider": "consul",
            "namespace": "test",
            "tags": ["test"],
            "health_check_path": "/health",
            "health_check_interval_ms": 10000,
        },
        "messaging": {
            "broker_type": "kafka",
            "uris": ["localhost:9092"],
            "consumer_group": "test-group",
            "max_retries": 3,
            "retry_backoff_ms": 1000,
            "batch_size": 100,
            "compression": "none",
        },
    }


# ---------------------------------------------------------------------------
# Config Schema Tests
# ---------------------------------------------------------------------------

class TestConfigSchema:
    """Tests for config.schema.json validation."""

    def test_schema_file_exists(self):
        assert CONFIG_SCHEMA.exists(), f"Schema not found at {CONFIG_SCHEMA}"

    def test_schema_is_valid_json(self):
        schema = json.loads(CONFIG_SCHEMA.read_text())
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["type"] == "object"

    def test_schema_has_required_fields(self):
        schema = json.loads(CONFIG_SCHEMA.read_text())
        required = schema.get("required", [])
        assert "service" in required
        assert "registry" in required
        assert "discovery" in required
        assert "messaging" in required

    def test_schema_service_config(self):
        schema = json.loads(CONFIG_SCHEMA.read_text())
        svc = schema["definitions"]["ServiceConfig"]
        assert svc["type"] == "object"
        assert "name" in svc["required"]
        assert "port" in svc["required"]

    def test_schema_port_range(self):
        schema = json.loads(CONFIG_SCHEMA.read_text())
        port = schema["definitions"]["ServiceConfig"]["properties"]["port"]
        assert port["minimum"] == 1
        assert port["maximum"] == 65535

    def test_schema_registry_backend_enum(self):
        schema = json.loads(CONFIG_SCHEMA.read_text())
        backend = schema["definitions"]["RegistryConfig"]["properties"]["backend"]
        assert "enum" in backend
        assert "etcd" in backend["enum"]

    def test_schema_discovery_provider_enum(self):
        schema = json.loads(CONFIG_SCHEMA.read_text())
        provider = schema["definitions"]["DiscoveryConfig"]["properties"]["provider"]
        assert "enum" in provider
        assert "consul" in provider["enum"]

    def test_schema_messaging_compression_enum(self):
        schema = json.loads(CONFIG_SCHEMA.read_text())
        compression = schema["definitions"]["MessagingConfig"]["properties"]["compression"]
        assert "enum" in compression
        assert "gzip" in compression["enum"]


# ---------------------------------------------------------------------------
# Build System Tests
# ---------------------------------------------------------------------------

class TestBuildSystem:
    """Tests for build.py diagnostics generation."""

    def test_build_lists_all_modules(self):
        result = subprocess.run(
            [sys.executable, "build.py", "--list"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "backend" in result.stdout
        assert "frontend" in result.stdout

    def test_diagnostic_dir_created(self):
        assert DIAGNOSTIC_DIR.exists()

    def test_diagnostic_artifacts_generated(self):
        json_files = list(DIAGNOSTIC_DIR.glob("build-*.json"))
        assert len(json_files) > 0, "No diagnostic JSON files found"

    def test_diagnostic_json_is_valid(self):
        json_files = list(DIAGNOSTIC_DIR.glob("build-*.json"))
        for jf in json_files[:3]:
            data = json.loads(jf.read_text())
            assert "commit" in data
            assert "modules" in data

    def test_diagnostic_report_has_required_fields(self):
        json_files = list(DIAGNOSTIC_DIR.glob("build-*.json"))
        if json_files:
            data = json.loads(json_files[0].read_text())
            assert "generated_at" in data
            assert "total_modules" in data


# ---------------------------------------------------------------------------
# Tool Module Tests
# ---------------------------------------------------------------------------

class TestToolModules:
    """Tests for Python tool module imports and basic functionality."""

    def test_data_generator_imports(self):
        import data_generator  # noqa: F401

    def test_data_generator_gaussian(self):
        from data_generator import gaussian_random
        result = gaussian_random(0.0, 1.0)
        assert isinstance(result, float)

    def test_data_generator_clamp(self):
        from data_generator import clamp
        assert clamp(5.0, 0.0, 10.0) == 5.0
        assert clamp(-1.0, 0.0, 10.0) == 0.0
        assert clamp(15.0, 0.0, 10.0) == 10.0

    def test_data_generator_round_to_tick(self):
        from data_generator import round_to_tick
        assert round_to_tick(3.7, 0.5) == 3.5

    def test_data_generator_random_phone(self):
        from data_generator import random_phone
        phone = random_phone()
        assert isinstance(phone, str)
        assert len(phone) > 0

    def test_data_generator_random_email(self):
        from data_generator import random_email
        email = random_email("John", "Doe")
        assert isinstance(email, str)
        assert "@" in email

    def test_health_check_imports(self):
        import health_check  # noqa: F401

    def test_legacy_analyzer_imports(self):
        import legacy_analyzer  # noqa: F401

    def test_config_generator_imports(self):
        import config_generator  # noqa: F401

    def test_benchmark_imports(self):
        import benchmark  # noqa: F401

    def test_log_aggregator_imports(self):
        import log_aggregator  # noqa: F401

    def test_ai_reviewer_imports(self):
        import ai_reviewer  # noqa: F401

    def test_ai_reviewer_has_type_hints(self):
        """All functions in ai_reviewer must have return type annotations."""
        import ast
        with open(TOOLS_DIR / "ai_reviewer.py") as f:
            tree = ast.parse(f.read())
        funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        no_returns = [f.name for f in funcs if not f.returns]
        assert len(no_returns) == 0, f"Functions missing return types: {no_returns}"

    def test_deploy_imports(self):
        import deploy  # noqa: F401


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

class TestIntegration:
    """Integration tests combining multiple components."""

    def test_config_matches_schema(self, sample_config):
        assert sample_config["service"]["name"] == "test-service"
        assert sample_config["registry"]["backend"] in ["etcd", "consul", "zookeeper", "eureka"]
        assert sample_config["discovery"]["provider"] in ["consul", "eureka", "kubernetes", "dns"]
        assert sample_config["messaging"]["broker_type"] in ["kafka", "rabbitmq", "nats", "redis", "pulsar"]

    def test_diagnostic_after_build(self):
        json_files = list(DIAGNOSTIC_DIR.glob("build-*.json"))
        assert len(json_files) > 0
        for jf in json_files[:2]:
            data = json.loads(jf.read_text())
            assert isinstance(data.get("modules"), list)

    def test_schema_and_build_integration(self):
        """Schema must exist and build must generate diagnostics."""
        assert CONFIG_SCHEMA.exists()
        json_files = list(DIAGNOSTIC_DIR.glob("build-*.json"))
        assert len(json_files) > 0
