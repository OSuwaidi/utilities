from vertica_python import connect, Connection
import polars as pl
from dataframes import optimize_dtypes
from concurrent.futures import ThreadPoolExecutor, TimeoutError


def free_namespace(namespace: dict | None = None) -> None:
    """
    Useful to free up memory from cluttered namespaces when working in Jupyter Notebooks such as cleaning "globals()" and "locals()".
    Parameters
    ----------
    namespace
        namespace dictionary to free up containing history variables (i.e. ones starting with "_") in REPL environments.
    """
    if namespace:
        for k in namespace.copy():
            if k != "_oh" and k.startswith("_") and not k.endswith("__") or k in ("In", "Out", "__", "___"):
                del namespace[k]
        return

    for k in globals().copy():
        if k != "_oh" and k.startswith("_") and not k.endswith("__") or k in ("In", "Out", "__", "___"):
            del globals()[k]


def get_connection_config(path_to_config_file: str = "vertica_config.env") -> dict[str, str | int]:
    with open(path_to_config_file, "r") as f:
        env_text: str = f.read().strip()
        key_value: map = (map(lambda pair: pair.strip().split("="), env_text.split("\n")))
        return {k: v if not v.isdigit() else int(v) for k, v in key_value}


def get_vertica_connection(*, force_new: bool = False, **kwargs) -> Connection | None:
    conn: Connection
    if not force_new and (conn := globals().get("conn")):
        print("Reconnecting...")

        with ThreadPoolExecutor(max_workers=1) as executor:  # context manager will automatically close and cleanup spawned thread(s)
            # Threads in Python are only useful for external tasks (I/O bound operations rather than CPU bound), as processes within Python are single-threaded
            # due to GIL ==> only one thread of execution can run instructions at a time in a Python process.
            future = executor.submit(conn.reset_connection)  # schedule the callable to be executed (in the future)
            try:
                future.result(timeout=120)  # wait for two minutes
            except TimeoutError:
                print(f"Reconnection attempt timed out after 2 minutes.")
                raise
            except Exception as e:
                print(f"Reconnection failed: {e}.")
                raise
            else:  # if no exception occurs
                print("Reconnected successfully!")
                return conn

    print("Connecting...")
    try:
        conn = connect(**kwargs)  # has timeout error built-in
    except TimeoutError:
        print(f"Reconnection attempt timed out after 2 minutes.")
        raise
    except Exception as e:
        print(f"Connection failed: {e}.")
        raise
    else:
        print("Connected successfully!")
        return conn


def fetch_data(query: str, conn: Connection, optimize: bool = True, auto_reconnect: bool = True) -> pl.DataFrame | pl.LazyFrame:
    # TODO: if cursor execution fails, establish reconnection automatically and re-execute the query.
    # Each query session is independent from one another, hence temp tables and session variables get reset every time
    with conn.cursor() as cursor:
        # or we can use: "pl.read_database(query, conn, infer_schema_length=None)"
        df = pl.DataFrame([row for row in cursor.execute(query).iterate()], orient="row", schema=(col.name for col in cursor.description), infer_schema_length=None)
        return optimize_dtypes(df, ignore_types=str) if optimize else df


def close(conn: Connection) -> None:
    # cursor_status = ""
    # if cursor:
    #     assert isinstance(cursor, Cursor), f"Expected {cursor} to be of type {Cursor}, but found {type(cursor).__name__} instead."
    #
    #     if cursor.closed():
    #         print("Cursor already closed.")
    #     else:
    #         cursor.close()
    #         cursor_status: str = f"\nCursor is closed: {cursor.closed()}."
    assert isinstance(conn, Connection), f"Expected {conn} to be of type {Connection}, but found {type(conn).__name__} instead."

    if conn.closed():
        print(f"Connection already closed.")
        return
    else:
        try:
            conn.close()  # idempotent operation (safe to call multiple times)
        except Exception as e:
            print(f"Tried to close connection, but errored: {e}.")
        finally:
            print(f"Connection is closed: {conn.closed()}.")
