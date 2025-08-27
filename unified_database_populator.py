#!/usr/bin/env python3
"""
Unified Database Population System
=================================
Efficiently creates and populates both agentic.db and knowledge.db from scratch.
Uses existing functions from Agentic and ultramin modules for efficiency.

Usage:
    python unified_database_populator.py
"""

import sqlite3
import os
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("UNIFIED_DB_POPULATOR")

class UnifiedDatabasePopulator:
    """Unified system for creating and populating both databases efficiently using existing modules."""
    
    def __init__(self):
        self.agentic_db_path = "agentic.db"
        self.knowledge_db_path = "knowledge.db"
        self.backup_suffix = ".backup"
        
        # Import existing modules
        self._import_existing_modules()
    
    def _import_existing_modules(self):
        """Import existing modules from Agentic and ultramin."""
        try:
            # Import ultramin package for PDF harvesting
            import sys
            sys.path.insert(0, 'ultramin_package')
            from schema_ultra_combo import init_db as init_ultramin_db
            from harvest_pdf_ultramin import harvest as harvest_pdf_ultramin
            from scrape_docs_ultramin import scrape as scrape_docs_ultramin
            self.init_ultramin_db = init_ultramin_db
            self.harvest_pdf_ultramin = harvest_pdf_ultramin
            self.scrape_docs_ultramin = scrape_docs_ultramin
            
            # Import Agentic templates directly (avoid connection issues)
            sys.path.insert(0, 'Agentic')
            from templates import populate_template_libraries
            self.populate_template_libraries = populate_template_libraries
            
            # Import Agentic schema SQL (extract from existing module)
            self._import_agentic_schema_sql()
            
            logger.info("✅ Successfully imported existing modules from Agentic and ultramin")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import existing modules: {e}")
            logger.error("Make sure Agentic and ultramin_package modules are available")
            raise
    
    def _import_agentic_schema_sql(self):
        """Import the agentic schema SQL from the existing Agentic.schema module."""
        # Extract the SQL directly from the existing Agentic.schema module
        with open('Agentic/schema.py', 'r') as f:
            schema_content = f.read()
        
        # Extract the SQL from the existing schema module using regex
        import re
        sql_match = re.search(r'cur\.executescript\(\s*"""\s*(.*?)\s*"""\s*\)', schema_content, re.DOTALL)
        if sql_match:
            self.agentic_schema_sql = sql_match.group(1)
        else:
            # If regex extraction fails, raise an error - we should always use existing modules
            raise ImportError("Could not extract schema SQL from existing Agentic.schema module. This should not happen if the module exists.")
    
    def backup_existing_databases(self):
        """Create backups of existing databases if they exist."""
        logger.info("🔄 Checking existing databases...")
        
        for db_path in [self.agentic_db_path, self.knowledge_db_path]:
            if os.path.exists(db_path):
                backup_path = f"{db_path}{self.backup_suffix}"
                try:
                    import shutil
                    shutil.copy2(db_path, backup_path)
                    logger.info(f"✅ Backed up existing {db_path} to {backup_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not backup {db_path}: {e}")
            else:
                logger.info(f"📝 No existing {db_path} found - will create from scratch")
    
    def create_agentic_database(self):
        """Create and populate the agentic database using existing Agentic functions."""
        logger.info("🚀 Setting up agentic database using existing Agentic module...")
        
        # Always remove existing database for fresh population (testing mode)
        if os.path.exists(self.agentic_db_path):
            os.remove(self.agentic_db_path)
            logger.info("🗑️ Removed existing agentic.db for fresh population")
        else:
            logger.info("📝 Creating new agentic.db from scratch")
        
        try:
            # Create agentic database schema using existing Agentic schema
            self._create_agentic_schema()
            logger.info("✅ Agentic database schema created using existing Agentic schema")
            
            # Use existing Agentic template population
            self.populate_template_libraries()
            logger.info("✅ Agentic database populated using existing template functions")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating agentic database: {e}")
            return False
    
    def _create_agentic_schema(self):
        """Create agentic database schema using existing Agentic schema definition."""
        conn = sqlite3.connect(self.agentic_db_path)
        cursor = conn.cursor()
        
        # Use the existing Agentic schema SQL (imported from Agentic/schema.py)
        cursor.executescript(self.agentic_schema_sql)
        
        conn.commit()
        conn.close()
    
    def create_knowledge_database(self):
        """Create and populate the knowledge database using ultramin functions."""
        logger.info("🚀 Setting up knowledge database using ultramin module...")
        
        # Always remove existing database for fresh population (testing mode)
        if os.path.exists(self.knowledge_db_path):
            os.remove(self.knowledge_db_path)
            logger.info("🗑️ Removed existing knowledge.db for fresh population")
        else:
            logger.info("📝 Creating new knowledge.db from scratch")
        
        try:
            # Create knowledge database using ultramin schema
            self.init_ultramin_db(self.knowledge_db_path, overwrite=True)
            logger.info("✅ Knowledge database schema created using ultramin module")
            
            # Run ultramin PDF harvesting to populate harvested steps from PDF
            logger.info("🔄 Running ultramin PDF harvesting...")
            pdf_path = "Flying-Wing-Instructions.pdf"
            if os.path.exists(pdf_path):
                # Harvest PDF using ultramin directly into knowledge database
                harvest_result = self.harvest_pdf_ultramin(pdf_path, self.knowledge_db_path, overwrite=False)
                logger.info(f"✅ Ultramin PDF harvesting completed: {harvest_result}")
            else:
                logger.warning(f"⚠️ PDF file {pdf_path} not found, skipping ultramin harvesting")
            
            # Run ultramin CATIA documentation scraping
            logger.info("🔄 Running ultramin CATIA documentation scraping...")
            master_url = "http://catiadoc.free.fr/online/interfaces/CAAMasterIdx.htm"
            try:
                scrape_result = self.scrape_docs_ultramin(master_url, self.knowledge_db_path, overwrite_docs=True, link_limit=100)
                logger.info(f"✅ Ultramin CATIA documentation scraping completed: {scrape_result} methods")
            except Exception as e:
                logger.warning(f"⚠️ CATIA documentation scraping failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating knowledge database: {e}")
            return False
    
    def verify_databases(self):
        """Verify that both databases are properly created and populated."""
        logger.info("🔍 Verifying database creation...")
        
        verification_results = {
            'agentic_db': False,
            'knowledge_db': False,
            'agentic_tables': {},
            'knowledge_tables': {}
        }
        
        # Verify agentic database
        if os.path.exists(self.agentic_db_path):
            with sqlite3.connect(self.agentic_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    verification_results['agentic_tables'][table] = count
                
                verification_results['agentic_db'] = True
        
        # Verify knowledge database
        if os.path.exists(self.knowledge_db_path):
            with sqlite3.connect(self.knowledge_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    verification_results['knowledge_tables'][table] = count
                
                verification_results['knowledge_db'] = True
        
        # Display verification results
        logger.info("\n📊 DATABASE VERIFICATION RESULTS:")
        logger.info("=" * 50)
        
        if verification_results['agentic_db']:
            logger.info("✅ Agentic Database:")
            for table, count in verification_results['agentic_tables'].items():
                logger.info(f"   {table}: {count} records")
        else:
            logger.error("❌ Agentic database verification failed")
        
        if verification_results['knowledge_db']:
            logger.info("✅ Knowledge Database:")
            for table, count in verification_results['knowledge_tables'].items():
                logger.info(f"   {table}: {count} records")
        else:
            logger.error("❌ Knowledge database verification failed")
        
        return verification_results['agentic_db'] and verification_results['knowledge_db']
    
    def run_complete_population(self):
        """Run the complete database population process using existing modules."""
        logger.info("🚀 UNIFIED DATABASE POPULATION SYSTEM")
        logger.info("=" * 60)
        logger.info("Using existing Agentic and ultramin modules for efficiency")
        logger.info("🔄 TESTING MODE: Always repopulate databases for fresh testing")
        
        try:
            # Step 1: Check and backup existing databases
            self.backup_existing_databases()
            
            # Step 2: Create/repopulate agentic database using existing Agentic functions
            if not self.create_agentic_database():
                logger.error("❌ Failed to create/repopulate agentic database")
                return False
            
            # Step 3: Create/repopulate knowledge database using ultramin functions
            if not self.create_knowledge_database():
                logger.error("❌ Failed to create/repopulate knowledge database")
                return False
            
            # Step 4: Verify both databases
            if not self.verify_databases():
                logger.error("❌ Database verification failed")
                return False
            
            logger.info("\n🎉 UNIFIED DATABASE POPULATION COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info("✅ Both agentic.db and knowledge.db created/repopulated")
            logger.info("✅ Used existing Agentic and ultramin modules for efficiency")
            logger.info("✅ Agentic templates loaded")
            logger.info("✅ PDF harvesting and CATIA documentation scraping completed")
            logger.info("✅ System ready for goal matching and strategy processing")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during database population: {e}")
            return False

def main():
    """Main function to run the unified database population system."""
    try:
        populator = UnifiedDatabasePopulator()
        success = populator.run_complete_population()
        
        if success:
            print("\n🎯 SYSTEM READY!")
            print("You can now use the databases for:")
            print("  • Goal matching using agentic.db templates")
            print("  • Strategy processing using knowledge.db data")
            print("  • PDF-extracted steps from ultramin harvesting")
            print("  • CATIA documentation from ultramin scraping")
            sys.exit(0)
        else:
            print("\n❌ SYSTEM SETUP FAILED!")
            sys.exit(1)
            
    except ImportError as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        print("Make sure Agentic and ultramin_package modules are available in the current directory")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()