-- Supabase (PostgreSQL) Schema for White Travels Agent

-- User Travelers Table
CREATE TABLE travelers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    google_calendar_token TEXT, -- For Calendar Integration
    loyalty_status TEXT DEFAULT 'Standard',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Active Bookings (PNR Data)
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES travelers(id),
    pnr_id TEXT UNIQUE NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    status TEXT DEFAULT 'ON_TIME', -- ON_TIME, DELAYED, CANCELLED
    departure_time TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agent Disruption Sessions (History)
CREATE TABLE disruption_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID REFERENCES bookings(id),
    severity TEXT NOT NULL,
    conflict_detected BOOLEAN DEFAULT FALSE,
    weather_impact TEXT,
    alternatives_generated JSONB, -- Storing 3 pathways A, B, C
    chosen_pathway TEXT,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- RLS Policies (Example)
ALTER TABLE travelers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own data" ON travelers FOR SELECT USING (auth.uid() = id);
