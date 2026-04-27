CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS competitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    country TEXT,
    scope_status TEXT NOT NULL DEFAULT 'approved_mvp',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    provider_type TEXT NOT NULL,
    base_url TEXT,
    status TEXT NOT NULL DEFAULT 'candidate',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS provider_competition_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    provider_competition_key TEXT NOT NULL,
    supports_fixtures BOOLEAN NOT NULL DEFAULT FALSE,
    supports_results BOOLEAN NOT NULL DEFAULT FALSE,
    supports_current_odds BOOLEAN NOT NULL DEFAULT FALSE,
    supports_historical_odds BOOLEAN NOT NULL DEFAULT FALSE,
    supports_xg BOOLEAN NOT NULL DEFAULT FALSE,
    supports_lineups BOOLEAN NOT NULL DEFAULT FALSE,
    supports_injuries BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider_id, competition_id)
);

CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID REFERENCES competitions(id),
    name TEXT NOT NULL,
    country TEXT,
    provider_keys JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fixtures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id),
    provider_fixture_key TEXT,
    kickoff_at TIMESTAMPTZ NOT NULL,
    home_team_id UUID REFERENCES teams(id),
    away_team_id UUID REFERENCES teams(id),
    status TEXT NOT NULL DEFAULT 'scheduled',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fixture_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fixture_id UUID UNIQUE NOT NULL REFERENCES fixtures(id) ON DELETE CASCADE,
    home_goals INTEGER,
    away_goals INTEGER,
    result_status TEXT NOT NULL DEFAULT 'pending',
    provider_code TEXT,
    provider_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS odds_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fixture_id UUID NOT NULL REFERENCES fixtures(id) ON DELETE CASCADE,
    provider_code TEXT NOT NULL,
    bookmaker TEXT NOT NULL,
    market_code TEXT NOT NULL,
    selection_code TEXT NOT NULL,
    decimal_odds NUMERIC(10,4) NOT NULL,
    raw_implied_probability NUMERIC(10,6),
    no_vig_probability NUMERIC(10,6),
    observed_at TIMESTAMPTZ NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    provider_payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS historical_odds_imports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_code TEXT NOT NULL,
    competition_code TEXT NOT NULL,
    season TEXT,
    market_code TEXT NOT NULL,
    source_uri TEXT,
    imported_rows INTEGER NOT NULL DEFAULT 0,
    import_status TEXT NOT NULL DEFAULT 'pending',
    provider_timestamp TIMESTAMPTZ,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS xg_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fixture_id UUID REFERENCES fixtures(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    provider_code TEXT NOT NULL,
    xg_for NUMERIC(10,4),
    xg_against NUMERIC(10,4),
    observed_at TIMESTAMPTZ,
    provider_timestamp TIMESTAMPTZ,
    provider_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lineups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fixture_id UUID NOT NULL REFERENCES fixtures(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    provider_code TEXT NOT NULL,
    confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    lineup_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    provider_timestamp TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS injuries_suspensions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fixture_id UUID REFERENCES fixtures(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    player_name TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    expected_return TEXT,
    provider_code TEXT NOT NULL,
    provider_timestamp TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS provider_health_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_code TEXT NOT NULL,
    endpoint TEXT,
    status TEXT NOT NULL,
    response_time_ms INTEGER,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS data_quality_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fixture_id UUID REFERENCES fixtures(id) ON DELETE CASCADE,
    overall_status TEXT NOT NULL,
    score NUMERIC(5,2) NOT NULL DEFAULT 0,
    has_current_odds BOOLEAN NOT NULL DEFAULT FALSE,
    has_historical_odds BOOLEAN NOT NULL DEFAULT FALSE,
    has_xg BOOLEAN NOT NULL DEFAULT FALSE,
    has_lineups BOOLEAN NOT NULL DEFAULT FALSE,
    has_injuries BOOLEAN NOT NULL DEFAULT FALSE,
    has_provider_timestamps BOOLEAN NOT NULL DEFAULT FALSE,
    has_provider_audit_trail BOOLEAN NOT NULL DEFAULT FALSE,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id TEXT,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    actor TEXT NOT NULL DEFAULT 'system',
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fixtures_competition_kickoff ON fixtures(competition_id, kickoff_at);
CREATE INDEX IF NOT EXISTS idx_odds_fixture_market ON odds_snapshots(fixture_id, market_code, observed_at);
CREATE INDEX IF NOT EXISTS idx_xg_fixture ON xg_observations(fixture_id);
CREATE INDEX IF NOT EXISTS idx_data_quality_fixture ON data_quality_scores(fixture_id, checked_at);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id, created_at);
