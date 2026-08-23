from scripts.apply_pip_fixture_registration import RegistrationWriteError, apply_registration, validated_write_statements


SQL = """-- Protected automatic discovery in temporary single-provider mode.
START TRANSACTION;
INSERT INTO pip_fixtures (fixture_code, canonical_event_key, competition_key, kickoff_at, home_team_key, away_team_key, status)
VALUES ('A1BC234', 'hash', 'nor-eliteserien', '2026-08-30 12:00:00.000000', 'home', 'away', 'scheduled');
SET @pip_fixture_id = LAST_INSERT_ID();
INSERT INTO pip_provider_fixture_mappings (provider, provider_fixture_id, fixture_id, provider_updated_at)
VALUES ('odds-api', 'event-id', @pip_fixture_id, NULL);
SELECT fixture_id FROM pip_fixtures WHERE fixture_id = @pip_fixture_id;
SELECT provider FROM pip_provider_fixture_mappings WHERE fixture_id = @pip_fixture_id;
COMMIT;
"""


class FakeCursor:
    def __init__(self):
        self.rowcount = 0
        self._result = None

    def execute(self, statement, parameters=None):
        if "information_schema.COLUMNS" in statement:
            self._result = [(7,)]
        elif "information_schema.TABLES" in statement:
            self._result = [("pip_fixtures", "InnoDB"), ("pip_provider_fixture_mappings", "InnoDB")]
        elif statement.startswith("INSERT INTO"):
            self.rowcount = 1
        elif statement.startswith("SELECT COUNT(*) FROM pip_"):
            self._result = [(1,)]

    def fetchone(self):
        return self._result[0]

    def fetchall(self):
        return self._result

    def close(self):
        pass


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.started = False
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self, buffered=False):
        assert buffered is True
        return self.cursor_instance

    def start_transaction(self):
        self.started = True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class FakeConnector:
    def __init__(self):
        self.connection = FakeConnection()
        self.config = None

    def connect(self, **config):
        self.config = config
        return self.connection


def environment():
    return {
        "PIP_DB_HOST": "database.example.invalid",
        "PIP_DB_PORT": "3306",
        "PIP_DB_NAME": "pip",
        "PIP_DB_USER": "writer",
        "PIP_DB_PASSWORD": "protected",
    }


def test_validates_exact_single_provider_registration_shape():
    statements = validated_write_statements(SQL)
    assert len(statements) == 3
    assert sum(statement.startswith("INSERT INTO") for statement in statements) == 2


def test_rejects_second_provider_mapping():
    document = SQL.replace("SELECT fixture_id", "INSERT INTO pip_provider_fixture_mappings VALUES ('x','y',1,NULL);\nSELECT fixture_id")
    try:
        validated_write_statements(document)
    except RegistrationWriteError as error:
        assert str(error) == "registration_sql_shape_invalid"
    else:
        raise AssertionError("second provider mapping was accepted")


def test_applies_and_verifies_inside_one_tls_verified_transaction(monkeypatch, tmp_path):
    ca_file = tmp_path / "ca.pem"
    ca_file.write_text("test-ca", encoding="utf-8")
    monkeypatch.setattr("scripts.apply_pip_fixture_registration.ssl.get_default_verify_paths", lambda: type("Paths", (), {"cafile": str(ca_file)})())
    connector = FakeConnector()

    apply_registration(SQL, connector, environment())

    assert connector.connection.started is True
    assert connector.connection.committed is True
    assert connector.connection.rolled_back is False
    assert connector.connection.closed is True
    assert connector.config["ssl_verify_cert"] is True
    assert connector.config["ssl_verify_identity"] is True
    assert connector.config["ssl_disabled"] is False
