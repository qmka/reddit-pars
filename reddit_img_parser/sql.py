import sqlite3
from reddit_img_parser.graph import load_graph
from reddit_img_parser.settings import DATABASE


ERROR_0 = "Done."
ERROR_1 = "Entry doesn't exists in the database."
ERROR_2 = "Entry already exists in the database."
ERROR_3 = "Entry already has this status."
ERROR_4 = "One or both of the entries do not exist in the database."
ERROR_5 = "Connection already exists."
ERROR_6 = "Connection doesn't exists."


def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''CREATE TABLE redditors
                (name TEXT PRIMARY KEY NOT NULL,
                status TEXT NOT NULL)''')
    conn.execute('''CREATE TABLE subreddits
                (name TEXT PRIMARY KEY NOT NULL,
                status TEXT NOT NULL)''')
    conn.execute('''CREATE TABLE connections
                (redditor_name TEXT NOT NULL,
                subreddit_name TEXT NOT NULL,
                PRIMARY KEY (redditor_name, subreddit_name),
                FOREIGN KEY (redditor_name) REFERENCES redditors(name),
                FOREIGN KEY (subreddit_name) REFERENCES subreddits(name))''')
    conn.commit()
    conn.close()


def fill_tables():
    G = load_graph()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for node in G.nodes(data=True):
        name = node[0]
        attr = node[1]['attribute']
        bip = node[1]['bipartite']
        if bip == 0:
            cursor.execute("INSERT INTO redditors (name, status) \
                            VALUES (?, ?)",
                           (name, attr))
        elif bip == 1:
            cursor.execute("INSERT INTO subreddits (name, status) \
                            VALUES (?, ?)",
                           (name, attr))

    for edge in G.edges(data=True):
        source, target, void = edge
        conn.execute("INSERT INTO connections (redditor_name, subreddit_name) \
                      VALUES (?, ?)",
                     (source, target))

    conn.commit()
    conn.close()

################
# ТИПОВЫЕ ЗАДАЧИ
################


def add_node(entry_type, name, status):
    table = f"{entry_type}s"
    operation_status = False
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table} WHERE name=?", (name,))
    existing_node = cursor.fetchone()
    if existing_node is None:
        cursor.execute(f"INSERT INTO {table} (name, status) VALUES (?, ?)",
                       (name, status))
        conn.commit()
        operation_status = True
    conn.close()
    return operation_status


def remove_node(entry_type, name):
    table = f"{entry_type}s"
    operation_status = False
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(f"SELECT name FROM {table} WHERE name=?", (name,))
    existing_node = cursor.fetchone()
    if existing_node is not None:
        cursor.execute(f"DELETE FROM {table} WHERE name=?", (name,))
        conn.commit()
        operation_status = True
    conn.close
    return operation_status


def get_nodes(entry_type, status=None):
    table = f"{entry_type}s"
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if status:
        query = f"SELECT name FROM {table} WHERE status = '{status}'"
    else:
        query = f"SELECT name FROM {table}"

    cursor.execute(query)
    result = [row[0] for row in cursor.fetchall()]
    conn.close()
    return result


def set_status(entry_type, name, status):
    table = f"{entry_type}s"
    operation_status = False
    error_code = ERROR_1

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(f"SELECT name, status FROM {table}")
    rows = cursor.fetchall()

    for row in rows:
        if row[0] == name:
            if row[1] != status:
                cursor.execute(f"UPDATE {table} \
                                 SET status = ? \
                                 WHERE name = ?",
                               (status, name))
                conn.commit()
                operation_status = True
                error_code = ERROR_0
            else:
                error_code = ERROR_3

    conn.close()
    return operation_status, error_code


def get_status(entry_type, name):
    table = f"{entry_type}s"
    status = None

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(f"SELECT name FROM {table}")
    names = [row[0] for row in cursor.fetchall()]

    if name in names:
        cursor.execute(f"SELECT status FROM {table} WHERE name=?", (name,))
        status = cursor.fetchone()[0]

    conn.close()
    return status


def connect_nodes(name1, name2):
    operation_status = False
    error_code = ERROR_4

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM redditors")
    redditor_names = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT name FROM subreddits")
    subreddit_names = [row[0] for row in cursor.fetchall()]

    if name1 in redditor_names and name2 in subreddit_names:
        redditor_name = name1
        subreddit_name = name2
    elif name1 in subreddit_names and name2 in redditor_names:
        redditor_name = name2
        subreddit_name = name1
    else:
        conn.close()
        return operation_status, error_code

    cursor.execute("SELECT redditor_name, subreddit_name \
                    FROM connections \
                    WHERE redditor_name=? \
                    AND subreddit_name=?",
                   (redditor_name, subreddit_name))
    existing_subscription = cursor.fetchone()

    if existing_subscription is None:
        cursor.execute("INSERT INTO connections \
                        (redditor_name, subreddit_name) \
                        VALUES (?, ?)",
                       (redditor_name, subreddit_name))
        conn.commit()
        operation_status = True
        error_code = ERROR_0
    else:
        error_code = ERROR_5

    conn.close()
    return operation_status, error_code


def disconnect_nodes(name1, name2):
    operation_status = False
    error_code = ERROR_4

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM redditors")
    redditor_names = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT name FROM subreddits")
    subreddit_names = [row[0] for row in cursor.fetchall()]

    if name1 in redditor_names and name2 in subreddit_names:
        redditor_name = name1
        subreddit_name = name2
    elif name1 in subreddit_names and name2 in redditor_names:
        redditor_name = name2
        subreddit_name = name1
    else:
        conn.close()
        return operation_status, error_code

    cursor.execute("SELECT redditor_name, subreddit_name \
                    FROM connections \
                    WHERE redditor_name=? \
                    AND subreddit_name=?",
                   (redditor_name, subreddit_name))
    existing_subscription = cursor.fetchone()

    if existing_subscription is not None:
        cursor.execute("DELETE FROM connections \
                        WHERE (redditor_name=? AND subreddit_name=?) \
                        OR (redditor_name=? AND subreddit_name=?)",
                       (name1, name2, name2, name1))
        conn.commit()
        operation_status = True
        error_code = ERROR_0
    else:
        error_code = ERROR_6

    conn.close()
    return operation_status, error_code
