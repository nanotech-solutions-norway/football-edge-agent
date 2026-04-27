-- Football Edge Agent — Phase 3 Baseline Model and Probability Engine
-- Migration: 003_model_probability_engine.sql
-- Purpose: Persist model versions, model inputs, probability outputs,
-- recommendation outputs, calibration runs, and backtest runs.

CREATE TABLE IF NOT EXISTS model_versions (
    id BIGSERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL UNIQUE,
    phase INTEGER NOT NULL DEFAULT 3,
    methodology TEXT NOT NULL,
    supported_markets TEXT[] NOT NULL,
    supported_recommendations TEXT[] NOT NULL DEFAULT ARRAY['BET','WATCHLIST','NO BET'],
    auto_betting_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    auto_betting_hard_locked BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_inputs (
    id BIGSERIAL PRIMARY KEY,
    fixture_id BIGINT NOT NULL,
    model_version TEXT NOT NULL REFERENCES model_versions(model_version),
    market TEXT NOT NULL,
    odds_by_selection JSONB NOT NULL,
    home_expected_goals NUMERIC(10,6) NOT NULL,
    away_expected_goals NUMERIC(10,6) NOT NULL,
    home_elo_rating NUMERIC(10,3),
    away_elo_rating NUMERIC(10,3),
    xg_available BOOLEAN NOT NULL,
    historical_odds_available BOOLEAN NOT NULL,
    provider_audit_trail JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS probability_outputs (
    id BIGSERIAL PRIMARY KEY,
    model_input_id BIGINT REFERENCES model_inputs(id) ON DELETE CASCADE,
    fixture_id BIGINT NOT NULL,
    model_version TEXT NOT NULL REFERENCES model_versions(model_version),
    market TEXT NOT NULL,
    selection TEXT NOT NULL,
    decimal_odds NUMERIC(10,4) NOT NULL,
    model_probability NUMERIC(12,9) NOT NULL CHECK (model_probability >= 0 AND model_probability <= 1),
    bookie_probability NUMERIC(12,9) NOT NULL CHECK (bookie_probability >= 0 AND bookie_probability <= 1),
    market_probability_raw NUMERIC(12,9) NOT NULL,
    market_probability_no_vig NUMERIC(12,9) NOT NULL,
    bookmaker_margin NUMERIC(12,9) NOT NULL,
    edge NUMERIC(12,9) NOT NULL,
    expected_value NUMERIC(12,9) NOT NULL,
    fair_odds NUMERIC(10,4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recommendation_outputs (
    id BIGSERIAL PRIMARY KEY,
    probability_output_id BIGINT REFERENCES probability_outputs(id) ON DELETE SET NULL,
    fixture_id BIGINT NOT NULL,
    model_version TEXT NOT NULL REFERENCES model_versions(model_version),
    market TEXT NOT NULL,
    selection TEXT NOT NULL,
    recommendation TEXT NOT NULL CHECK (recommendation IN ('BET','WATCHLIST','NO BET')),
    confidence TEXT NOT NULL CHECK (confidence IN ('LOW','MEDIUM','HIGH')),
    risk TEXT NOT NULL CHECK (risk IN ('LOW','MEDIUM','HIGH')),
    edge NUMERIC(12,9) NOT NULL,
    expected_value NUMERIC(12,9) NOT NULL,
    model_probability NUMERIC(12,9) NOT NULL,
    bookie_probability NUMERIC(12,9) NOT NULL,
    comparison_chart JSONB NOT NULL,
    audit_trail JSONB NOT NULL,
    hard_fail_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS calibration_runs (
    id BIGSERIAL PRIMARY KEY,
    model_version TEXT NOT NULL REFERENCES model_versions(model_version),
    market TEXT,
    sample_size INTEGER NOT NULL DEFAULT 0,
    brier_score NUMERIC(12,9),
    log_loss NUMERIC(12,9),
    calibration_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS backtest_runs (
    id BIGSERIAL PRIMARY KEY,
    model_version TEXT NOT NULL REFERENCES model_versions(model_version),
    date_from DATE,
    date_to DATE,
    sample_size INTEGER NOT NULL DEFAULT 0,
    roi NUMERIC(12,9),
    yield_value NUMERIC(12,9),
    maximum_drawdown NUMERIC(12,9),
    no_bet_rate NUMERIC(12,9),
    brier_score NUMERIC(12,9),
    log_loss NUMERIC(12,9),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO model_versions (
    model_name,
    model_version,
    methodology,
    supported_markets,
    supported_recommendations,
    auto_betting_enabled,
    auto_betting_hard_locked
)
VALUES (
    'football_edge_baseline_probability_engine',
    '0.3.0-phase3',
    'Market-implied probabilities, no-vig normalization, Elo/Glicko scaffold, Poisson goal model, xG inputs, ensemble blending, calibration metrics, and strict NO BET governance.',
    ARRAY['1X2','OVER_UNDER_2_5','BTTS'],
    ARRAY['BET','WATCHLIST','NO BET'],
    FALSE,
    TRUE
)
ON CONFLICT (model_version) DO NOTHING;
