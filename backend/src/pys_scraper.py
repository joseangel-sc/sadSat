"""
Comprehensive scraper for SAT PYS (Productos y Servicios) catalog
Based on the approach from phpcfdi/sat-pys-scraper but implemented in Python
"""

import json
import logging
import os
import glob
from typing import Dict, List, Any
from datetime import datetime
from ._scraper import obtain_types, obtain_segments, obtain_families, obtain_classes

logger = logging.getLogger(__name__)


class PYSScraper:
    """Scraper for SAT PYS catalog using the same approach as phpcfdi/sat-pys-scraper"""
    
    def __init__(self):
        self.data = {
            "types": {},
            "segments": {},
            "families": {},
            "classes": {},
            "metadata": {
                "scraped_at": None,
                "total_types": 0,
                "total_segments": 0,
                "total_families": 0,
                "total_classes": 0
            }
        }
    
    def scrape_all(self) -> Dict[str, Any]:
        """Scrape the complete PYS catalog from SAT website"""
        logger.info("Starting comprehensive PYS catalog scraping")
        
        try:
            # Step 1: Get all types
            logger.info("Step 1: Obtaining types")
            types = obtain_types()
            self.data["types"] = types
            self.data["metadata"]["total_types"] = len(types)
            logger.info(f"Found {len(types)} types")
            
            # Step 2: For each type, get segments
            logger.info("Step 2: Obtaining segments for each type")
            for type_id, type_name in types.items():
                logger.info(f"Processing type: {type_name} (ID: {type_id})")
                try:
                    segments = obtain_segments(type_id)
                    self.data["segments"][type_id] = segments
                    self.data["metadata"]["total_segments"] += len(segments)
                    logger.info(f"Found {len(segments)} segments for type {type_name}")
                    
                    # Step 3: For each segment, get families
                    for segment_id, segment_name in segments.items():
                        logger.info(f"Processing segment: {segment_name} (ID: {segment_id})")
                        try:
                            families = obtain_families(type_id, segment_id)
                            family_key = f"{type_id}_{segment_id}"
                            self.data["families"][family_key] = families
                            self.data["metadata"]["total_families"] += len(families)
                            logger.info(f"Found {len(families)} families for segment {segment_name}")
                            
                            # Step 4: For each family, get classes
                            for family_id, family_name in families.items():
                                logger.info(f"Processing family: {family_name} (ID: {family_id})")
                                try:
                                    classes = obtain_classes(type_id, segment_id, family_id)
                                    class_key = f"{type_id}_{segment_id}_{family_id}"
                                    self.data["classes"][class_key] = classes
                                    self.data["metadata"]["total_classes"] += len(classes)
                                    logger.info(f"Found {len(classes)} classes for family {family_name}")
                                    
                                except Exception as e:
                                    logger.error(f"Error getting classes for family {family_name}: {e}")
                                    continue
                                    
                        except Exception as e:
                            logger.error(f"Error getting families for segment {segment_name}: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error getting segments for type {type_name}: {e}")
                    continue
            
            # Update metadata
            self.data["metadata"]["scraped_at"] = datetime.now().isoformat()
            
            logger.info("PYS catalog scraping completed successfully")
            logger.info(f"Total data collected:")
            logger.info(f"  - Types: {self.data['metadata']['total_types']}")
            logger.info(f"  - Segments: {self.data['metadata']['total_segments']}")
            logger.info(f"  - Families: {self.data['metadata']['total_families']}")
            logger.info(f"  - Classes: {self.data['metadata']['total_classes']}")
            
            return self.data
            
        except Exception as e:
            logger.error(f"Error during PYS catalog scraping: {e}")
            raise
    
    def get_flattened_data(self) -> List[Dict[str, Any]]:
        """Get flattened data structure similar to your current taxonomy format"""
        flattened = []
        
        for type_id, type_name in self.data["types"].items():
            type_data = {
                "tipo_num": int(type_id),
                "Tipo": type_name,
                "Div_num": None,
                "Division": None,
                "Grupo_num": None,
                "Grupo": None,
                "Clase_num": None,
                "Clase": None
            }
            
            # Get segments for this type
            segments = self.data["segments"].get(type_id, {})
            for segment_id, segment_name in segments.items():
                segment_data = type_data.copy()
                segment_data.update({
                    "Div_num": int(segment_id),
                    "Division": segment_name
                })
                
                # Get families for this type-segment combination
                family_key = f"{type_id}_{segment_id}"
                families = self.data["families"].get(family_key, {})
                for family_id, family_name in families.items():
                    family_data = segment_data.copy()
                    family_data.update({
                        "Grupo_num": int(family_id),
                        "Grupo": family_name
                    })
                    
                    # Get classes for this type-segment-family combination
                    class_key = f"{type_id}_{segment_id}_{family_id}"
                    classes = self.data["classes"].get(class_key, {})
                    for class_id, class_name in classes.items():
                        class_data = family_data.copy()
                        class_data.update({
                            "Clase_num": int(class_id),
                            "Clase": class_name
                        })
                        flattened.append(class_data)
        
        return flattened
    
    def save_to_json(self, filename: str = None) -> str:
        """Save scraped data to JSON file"""
        if filename is None:
            filename = "/app/pys_catalog_latest.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Data saved to {filename}")
        return filename
    
    def save_flattened_to_json(self, filename: str = None) -> str:
        """Save flattened data to JSON file"""
        if filename is None:
            filename = "/app/pys_flattened_latest.json"
        
        flattened_data = self.get_flattened_data()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(flattened_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Flattened data saved to {filename}")
        return filename


def cleanup_old_files():
    """Remove old PYS catalog files, keeping only the latest ones"""
    try:
        # Remove old timestamped files
        old_files = glob.glob("/app/pys_catalog_*.json") + glob.glob("/app/pys_flattened_*.json")
        # Keep only the latest files
        latest_files = ["/app/pys_catalog_latest.json", "/app/pys_flattened_latest.json"]
        
        for file_path in old_files:
            if file_path not in latest_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed old file: {file_path}")
    except Exception as e:
        logger.warning(f"Error cleaning up old files: {e}")


def scrape_pys_catalog() -> Dict[str, Any]:
    """Main function to scrape PYS catalog"""
    scraper = PYSScraper()
    return scraper.scrape_all()


def scrape_and_save_pys_catalog() -> Dict[str, str]:
    """Scrape PYS catalog and save both raw and flattened data"""
    scraper = PYSScraper()
    data = scraper.scrape_all()
    
    # Clean up old files first
    cleanup_old_files()
    
    # Save raw data
    raw_file = scraper.save_to_json()
    
    # Save flattened data
    flattened_file = scraper.save_flattened_to_json()
    
    return {
        "raw_file": raw_file,
        "flattened_file": flattened_file,
        "metadata": data["metadata"]
    }


if __name__ == "__main__":
    # Test the scraper
    logging.basicConfig(level=logging.INFO)
    result = scrape_and_save_pys_catalog()
    print(f"Scraping completed. Files saved:")
    print(f"  Raw data: {result['raw_file']}")
    print(f"  Flattened data: {result['flattened_file']}")
    print(f"  Metadata: {result['metadata']}")
