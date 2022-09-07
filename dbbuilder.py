import sqlalchemy as sql

sql.create_engine('sqlite:///spacedrepetition.sqlite')
query='CREATE TABLE Cards (front VARCHAR(1000), back VARCHAR(1000), added DATE, review DATE, new BIT,easiness FLOAT,\
        interval INT, repetitions INT);'
sql.create_engine('sqlite:///spacedrepetition.sqlite').execute(query)