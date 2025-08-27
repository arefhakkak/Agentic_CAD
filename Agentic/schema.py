import logging
import sqlite3

from .connection import get_agentic_connection

logger = logging.getLogger("SCHEMA")


def init_db(drop_and_recreate: bool = True):
    with get_agentic_connection() as conn:
        cur = conn.cursor()

        tables = [
            "FunctionParametersInstance",
            "FunctionOutputInstance",
            "FunctionInstance",
            "StrategyInstance",
            "StrategyLibrary",
            "FunctionParametersLibrary",
            "FunctionOutputLibrary",
            "FunctionTemplateLibrary",
            "GoalInstance",
        ]

        if drop_and_recreate:
            cur.execute("PRAGMA foreign_keys = OFF")
            for t in tables:
                cur.execute(f"DROP TABLE IF EXISTS {t}")
            cur.execute("PRAGMA foreign_keys = ON")

        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS GoalInstance(
                GoalID          INTEGER PRIMARY KEY AUTOINCREMENT,
                SessionID       INTEGER,
                GoalName        TEXT,
                GoalTarget      TEXT,
                GoalValidation  TEXT,
                GoalDescription TEXT,
                GoalSuccess     BOOLEAN
            );

            CREATE TABLE IF NOT EXISTS FunctionTemplateLibrary(
                FunctionTemplateID INTEGER PRIMARY KEY AUTOINCREMENT,
                FunctionName        TEXT,
                StrategyType        TEXT,
                FunctionDescription TEXT
            );

            CREATE TABLE IF NOT EXISTS FunctionOutputLibrary(
                FunctionOutputID INTEGER PRIMARY KEY AUTOINCREMENT,
                FunctionTemplateID INTEGER,
                OutputName TEXT, OutputValue TEXT, Type TEXT,
                FOREIGN KEY(FunctionTemplateID) REFERENCES FunctionTemplateLibrary(FunctionTemplateID)
            );

            CREATE TABLE IF NOT EXISTS FunctionParametersLibrary(
                FunctionParameterID INTEGER PRIMARY KEY AUTOINCREMENT,
                FunctionTemplateID INTEGER,
                ParameterName TEXT, ParameterValue TEXT, Type TEXT,
                FOREIGN KEY(FunctionTemplateID) REFERENCES FunctionTemplateLibrary(FunctionTemplateID)
            );


            CREATE TABLE IF NOT EXISTS StrategyInstance(
                StrategyID          INTEGER PRIMARY KEY AUTOINCREMENT,
                GoalID              INTEGER,
                StrategyName        TEXT,
                StrategyTarget      TEXT,
                StrategyDescription TEXT,
                StrategySuccess     BOOLEAN,
                StrategyValidation  TEXT,
                FOREIGN KEY(GoalID) REFERENCES GoalInstance(GoalID)
            );

            CREATE TABLE IF NOT EXISTS StrategyLibrary(
                StrategyID          INTEGER PRIMARY KEY AUTOINCREMENT,
                StrategyName        TEXT,
                StrategyTarget      TEXT,
                StrategyDescription TEXT,
                PlanSteps TEXT
            );


            CREATE TABLE IF NOT EXISTS FunctionInstance(
                FunctionID      INTEGER PRIMARY KEY AUTOINCREMENT,
                StrategyID      INTEGER,
                FunctionName    TEXT,
                FunctionSuccess BOOLEAN,
                failedtext      TEXT,
                FOREIGN KEY(StrategyID) REFERENCES StrategyInstance(StrategyID)
            );

            CREATE TABLE IF NOT EXISTS FunctionOutputInstance(
                FunctionOutputID INTEGER PRIMARY KEY AUTOINCREMENT,
                FunctionID INTEGER,
                OutputName TEXT, OutputValue TEXT, Type TEXT,
                FOREIGN KEY(FunctionID) REFERENCES FunctionInstance(FunctionID)
            );

            CREATE TABLE IF NOT EXISTS FunctionParametersInstance(
                FunctionParameterID INTEGER PRIMARY KEY AUTOINCREMENT,
                FunctionID INTEGER,
                ParameterName TEXT, ParameterValue TEXT, Type TEXT,
                FOREIGN KEY(FunctionID) REFERENCES FunctionInstance(FunctionID)
            );
            """
        )
        conn.commit()
        # logger.info(f"✅ agentic.db initialized with tables: len{tables}")
        logger.info(f"✅ agentic.db initialized with {len(tables)} tables.")


if __name__ == "__main__":
    init_db(drop_and_recreate=True)
