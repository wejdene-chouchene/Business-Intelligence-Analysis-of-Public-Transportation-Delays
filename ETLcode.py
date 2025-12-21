import pandas as pd
import numpy as np

df = pd.read_csv('public_transport_complete_10000_rows.csv')

columns_needed = [
    'trip_id', 'date', 'time', 'transport_type', 'route_id',
    'origin_station', 'destination_station',
    'scheduled_departure', 'scheduled_arrival',
    'actual_departure_delay_min', 'actual_arrival_delay_min',
    'passenger_count', 'capacity_percentage',
    'trip_status', 'delayed', 'peak_hour', 'weekday'
]

df = df[columns_needed]

df['passenger_count'] = df['passenger_count'].fillna(df['passenger_count'].median())

df['date'] = pd.to_datetime(df['date'])
df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.time
df['scheduled_departure'] = pd.to_datetime(df['scheduled_departure'], format='%H:%M:%S', errors='coerce').dt.time
df['scheduled_arrival'] = pd.to_datetime(df['scheduled_arrival'], format='%H:%M:%S', errors='coerce').dt.time

delay_cols = ['actual_departure_delay_min', 'actual_arrival_delay_min']
for col in delay_cols:
    df[col] = np.where(df[col] > 60, 60, df[col])
    df[col] = np.where(df[col] < -10, -10, df[col])

df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
df['hour'] = df['datetime'].dt.hour
df['day_name'] = df['datetime'].dt.day_name()
df['on_time'] = (df['actual_arrival_delay_min'] <= 0).astype(int)
df['delayed_5min'] = (df['actual_arrival_delay_min'] > 5).astype(int)

def get_duration(row):
    try:
        dep = pd.Timestamp.combine(pd.Timestamp('2023-01-01'), row['scheduled_departure'])
        arr = pd.Timestamp.combine(pd.Timestamp('2023-01-01'), row['scheduled_arrival'])
        if arr < dep:
            arr += pd.Timedelta(days=1)
        return (arr - dep).seconds / 60
    except:
        return np.nan

df['trip_duration_min'] = df.apply(get_duration, axis=1)

df = df[df['passenger_count'] >= 0]
df = df[df['capacity_percentage'].between(0, 200)]
df = df[df['trip_duration_min'] > 0]

df.to_csv('public_transport_cleaned1.csv', index=False)