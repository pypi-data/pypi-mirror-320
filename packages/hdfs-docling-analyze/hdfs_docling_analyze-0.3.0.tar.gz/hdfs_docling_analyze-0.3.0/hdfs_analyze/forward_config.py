from .extract_content_no_docling_v2 import *
from .config_docling import *
from docling.document_converter import *
from docling.datamodel.pipeline_options import *
from docling_core.types.doc import ImageRefMode

class CheckDocLing:
  @staticmethod
  def check_docling(file_name:str):
    valid_docling_extensions = [
        "docx", "pptx", "html", "image", "pdf", "md", "xlsx", "asciidoc", "ppsx", "pptm", 
        "potm", "adoc", "asc", "htm", "xhtml", "nxml", "xml","txt","xml"
    ]
    file_extension = file_name.split(".")[-1].lower()
    if file_extension in valid_docling_extensions:
        return True
    else:
        return False

  @staticmethod
  def check_no_docling(file_name:str):
    valid_no_docling_extensions = [
        "doc", "json", "dotm", "xls", "dotx", "docm", "rtf", "tsv", "odt", "ods", "odp", "ott","tex","txt","xml","ppt"
    ]
    file_extension = file_name.split(".")[-1].lower()
    if file_extension in valid_no_docling_extensions:
        return True
    else:
        return False

class ExtractFile:
 @staticmethod
 def extract_file(file_path: str):
    if CheckDocLing.check_docling(file_path) == True:
        if file_path.split(".")[-1].lower() in ["xml","txt","pptx","ppt"]:
         try:
          pipelineOptions = ConfigPipelineOption.config_ocr(file_path)
          converter = ConfigConverter.config_converter(pipelineOptions)    
          result = converter.convert(file_path)
          output_text = result.document.export_to_markdown(image_mode=ImageRefMode.PLACEHOLDER)
          return output_text
         except :
          if file_path.split(".")[-1].lower() == "xml":
            output_text = XmlLangchainExtractor.read_xml_text(file_path)
            return output_text
          if file_path.split(".")[-1].lower() == "txt":
            output_text = TxtExtractor.read_txt_text(file_path)
            return output_text
          if file_path.split(".")[-1].lower() == "pptx":
             output_text = PptxDocumentLangChainExtractor.read_xls_text(file_path)
             return output_text
         
        elif file_path.split(".")[-1].lower() in ["pdf"]:
      #    pipelineOptions = config_docling.ConfigPipelineOption.config_ocr_pdf(file_path)
         pipelineOptions = ConfigPipelineOption.config_ocr_pdf(file_path)
         converter = ConfigConverter.config_converter(pipelineOptions)    
         result = converter.convert(file_path)
         output_text = result.document.export_to_markdown(image_mode=ImageRefMode.PLACEHOLDER)
         return output_text
        elif file_path.split(".")[-1].lower() in ["docx"]:
              output_text = DocxExtractor.read_doc_text(file_path)
              return output_text

        else:
         pipelineOptions = ConfigPipelineOption.config_ocr(file_path)
         converter = ConfigConverter.config_converter(pipelineOptions)    
         result = converter.convert(file_path)
         output_text = result.document.export_to_markdown(image_mode=ImageRefMode.PLACEHOLDER)
         return output_text     
    elif CheckDocLing.check_docling(file_path) == False and CheckDocLing.check_no_docling(file_path) == True:
        if CheckDocLing.check_no_docling(file_path) == True:
             if file_path.split(".")[-1].lower() == "doc":
                   output_text = DocExtractor.read_doc_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "ppt":
                   output_text = LlamaIndexExtractor.read_doc_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "json":
                  try:
                   output_text = JsonExtractor.read_json_text(file_path)
                   return output_text
                  except:
                    output_text = LlamaIndexExtractor.read_doc_text(file_path)
                    return output_text
             elif file_path.split(".")[-1].lower() == "dotm":
                   output_text = DotmLangChainExtractor.read_dotm_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "xls":
                   output_text = ExcelDocumentLangChainExtractor.read_xls_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "dotx":
                   output_text = DotxLangChainExtractor.read_dotx_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "docm":
                   output_text = DocmLangChainExtractor.read_docm_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "rtf":
                   output_text = RtfLangChainExtractor.read_rtf_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "tsv":
                   output_text = TSVExtractor.read_tsv_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "odt":
                   output_text = OpenDocumentExtractor.read_odt_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "ods":
                   output_text = OpenDocumentExtractor.read_ods_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "odp":
                   output_text = OpenDocumentExtractor.read_odp_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "ott":
                   output_text =OpenDocumentExtractor.read_ott_text(file_path)
                   return output_text
             elif file_path.split(".")[-1].lower() == "tex":
                   output_text =LatexExtractor.read_latex_text(file_path)
                   return output_text      
        else:
             ValueError("File not allow format")
    elif CheckDocLing.check_docling(file_path) == False and CheckDocLing.check_no_docling(file_path) == False:
        try:
          output_text = LlamaIndexExtractor.read_doc_text(file_path)
          return output_text
        except Exception as e:
          ValueError("File not allow format")
          