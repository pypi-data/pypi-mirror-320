from ethosian.docker.app.postgres.postgres import PostgresDb


class PgVectorDb(PostgresDb):
    # -*- App Name
    name: str = "pgvector-db"

    # -*- Image Configuration
    image_name: str = "ethosian/pgvector"
    image_tag: str = "16"
