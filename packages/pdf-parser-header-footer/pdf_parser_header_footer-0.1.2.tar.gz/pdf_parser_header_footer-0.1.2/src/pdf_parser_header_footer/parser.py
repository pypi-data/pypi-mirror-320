import json
import os
from pathlib import Path
from tqdm.auto import tqdm
from typing import Union, Optional
from .config import ParserConfig
from .utils import boundaries, text, visualization

class PDFSectionParser:
    """
    Main class for parsing PDFs and extracting sections (header, body, footer).
    Detects section boundaries and can generate both visual PDF output and JSON structured content.
    """
    
    def __init__(self, config: Optional[ParserConfig] = None):
        """
        Initialize the parser with optional configuration.
        
        Args:
            config: Configuration settings. If None, default settings will be used.
        """
        self.config = config or ParserConfig()
        
    def parse(self, input_path: Union[str, Path]) -> None:
        """
        Parse either a single PDF file or a directory of PDFs.
        
        Args:
            input_path: Path to either a PDF file or directory containing PDFs
        
        Raises:
            FileNotFoundError: If input_path doesn't exist
            ValueError: If input_path is not a PDF file or directory
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Path does not exist: {input_path}")
        
        if input_path.is_file():
            if input_path.suffix.lower() != '.pdf':
                raise ValueError(f"File must be a PDF: {input_path}")
            self._parse_single_file(input_path)
        elif input_path.is_dir():
            self._parse_directory(input_path)
        else:
            raise ValueError(f"Input path {input_path} is neither a file nor directory")
    
    def _parse_single_file(self, file_path: Path) -> None:
        """
        Process a single PDF file.
        
        Args:
            file_path: Path to the PDF file
        """
        # Convert to Path object and resolve any symlinks
        file_path = Path(file_path).resolve()
        output_dir = (self.config.output_dir or file_path.parent).resolve()
        
        # Create all necessary directories
        output_dir.mkdir(parents=True, exist_ok=True)
        split_dir = output_dir / "split_sections"
        split_dir.mkdir(exist_ok=True)
        temp_dir = output_dir / "temp_split_pdfs"
        temp_dir.mkdir(exist_ok=True)

        try:            
            # 1. Detect header and footer boundaries
            print("Detecting header and footer boundaries...")
            header, footer = boundaries.detect_header_footer_boundaries(str(file_path))
            
            # 2. Process boundaries and generate split sections
            if self.config.generate_boundaries_pdf or self.config.generate_json:
                visualization.delete_lines_if_needed(
                    str(file_path),
                    split_dir,
                    header,
                    footer
                )
            
            # 3. Generate JSON with extracted text if requested
            if self.config.generate_json:
                print("Extracting and processing text...")
                result = None
                
                for filename in tqdm(split_dir.glob("*_page*_*.pdf")):
                    if "_final_boundaries" not in str(filename):
                        markdown = text.split_and_convert_to_markdown(str(filename), temp_dir)
                        result = text.create_json_object(result, str(filename), markdown)
                
                # Save JSON output
                if result:
                    base_name = file_path.stem
                    final_result = {
                        "pdf_with_lines": result["pdf_with_lines"],
                        "pages": [result["pages"][num] for num in sorted(result["pages"].keys())]
                    }
                    json_path = output_dir / f"{base_name}.json"
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(final_result, f, ensure_ascii=False, indent=4)
                    print(f"JSON output saved to: {json_path}")

        finally:
            # Clean up temporary files and directories
            print("Cleaning up temporary files...")
            try:
                if temp_dir.exists():
                    for f in temp_dir.glob("*"):
                        f.unlink()
                    temp_dir.rmdir()
                if split_dir.exists():
                    for f in split_dir.glob("*"):
                        f.unlink()
                    split_dir.rmdir()
            except Exception as cleanup_error:
                print(f"Error during cleanup: {str(cleanup_error)}")

        print(f"Successfully processed: {file_path}")
    
    def _parse_directory(self, dir_path: Path) -> None:
        """
        Process all PDF files in a directory.
        
        Args:
            dir_path: Path to directory containing PDF files

        Raises:
            ValueError: If no PDF files are found in the directory
        """
        pdf_files = list(dir_path.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in directory: {dir_path}")
        print(f"Found {len(pdf_files)} PDF files in {dir_path}")
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            try:
                self._parse_single_file(pdf_file)
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
                continue