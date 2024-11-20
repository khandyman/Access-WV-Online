from sqlalchemy import create_engine, text

params = "mysql+pymysql://tsw581:m1kayr1s@127.0.0.1/access_wv_online?charset=utf8mb4"
engine = create_engine(params)

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM network_elements"))
    print(result.all())
