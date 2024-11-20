from sqlalchemy import create_engine, text

params = "mysql+pymysql://tsw581:test_pass123@127.0.0.1/access_wv_online?charset=utf8mb4"
engine = create_engine(params)


def retrieve_records(sql_string):
    records_list = []

    with engine.connect() as conn:
        result = conn.execute(text(sql_string))

        for row in result.all():
            row_to_dict = row._asdict()
            records_list.append(row_to_dict)

    return records_list
