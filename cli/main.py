import click
from pathlib import Path
from ai_engine.prompt_processor import PromptProcessor
from generators.pdf_generator import PDFGenerator
from generators.excel_generator import ExcelGenerator
from generators.docx_generator import DocxGenerator
from generators.csv_json_generator import CSVJSONGenerator
from models.schemas import FileType, ColorScheme
from utils.logger import setup_logger
from utils.validators import PromptValidator
from config.settings import settings

logger = setup_logger(__name__)

@click.group()
def cli():
    """AI File Generator - Generate professional documents from prompts"""
    pass

@cli.command()
@click.option('--prompt', '-p', required=True, help='Describe what you want to generate')
@click.option('--file-type', '-f', type=click.Choice(['pdf', 'excel', 'docx', 'csv', 'json']), 
              default='pdf', help='Output file type')
@click.option('--color-scheme', '-c', type=click.Choice(['professional', 'modern', 'vibrant', 'classic']),
              default='professional', help='Color scheme')
def generate(prompt, file_type, color_scheme):
    """Generate a file from a prompt"""
    try:
        PromptValidator.validate_prompt(prompt)
        PromptValidator.validate_file_type(file_type)
        
        click.echo(f"🚀 Generating {file_type.upper()} file...")
        
        processor = PromptProcessor()
        structured_output = processor.process(prompt, file_type)
        logger.info("✅ AI processing complete")
        
        generator = _get_generator(file_type, structured_output)
        filepath = generator.generate()
        
        file_size = filepath.stat().st_size / (1024 * 1024)
        click.echo(f"\n✨ Success!")
        click.echo(f"  File: {filepath.name}")
        click.echo(f"  Size: {file_size:.2f} MB")
        click.echo(f"  Location: {filepath}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        logger.error(f"Generation failed: {str(e)}")
        raise click.Exit(1)

@cli.command()
def info():
    """Show system information"""
    click.echo(f"App: {settings.APP_NAME} v{settings.APP_VERSION}")
    click.echo(f"Environment: {settings.ENVIRONMENT}")
    click.echo(f"Output Directory: {settings.OUTPUT_DIR}")
    click.echo(f"API available backends:")
    if settings.OR_API_KEY:
        click.echo(f"  ✓ OpenRouter: {settings.OR_MODEL}")
    else:
        click.echo(f"  ✗ OpenRouter: not configured")
    if settings.HF_API_KEY:
        click.echo(f"  ✓ HuggingFace: {settings.HF_MODEL}")
    else:
        click.echo(f"  ✗ HuggingFace: not configured")

def _get_generator(file_type: str, structured_output):
    """Get appropriate generator"""
    if file_type == 'pdf':
        return PDFGenerator(structured_output)
    elif file_type == 'excel':
        return ExcelGenerator(structured_output)
    elif file_type == 'docx':
        return DocxGenerator(structured_output)
    elif file_type == 'csv':
        return CSVJSONGenerator(structured_output, file_format='csv')
    elif file_type == 'json':
        return CSVJSONGenerator(structured_output, file_format='json')
    else:
        raise ValueError(f"Unknown file type: {file_type}")

if __name__ == '__main__':
    cli()