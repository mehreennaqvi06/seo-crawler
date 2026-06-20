import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_8RzaNsB0yfQV@ep-jolly-fire-ao609kn4-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def create_job_db(url, status):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO jobs (url, status)
        VALUES (%s, %s)
        RETURNING id
        """,
        (url, status)
    )

    job_id = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    return job_id

def update_job_db(
    job_id,
    status,
    pages_crawled,
    crawl_duration,
    error_count,
    retry_count
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE jobs
        SET status = %s,
            pages_crawled = %s,
            crawl_duration_seconds = %s,
            error_count = %s,
            retry_count = %s,
            completed_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (
            status,
            pages_crawled,
            crawl_duration,
            error_count,
            retry_count,
            job_id
        )
    )

    conn.commit()

    cur.close()
    conn.close()
    
def save_page_db(
    job_id,
    url,
    title,
    h1,
    meta_description,
    status_code
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO pages
        (job_id, url, title, h1, meta_description, status_code)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            job_id,
            url,
            title,
            h1,
            meta_description,
            status_code
        )
    )

    conn.commit()

    cur.close()
    conn.close()   
    
def get_metrics_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*) AS total_jobs,
            COUNT(*) FILTER (WHERE status = 'completed') AS completed_jobs,
            COUNT(*) FILTER (WHERE status = 'queued') AS queued_jobs,
            COALESCE(SUM(pages_crawled), 0) AS total_pages_crawled,
            COALESCE(SUM(error_count), 0) AS total_errors,
            COALESCE(SUM(retry_count), 0) AS total_retries,
            COALESCE(AVG(crawl_duration_seconds), 0) AS average_crawl_duration
        FROM jobs
    """)

    row = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "total_jobs": row[0],
        "completed_jobs": row[1],
        "queued_jobs": row[2],
        "total_pages_crawled": row[3],
        "total_errors": row[4],
        "total_retries": row[5],
        "average_crawl_duration": float(row[6])
    }
    
def get_all_jobs_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            url,
            status,
            pages_crawled,
            crawl_duration_seconds,
            error_count,
            completed_at
        FROM jobs
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "url": row[1],
            "status": row[2],
            "pages_crawled": row[3],
            "crawl_duration_seconds": row[4],
            "error_count": row[5],
            "completed_at": row[6]
        }
        for row in rows
    ]

def get_job_history_db(job_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            url,
            status,
            pages_crawled,
            crawl_duration_seconds,
            error_count,
            completed_at
        FROM jobs
        WHERE id = %s
        """,
        (job_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "url": row[1],
        "status": row[2],
        "pages_crawled": row[3],
        "crawl_duration_seconds": row[4],
        "error_count": row[5],
        "completed_at": row[6]
    }
    
if __name__ == "__main__":
    conn = get_connection()
    print("Database connected successfully!")
    conn.close()