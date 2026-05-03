import json
import csv
from pathlib import Path

from generators.base_generator import BaseGenerator
from models.schemas import DataType
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CSVJSONGenerator(BaseGenerator):
    def __init__(self, structured_output, output_filename=None, file_format='json'):
        self.file_format = file_format
        super().__init__(structured_output, output_filename)
    
    def generate(self) -> Path:
        try:
            if self.file_format == 'json':
                return self._generate_json()
            elif self.file_format == 'csv':
                return self._generate_csv()
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise
    
    def get_file_extension(self) -> str:
        return self.file_format
    
    def _generate_json(self) -> Path:
        logger.info(f"Generating JSON: {self.filepath}")
        
        data = self.output.dict()
        
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"JSON generated: {self.filepath}")
        return self.filepath
    
    def _generate_csv(self) -> Path:
        logger.info(f"Generating CSV: {self.filepath}")
        
        with open(self.filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            writer.writerow([self.output.title])
            writer.writerow([])
            
            for section in self.output.sections:
                if section.type == DataType.TABLE:
                    content = section.content
                    if 'headers' in content:
                        writer.writerow(content['headers'])
                        writer.writerows(content.get('rows', []))
                        writer.writerow([])
        
        logger.info(f"CSV generated: {self.filepath}")
        return self.filepath