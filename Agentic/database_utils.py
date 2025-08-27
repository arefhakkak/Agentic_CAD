"""
Database utility functions for the Agentic system.
"""

import sqlite3
from typing import Dict


def get_agentic_database_info() -> Dict[str, int]:
    """Get information about all tables in the agentic database."""
    try:
        with sqlite3.connect("agentic.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            info = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                info[table] = count
            
            return info
    except Exception as e:
        print(f"❌ Error getting agentic database info: {e}")
        return {}


def check_agentic_data_exists() -> bool:
    """Check if agentic database already has complete data."""
    try:
        with sqlite3.connect("agentic.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM StrategyLibrary")
            strategy_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM FunctionTemplateLibrary")
            function_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM FunctionOutputLibrary")
            output_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM FunctionParametersLibrary")
            param_count = cursor.fetchone()[0]
            
            # Check if we have comprehensive data
            has_complete_data = (strategy_count >= 6 and function_count >= 9 and 
                               output_count >= 9 and param_count >= 9)
            
            if has_complete_data:
                print(f"✅ Agentic database already has complete data!")
                print(f"   📋 StrategyLibrary: {strategy_count} strategies")
                print(f"   📋 FunctionTemplateLibrary: {function_count} functions")
                print(f"   📋 FunctionOutputLibrary: {output_count} outputs")
                print(f"   📋 FunctionParametersLibrary: {param_count} parameters")
                return True
            else:
                print(f"⚠️ Agentic database has incomplete data:")
                print(f"   📋 StrategyLibrary: {strategy_count} strategies")
                print(f"   📋 FunctionTemplateLibrary: {function_count} functions")
                print(f"   📋 FunctionOutputLibrary: {output_count} outputs")
                print(f"   📋 FunctionParametersLibrary: {param_count} parameters")
                print("🔧 Will repopulate with complete data...")
                return False
                
    except Exception as e:
        print(f"⚠️ Could not check existing agentic data: {e}")
        print("🔧 Will create and populate agentic database...")
        return False
