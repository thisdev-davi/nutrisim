from app.db.base import url_do_banco


def test_url_do_neon_usa_psycopg3(monkeypatch):
    """a string do neon (postgresql://) passa a usar o driver instalado."""
    neon = "postgresql://u:s3nha@ep-x.neon.tech/nutrisim?sslmode=require"
    monkeypatch.setenv("DATABASE_URL", neon)
    esperado = "postgresql+psycopg://u:s3nha@ep-x.neon.tech/nutrisim?sslmode=require"
    assert url_do_banco() == esperado
