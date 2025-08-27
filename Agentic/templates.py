import logging
import sqlite3

# Remove problematic imports and use direct database connections
logger = logging.getLogger("TEMPLATE")

# 8 Core Merged Actions - replacing old function templates
templates = [
    # (FunctionName, StrategyType, FunctionDescription)
    (
        "SEARCH",
        "search",
        "Query different knowledge tables based on strategy type. Searches CatiaDocFunctionsLibrary for declarative KC, ConditionalKnowledge for conditional strategies, ProceduralKnowledge for procedural strategies, and DeclarativeKnowledge for declarative KG."
    ),
    (
        "ANALYZE", 
        "analyze",
        "Process data with different analytical approaches. Performs text analysis for declarative facts, geometric analysis for constraint relationships, parameter analysis for procedural values, pattern analysis for knowledge generation, and usage/frequency analysis for optimization."
    ),
    (
        "EXTRACT",
        "extract", 
        "Pull out specific information elements from various sources. Extracts product numbers and key identifiers, parameter values and constraints, sequence patterns and workflow elements, and implicit knowledge from high-confidence data."
    ),
    (
        "CLASSIFY",
        "filter",
        "Categorize information by different criteria based on strategy needs. Classifies constraints by type (geometric, dimensional), workflows by grouping, functions by enhancement level, and procedures by optimization type."
    ),
    (
        "MAP",
        "modification",
        "Create relationships and connections between different elements. Maps step actions to CATIA functions, constraints between objects, cross-references with documentation, and establishes procedural dependencies."
    ),
    (
        "GENERATE",
        "generation",
        "Create new knowledge variations and combinations. Generates object type variations, constraint context variations, adaptive procedures, logic combinations (AND/OR), and workflow synthesis from existing knowledge."
    ),
    (
        "VALIDATE",
        "validation",
        "Assess quality and completeness of processed knowledge. Performs confidence assessment for reliability, parameter validation for completeness, cross-validation with documentation, and meta-analysis for procedure management."
    ),
    (
        "POPULATE",
        "storage",
        "Store processed knowledge in appropriate knowledge tables. Populates declarative knowledge with factual information, conditional knowledge with constraint rules, procedural knowledge with execution procedures, and generates new knowledge entries."
    ),
]

# Enhanced output definitions for each core action
outputs = {
    "SEARCH": [
        ("Search Results", "", "json"), 
        ("Source Table", "", "string"),
        ("Record Count", "", "integer"),
        ("Query Execution Time", "", "float")
    ],
    "ANALYZE": [
        ("Analysis Results", "", "json"), 
        ("Analysis Type", "", "string"),
        ("Confidence Score", "", "float"),
        ("Pattern Matches", "", "json")
    ],
    "EXTRACT": [
        ("Extracted Data", "", "json"), 
        ("Extraction Method", "", "string"),
        ("Success Rate", "", "float"),
        ("Failed Extractions", "", "json")
    ],
    "CLASSIFY": [
        ("Classification Results", "", "json"), 
        ("Category Type", "", "string"),
        ("Classification Accuracy", "", "float"),
        ("Category Counts", "", "json")
    ],
    "MAP": [
        ("Mapping Results", "", "json"), 
        ("Relationship Type", "", "string"),
        ("Mapping Completeness", "", "float"),
        ("Unmapped Elements", "", "json")
    ],
    "GENERATE": [
        ("Generated Knowledge", "", "json"), 
        ("Generation Method", "", "string"),
        ("Generation Count", "", "integer"),
        ("Quality Score", "", "float")
    ],
    "VALIDATE": [
        ("Validation Results", "", "json"), 
        ("Confidence Score", "", "float"),
        ("Validation Errors", "", "json"),
        ("Validation Status", "", "string")
    ],
    "POPULATE": [
        ("Population Status", "", "string"), 
        ("Records Created", "", "integer"),
        ("Population Errors", "", "json"),
        ("Target Knowledge Type", "", "string")
    ],
}

# Enhanced parameter definitions for each core action
params = {
    "SEARCH": [
        ("Target Table", "", "string"), 
        ("Search Criteria", "", "string"),
        ("Strategy Context", "", "string"),
        ("Search Filters", "", "json")
    ],
    "ANALYZE": [
        ("Data Input", "", "json"), 
        ("Analysis Type", "", "string"),
        ("Strategy Phase", "", "string"),
        ("Analysis Parameters", "", "json")
    ],
    "EXTRACT": [
        ("Source Data", "", "string"), 
        ("Extraction Pattern", "", "string"),
        ("Target Elements", "", "json"),
        ("Extraction Rules", "", "json")
    ],
    "CLASSIFY": [
        ("Input Data", "", "json"), 
        ("Classification Criteria", "", "string"),
        ("Category Schema", "", "json"),
        ("Classification Threshold", "", "float")
    ],
    "MAP": [
        ("Source Elements", "", "json"), 
        ("Target Elements", "", "json"),
        ("Mapping Rules", "", "json"),
        ("Relationship Type", "", "string")
    ],
    "GENERATE": [
        ("Base Knowledge", "", "json"), 
        ("Generation Rules", "", "string"),
        ("Strategy Type", "", "string"),
        ("Generation Parameters", "", "json")
    ],
    "VALIDATE": [
        ("Input Data", "", "json"), 
        ("Validation Criteria", "", "string"),
        ("Quality Thresholds", "", "json"),
        ("Validation Rules", "", "json")
    ],
    "POPULATE": [
        ("Knowledge Data", "", "json"), 
        ("Target Table", "", "string"),
        ("Population Mode", "", "string"),
        ("Data Validation", "", "boolean")
    ],
}

# Keep existing strategies unchanged
strategies = [
    # (StrategyName, StrategyTarget, StrategyDescription)
    (
        "Declarative KC",
        "knowledge_construction",
        "Strategy for constructing declarative knowledge from extracted data and user queries. Focuses on building factual knowledge representations about CATIA objects, their types, subtypes, and parameters. Extracts object creation facts, properties, and specifications from the steps data and CATIA documentation."
    ),
    (
        "Declarative KG",
        "knowledge_generation",
        "Strategy for generating declarative knowledge from existing knowledge base. Focuses on creating new factual knowledge from stored information. Combines existing declarative facts with CATIA documentation to generate new object specifications, properties, and relationships."
    ),
    (
        "Conditional KC", 
        "knowledge_construction",
        "Strategy for constructing conditional knowledge from extracted data and user queries. Focuses on building if-then relationships and constraints. Identifies tangency conditions, parameter modifications, and geometric constraints from the steps data and maps them to conditional logic."
    ),
    (
        "Conditional KG",
        "knowledge_generation",
        "Strategy for generating conditional knowledge from existing knowledge base. Focuses on creating new if-then relationships and conditional logic. Synthesizes existing constraints with CATIA function parameters to generate new conditional rules and constraint patterns."
    ),
    (
        "Procedural KC",
        "knowledge_construction", 
        "Strategy for constructing procedural knowledge from extracted data and user queries. Focuses on building step-by-step procedures and workflows. Extracts procedural sequences, tool selections, and workflow patterns from the steps data to create executable procedures."
    ),
    (
        "Procedural KG", 
        "knowledge_generation",
        "Strategy for generating procedural knowledge from existing knowledge base. Focuses on creating new step-by-step procedures and workflows. Combines existing procedural knowledge with CATIA function outputs to generate new workflow sequences and procedural patterns."
    ),
]

# Goal templates for different types of user requests
goals = [
    # (GoalName, GoalTarget, GoalDescription, GoalValidation)
    (
        "create_wing",
        "wing_creation",
        "Create a complete wing structure using CATIA functions and knowledge from the database. This involves creating the main wing body, adding necessary features, and ensuring proper geometry.",
        "Wing structure is successfully created with all required components and features"
    ),
]

# ────────────────────────────────────────────────────────────────────────────────────────
# Populate the template libraries in the database with 8 core actions

def populate_template_libraries():
    """Populate the template libraries with 8 core merged actions."""
    # Use direct database connection
    conn = sqlite3.connect("agentic.db")
    cur = conn.cursor()

    # Clear existing data and reset auto-increment counters
    cur.executescript(
        """
        DELETE FROM FunctionTemplateLibrary;
        DELETE FROM FunctionOutputLibrary;
        DELETE FROM FunctionParametersLibrary;
        DELETE FROM StrategyLibrary;
        DELETE FROM GoalInstance;
        
        -- Reset auto-increment counters to start from 1
        DELETE FROM sqlite_sequence WHERE name='FunctionTemplateLibrary';
        DELETE FROM sqlite_sequence WHERE name='FunctionOutputLibrary';
        DELETE FROM sqlite_sequence WHERE name='FunctionParametersLibrary';
        DELETE FROM sqlite_sequence WHERE name='StrategyLibrary';
        DELETE FROM sqlite_sequence WHERE name='GoalInstance';
        """
    )

    # Insert goals first
    for gname, gtarget, gdesc, gvalidation in goals:
        cur.execute(
            """INSERT INTO GoalInstance
                (GoalName, GoalTarget, GoalDescription, GoalValidation)
                VALUES (?, ?, ?, ?)
            """,
            (gname, gtarget, gdesc, gvalidation),
        )

    # Insert strategies (keep existing 6 strategies)
    for sname, starg, sdesc in strategies:
        cur.execute(
            """INSERT INTO StrategyLibrary
                (StrategyName,StrategyTarget,StrategyDescription)
                VALUES (?,?,?)""",
            (sname, starg, sdesc),
        )

    # Insert the 8 core action templates
    for fname, stype, fdesc in templates:
        cur.execute(
            """INSERT INTO FunctionTemplateLibrary
                    (FunctionName,StrategyType,FunctionDescription)
                    VALUES (?,?,?)""",
            (fname, stype, fdesc),
        )
        fid = cur.lastrowid

        # Insert outputs for this function
        for oname, oval, otype in outputs.get(fname, []):
            cur.execute(
                """INSERT INTO FunctionOutputLibrary
                        (FunctionTemplateID,OutputName,OutputValue,Type)
                        VALUES (?,?,?,?)""",
                (fid, oname, oval, otype),
            )

        # Insert parameters for this function
        for pname, pval, ptype in params.get(fname, []):
            cur.execute(
                """INSERT INTO FunctionParametersLibrary
                        (FunctionTemplateID,ParameterName,ParameterValue,Type)
                        VALUES (?,?,?,?)""",
                (fid, pname, pval, ptype),
            )

    conn.commit()
    logger.info(f"✅ Template-library tables populated with 8 core actions in agentic.db")
    logger.info(f"   📋 Functions: {len(templates)} core actions")
    logger.info(f"   📋 Strategies: {len(strategies)} strategies")
    logger.info(f"   📋 Goals: {len(goals)} goals")
    conn.close()

if __name__ == "__main__":
    populate_template_libraries()