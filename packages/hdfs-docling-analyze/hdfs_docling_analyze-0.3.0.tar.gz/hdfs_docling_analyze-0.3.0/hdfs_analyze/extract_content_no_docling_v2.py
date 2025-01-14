
from langchain_community.document_loaders import Docx2txtLoader
import zipfile
import xml.etree.ElementTree as ET
import json
from pylatexenc.latex2text import LatexNodes2Text
from pyexcel_ods3 import get_data
import csv
from spire.doc import *
from spire.doc.common import *
import os
import pandas as pd
import re
from langchain_community.document_loaders import UnstructuredODTLoader,UnstructuredExcelLoader
from odf.opendocument import load
from odf.text import P, Span, S
from langchain_community.document_loaders import UnstructuredTSVLoader,UnstructuredRTFLoader
from langchain_community.document_loaders import UnstructuredPDFLoader
import xml.etree.ElementTree as ET
from llama_parse import LlamaParse
from llama_index import SimpleDirectoryReader
from llama_parse import LlamaParse
parser = LlamaParse(result_type="markdown",api_key="llx-MFNOzhVXgCwf8Ic0BASMlnSqzTkbbU3N2GQnIuwAX01QDn3l")

SUPPORTED_EXTENSIONS = [
    '.pdf', '.602', '.json', '.abw', '.cgm', '.cwk', '.doc', '.docx', '.docm', '.dot', '.dotm', '.hwp', '.key', '.lwp', '.mw',
    '.mcw', '.pages', '.pbd', '.ppt', '.pptm', '.pptx', '.pot', '.potm', '.potx', '.rtf', '.sda', '.sdd', '.sdp',
    '.sdw', '.sgl', '.sti', '.sxi', '.sxw', '.stw', '.sxg', '.txt', '.uof', '.uop', '.uot', '.vor', '.wpd', '.wps',
    '.xml', '.zabw', '.epub', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', '.webp', '.htm', '.html',
    '.xlsx', '.xls', '.xlsm', '.xlsb', '.xlw', '.csv', '.dif', '.sylk', '.slk', '.prn', '.numbers', '.et', '.ods',
    '.fods', '.uos1', '.uos2', '.dbf', '.wk1', '.wk2', '.wk3', '.wk4', '.wks', '.123', '.wq1', '.wq2', '.wb1', '.wb2',
    '.wb3', '.qpw', '.xlr', '.eth', '.tsv', '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'
]


def read_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    content = []
    for elem in root.iter():
        if elem.text:
            content.append(elem.text.strip())
    return "\n".join(content)


def check_file_extension(file_path, valid_extensions):
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in valid_extensions:
        raise ValueError(f"Tệp không phải là định dạng hợp lệ. Định dạng hợp lệ: {', '.join(valid_extensions)}")
    return ext.lower()


def read_json(file_path):
    check_file_extension(file_path, ['.json'])
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return json.dumps(data, indent=4, ensure_ascii=False)


def extract_text_from_ott(file_path):
    check_file_extension(file_path, ['.ott'])
    doc = load(file_path)
    text_content = []
    def extract_text_from_element(element):
        text = ""
        for child in element.childNodes:
            if child.nodeType == 3:
                text += child.data
            elif child.nodeType == 1:
                if child.tagName == "text:s": 
                    text += " "
                elif child.tagName in ["text:span", "text:p"]:
                    text += extract_text_from_element(child)
        return text
    for paragraph in doc.getElementsByType(P):
        text_content.append(extract_text_from_element(paragraph))
    return "\n".join(text_content)


def extract_text_from_doc(file_path):
    check_file_extension(file_path, ['.doc'])
    doc = Document()
    doc.LoadFromFile(file_path)
    data = doc.GetText()
    return data

def extract_text_from_docx(file_path):
    check_file_extension(file_path, ['.docx'])
    doc = Document()
    doc.LoadFromFile(file_path)
    data = doc.GetText()
    return data


def convert_latex_to_text(file_url):
    """
    Hàm chuyển đổi nội dung LaTeX từ file .tex sang văn bản thuần.
    
    Tham số:
        file_url (str): Đường dẫn URL của file .tex.
    
    Trả về:
        str: Nội dung văn bản đã chuyển đổi từ LaTeX.
    """
    try:
        # Đọc file .tex
        with open(file_url, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Chuyển đổi LaTeX thành văn bản thuần
        converter = LatexNodes2Text()
        plain_text = converter.latex_to_text(content)
        
        return plain_text
    except FileNotFoundError:
        return f"File not found: {file_url}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


def extract_text_from_txt(file_path):
    check_file_extension(file_path, ['.txt'])
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def extract_text_from_odp(file_path):
    check_file_extension(file_path, ['.odp'])
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall("extracted_folder") 
    slides_file = "extracted_folder/content.xml"
    tree = ET.parse(slides_file)
    root = tree.getroot()
    all_text = []
    for elem in root.iter():
        if 'text' in elem.tag:
            if elem.text:
                all_text.append(elem.text.strip())
    return all_text


def read_tsv(file_path):
    check_file_extension(file_path, ['.tsv'])
    content = []
    with open(file_path, 'r', encoding='utf-8') as file:
        tsv_reader = csv.reader(file, delimiter='\t')
        for row in tsv_reader:
            content.append("\t".join(row))
    return "\n".join(content)


def load_file_content_llamaIndex(file_path):
    parser = LlamaParse(result_type="markdown", api_key="llx-MFNOzhVXgCwf8Ic0BASMlnSqzTkbbU3N2GQnIuwAX01QDn3l")
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"File extension {file_extension} is not supported.")
    file_extractor = {file_extension: parser}
    reader = SimpleDirectoryReader(
        input_files=[file_path],
        file_extractor=file_extractor
    )
    documents = reader.load_data()
    full_content = "\n".join([doc.text for doc in documents])
    return full_content


class LlamaIndexExtractor:
    @staticmethod
    def read_doc_text(file_path):
        try:
            data = load_file_content_llamaIndex(file_path)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản: {str(e)}")


class DocExtractor:
    @staticmethod
    def read_doc_text(file_path):
        check_file_extension(file_path, ['.doc'])
        try:
            data = extract_text_from_docx(file_path)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .docx: {str(e)}")

class DocxExtractor:
    @staticmethod
    def read_doc_text(file_path):
        check_file_extension(file_path, ['.docx'])
        try:
            data = extract_text_from_docx(file_path)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .docx: {str(e)}")


class JsonExtractor:
    @staticmethod
    def read_json_text(file_path):
        check_file_extension(file_path, ['.json'])
        try:
            data = read_json(file_path)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .json: {str(e)}")


class TxtExtractor:
    @staticmethod
    def read_txt_text(file_path):
        check_file_extension(file_path, ['.txt'])
        try:
            data = extract_text_from_txt(file_path)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .txt: {str(e)}")


class LatexExtractor:
    @staticmethod
    def read_latex_text(file_path):
            check_file_extension(file_path, ['.tex'])
            try:
                data = convert_latex_to_text(file_path)
                return data
            except Exception as e:
                raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .tex: {str(e)}")


class DotmLangChainExtractor:
    @staticmethod
    def read_dotm_text(file_path):
        check_file_extension(file_path, ['.dotm'])
        try:
            loader = Docx2txtLoader(file_path)
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .dotm: {str(e)}")
from langchain_community.document_loaders import PyPDFLoader,PyPDFium2Loader,PDFMinerLoader
class PDFLangChainExtractor:
    @staticmethod
    def read_dotm_text(file_path):
        check_file_extension(file_path, ['.pdf'])
        try:
            loader = PDFMinerLoader(file_path)
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .dotm: {str(e)}")


class ExcelDocumentLangChainExtractor:
    @staticmethod
    def read_xls_text(file_path):
        check_file_extension(file_path, ['.xls'])
        try:
            loader = UnstructuredExcelLoader(file_path)
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp Excel: {str(e)}")

from langchain_community.document_loaders import UnstructuredPowerPointLoader
class PptxDocumentLangChainExtractor:
    @staticmethod
    def read_xls_text(file_path):
        check_file_extension(file_path, ['.pptx'])
        try:
            loader = UnstructuredPowerPointLoader(file_path)
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp Excel: {str(e)}")

import win32com.client
def extract_text_from_ppt(ppt_path):
    content = "" 
    try:
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        presentation = powerpoint.Presentations.Open(ppt_path, WithWindow=False)
        for slide in presentation.Slides:
            for shape in slide.Shapes:
                if shape.HasTextFrame:
                    content += shape.TextFrame.TextRange.Text + "\n"  # Thêm nội dung của mỗi shape

        # Đóng PowerPoint
        presentation.Close()
        powerpoint.Quit()
        return content 

    except Exception as e:
        return f"Lỗi khi xử lý file .ppt: {e}"
    

class PptDocumentLangChainExtractor:
    @staticmethod
    def read_xls_text(file_path):
        check_file_extension(file_path, ['.ppt'])
        try:
            data = extract_text_from_ppt(file_path)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp Excel: {str(e)}")


class DotxLangChainExtractor:
    @staticmethod
    def read_dotx_text(file_path):
        check_file_extension(file_path, ['.dotx'])
        try:
            loader = Docx2txtLoader(file_path)
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .dotx: {str(e)}")


class DocmLangChainExtractor:
    @staticmethod
    def read_docm_text(file_path):
        check_file_extension(file_path, ['.docm'])
        try:
            loader = Docx2txtLoader(file_path)
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .docm: {str(e)}")


class RtfLangChainExtractor:
    @staticmethod
    def read_rtf_text(file_path):
        check_file_extension(file_path, ['.rtf'])
        try:
            loader = UnstructuredRTFLoader(file_path)
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .rtf: {str(e)}")


from striprtf.striprtf import rtf_to_text
def read_rtf(file_path):
    check_file_extension(file_path, ['.rtf'])
    with open(file_path, 'r', encoding='utf-8') as file:
        rtf_content = file.read()
    text = rtf_to_text(rtf_content)
    return text


class RtfExtractor:
    @staticmethod
    def read_rtf_text(file_path):
        check_file_extension(file_path, ['.rtf'])
        try:
            data = read_rtf(file_path)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .rtf: {str(e)}")


class TSVExtractor:
    @staticmethod
    def read_tsv_text(file_path):
        check_file_extension(file_path, ['.tsv'])
        try:
            data = read_tsv(file_path)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .tsv: {str(e)}")


class TsvLangChainExtractor:
    @staticmethod
    def read_tsv_text(file_path):
        check_file_extension(file_path, ['.tsv'])
        try:
            loader = UnstructuredTSVLoader(file_path)
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .tsv: {str(e)}")


from langchain_community.document_loaders import UnstructuredXMLLoader
class XmlLangchainExtractor:
    @staticmethod
    def read_xml_text(file_path):
        check_file_extension(file_path, ['.xml'])
        try:
            loader = UnstructuredXMLLoader(file_path)
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .xml: {str(e)}")


class XmlExtractor:
    @staticmethod
    def read_xml_text(file_path):
        check_file_extension(file_path, ['.xml'])
        try:
            data = read_xml(file_path)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .xml: {str(e)}")
    

class OpenDocumentExtractor:
    @staticmethod
    def read_odt_text(file_path):
        check_file_extension(file_path, ['.odt'])
        try:
            loader = UnstructuredODTLoader(file_path, "single")
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .odt: {str(e)}")


    @staticmethod
    def read_ods_text(file_path):
        check_file_extension(file_path, ['.ods'])
        try:
            loader = get_data(file_path)
            data = json.dumps(loader)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .ods: {str(e)}")


    @staticmethod
    def read_odp_text(file_path):
        check_file_extension(file_path, ['.odp'])
        try:
            loader = extract_text_from_odp(file_path)
            odp_content = [re.sub(r'(?<!\d)0(?!\d)', '', text) for text in loader]
            data = "\n".join(odp_content)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .odp: {str(e)}")


    @staticmethod
    def read_ott_text(file_path):
        check_file_extension(file_path, ['.ott'])
        try:
            data = extract_text_from_ott(file_path)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi trích xuất văn bản từ tệp .ott: {str(e)}")
