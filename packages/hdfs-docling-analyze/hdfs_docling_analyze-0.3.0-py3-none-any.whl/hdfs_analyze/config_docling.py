from docling.datamodel.base_models import InputFormat
from docling.document_converter import *
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.datamodel.pipeline_options import *

def check_file_extension(file_path, valid_extensions):
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in valid_extensions:
        raise ValueError(f"Tệp không phải là định dạng hợp lệ. Định dạng hợp lệ: {', '.join(valid_extensions)}")
    return ext.lower()

class ConfigPipelineOption:
    @staticmethod
    def config_ocr_pdf(file_path):
        try:
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = True
            pipeline_options.do_table_structure = True
            pipeline_options.ocr_options = TesseractCliOcrOptions(lang=["vie"])            
            pipeline_options.table_structure_options.do_cell_matching = True
            pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
            pipeline_options.generate_picture_images = True
            pipeline_options.generate_page_images = True
            pipeline_options.generate_table_images = True
            return pipeline_options
        except Exception as e:
            raise ValueError(f"Lỗi khi cấu hình: {str(e)}")
        
    @staticmethod
    def config_ocr(file_path):
        try:
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = False
            pipeline_options.do_table_structure = True          
            pipeline_options.table_structure_options.do_cell_matching = True
            pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
            return pipeline_options
        except Exception as e:
            raise ValueError(f"Lỗi khi cấu hình: {str(e)}")
    
    @staticmethod
    def config_ocr_no_table(file_path):
        try:
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = False
            pipeline_options.do_table_structure = False          
            pipeline_options.table_structure_options.do_cell_matching = False
            pipeline_options.table_structure_options.mode = TableFormerMode.FAST
            
            return pipeline_options
        except Exception as e:
            raise ValueError(f"Lỗi khi cấu hình: {str(e)}")

class ConfigConverter:
    @staticmethod
    def config_converter(pipeline_options):
        try:
            converter = DocumentConverter(format_options={
        InputFormat.PPTX : PowerpointFormatOption(pipeline_options=pipeline_options),
        InputFormat.XLSX : ExcelFormatOption(pipeline_options=pipeline_options),
        InputFormat.HTML : HTMLFormatOption(pipeline_options=pipeline_options),
        InputFormat.ASCIIDOC:AsciiDocFormatOption(pipeline_options=pipeline_options),
        InputFormat.MD:MarkdownFormatOption(pipeline_options=pipeline_options),
        InputFormat.PDF :PdfFormatOption(pipeline_options=pipeline_options),
        InputFormat.DOCX : WordFormatOption(pipeline_options=pipeline_options),
        InputFormat.XML_PUBMED: XMLPubMedFormatOption(),
        InputFormat.XML_USPTO: PatentUsptoFormatOption(),
        InputFormat.IMAGE: ImageFormatOption()
    })
            
            return converter
        except Exception as e:
            raise ValueError(f"Lỗi khi cấu hình: {str(e)}")