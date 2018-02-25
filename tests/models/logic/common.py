def clean_create_tables(table_list):
    for table in table_list:
        if table.exists():
            table.delete_table()
        table.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
