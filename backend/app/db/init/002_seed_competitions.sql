INSERT INTO competitions (code, name, country, scope_status) VALUES
('EPL', 'Premier League', 'England', 'approved_mvp'),
('LALIGA', 'La Liga', 'Spain', 'approved_mvp'),
('BUNDESLIGA', 'Bundesliga', 'Germany', 'approved_mvp'),
('SERIE_A', 'Serie A', 'Italy', 'approved_mvp'),
('LIGUE_1', 'Ligue 1', 'France', 'approved_mvp'),
('UCL', 'UEFA Champions League', 'Europe', 'approved_mvp'),
('UEL', 'UEFA Europa League', 'Europe', 'approved_mvp'),
('NOR_ELITESERIEN', 'Eliteserien', 'Norway', 'approved_mvp')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    country = EXCLUDED.country,
    scope_status = EXCLUDED.scope_status;

INSERT INTO providers (code, name, provider_type, base_url, status) VALUES
('api_football', 'API-FOOTBALL', 'fixtures_lineups_injuries_candidate', 'https://v3.football.api-sports.io', 'candidate'),
('odds_api', 'The Odds API', 'odds_candidate', 'https://api.the-odds-api.com', 'candidate'),
('sportmonks', 'Sportmonks Football API', 'combined_candidate', 'https://api.sportmonks.com/v3/football', 'candidate'),
('statsbomb', 'StatsBomb', 'xg_candidate', NULL, 'candidate')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    provider_type = EXCLUDED.provider_type,
    base_url = EXCLUDED.base_url,
    status = EXCLUDED.status;

INSERT INTO audit_logs (entity_type, entity_id, action, status, actor, details) VALUES
('phase_2_seed', 'mvp_competitions', 'seed_approved_competitions', 'completed', 'system',
 '{"competitions":["EPL","LALIGA","BUNDESLIGA","SERIE_A","LIGUE_1","UCL","UEL","NOR_ELITESERIEN"],"norwegian_league_name":"Eliteserien only","historical_odds":"mandatory","xg":"mandatory","auto_betting":"inactive_hard_locked"}'::jsonb);
