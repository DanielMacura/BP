from tokens import *
expressions = [
    (r"[0-9]+", Integer),
    (r"[0-9]\.[0-9]+", Float),
    (r'"(?:\\"|[^"])*"', String),
    (r"[A-Za-z][A-Za-z0-9]*", Symbol),
    (r"\+", Plus),
    (r"-", Minus),
    (r"\\", Divide),
    (r"\*", Multiply),
    (r"#.*$", Comment),
    (r"[\t ]+", Space),
    (r"\r?\n", NewLine),
    (r"\?", Questionmark),
    (r"\=", Equal)
]
