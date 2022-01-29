BEGIN;

    CREATE TABLE IF NOT EXISTS exchangerate_api_rates (
        rec_id BIGSERIAL PRIMARY KEY,
        currrency_code TEXT NOT NULL,
        base_currency_code TEXT NOT NULL,
        rate DECIMAL(15,4) NOT NULL,
        time_last_update_unix TIMESTAMP NOT NULL,
        response JSONB,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp,
        UNIQUE (currrency_code, time_last_update_unix)
    );

    CREATE INDEX IF NOT EXISTS idx_exchangerate_api_rates_currrency_code ON exchangerate_api_rates(currrency_code);
    CREATE INDEX IF NOT EXISTS idx_exchangerate_api_rates_time_last_update_unix ON exchangerate_api_rates(time_last_update_unix);


COMMIT;
