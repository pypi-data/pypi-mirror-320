from hdfs import InsecureClient
import os
from .forward_config import *
from  .connect_mongo import *
import asyncio
from .pipe_line_obsei import *


class FunctionMongo:
    """Load result analyze to Mongo"""
    @staticmethod
    def save_file_mongo(mongo_url: str,db_name:str,collection:str,hdfs_file_path:str ,hdfs_output_file_path: str,obsei_ner,obsei_sentiment,obsei_classification):
        """
    This function saves processed data into a MongoDB collection after processing 
    a file from HDFS using the provided models for NER, sentiment analysis, and text classification.
    
    Parameters:
    mongo_url (str): The URL of the MongoDB instance (e.g., 'mongodb://localhost:27017').
    db_name (str): The name of the MongoDB database where data will be stored.
    collection (str): The name of the MongoDB collection where data will be stored.
    hdfs_file_path (str): The path to the input file in HDFS that needs to be processed.
    hdfs_output_file_path (str): The path to save the processed output file in HDFS.
    obsei_ner: A model or object used for Named Entity Recognition (NER).
    obsei_sentiment: A model or object used for sentiment analysis.
    obsei_classification: A model or object used for text classification.

    Returns:
    None: The function saves the processed data to MongoDB and does not return anything.
    """
        collection = connect_to_mongo(mongo_url,db_name, collection)
        
        if collection is False: 
            return "Connection failed. Please check the field Mongo"
        document = {
                    "hdfs_file_path": hdfs_file_path,
                    "hdfs_file_convert_path": hdfs_output_file_path,
                    "obsei_ner": obsei_ner,
                    "obsei_sentiment": obsei_sentiment,
                    "obsei_classification": obsei_classification
                }
        record = collection.find_one({"hdfs_file_path": hdfs_file_path})
        if not record:
            collection.insert_one(document)
            return True
        else:     
            return False

import os
from .connect_hdfs import *
class HDFSAnalyzeFile:
    """Download file HDFS and analyze. Then save link to MongoDB and load file to HDFS"""
    @staticmethod
    def hadoop_load_file_and_analyze(hdfs_url:str, hdfs_user: str,mongo_url:str, db_name:str,hdfs_source_directory: str, output_base_directory: str, name: str,language:str):
     """
    This function loads files from HDFS, processes them, and stores the results in a specified database.
    
    Parameters:
    mongo_url (str): The URL of the MongoDB instance (e.g., 'mongodb://localhost:27017').
    hdfs_url (str): The URL of the HDFS instance (e.g., 'hdfs://localhost:9000').
    hdfs_user (str): The user name for accessing the HDFS system.
    db_name (str): The name of the database where processed data will be stored.
    hdfs_source_directory (str): The directory in HDFS where input files are located.
    output_base_directory (str): The directory in HDFS where the processed output files will be saved.
    name (str): A name or identifier for the task or job being processed.
    language(str): 

    Returns:
    None: The function processes files from HDFS and stores the result in the specified database and HDFS directory.
    """
     if not hdfs_url.strip():
        return "HDFS URL cannot be empty or blank."
     if not mongo_url.strip():
        return "MONGO URL cannot be empty or blank."
     if not hdfs_user.strip():
        return "HDFS User cannot be empty or blank."
     if not db_name.strip():
        return "Database name (db_name) cannot be empty or blank."
     if not hdfs_source_directory.strip():
        return "HDFS source directory (hdfs_source_directory) cannot be empty or blank."
     if not output_base_directory.strip():
        return "Output base directory (output_base_directory) cannot be empty or blank."
     if not name.strip():
        return "Name cannot be empty or blank."
     if not language.strip():
        return "Language cannot be empty or blank."
     client = InsecureClient(hdfs_url,hdfs_user)
     client1 = hdfs_connection(hdfs_url,hdfs_user)
     if client1 is False:
         return "Error connecting to HDFS. Please check the HDFS URL or HDFS User."
     
     
     os.makedirs(output_base_directory, exist_ok=True)
     local_temp_directory = f"./temp/{name}/"
     os.makedirs(local_temp_directory, exist_ok=True)

     try:
            hdfs_files = client.list(hdfs_source_directory)
            for file_name in hdfs_files:
                hdfs_file_path = f"{hdfs_source_directory.rstrip('/')}/{file_name}"
                local_file_path = os.path.join(local_temp_directory, file_name)
                client.download(hdfs_file_path, local_file_path, overwrite=True)
                file_extension = os.path.splitext(file_name)[1].lower()
                base_name = os.path.splitext(file_name)[0]

                if file_extension:
                    hdfs_directory = f'{hdfs_source_directory}/{name}/output_{file_extension[1:]}/'
                else:
                    hdfs_directory = f'{hdfs_source_directory}/{name}/output_unknown/'

                # Tạo thư mục trên HDFS nếu chưa tồn tại
                if not client.status(hdfs_directory, strict=False):
        
                    client.makedirs(hdfs_directory)

                try:
                    result = ExtractFile.extract_file(local_file_path)
                    data = asyncio.run(process_url_hadoop(mongo_url,hdfs_file_path, result, db_name, name, "VN"))
                    output_directory = os.path.join(output_base_directory, file_extension[1:] if file_extension else "unknown")
                    os.makedirs(output_directory, exist_ok=True)
                    output_file_path = os.path.join(output_directory, f"{base_name}.md")

                    with open(output_file_path, "w", encoding="utf-8") as f:
                        f.write(result)

                    hdfs_output_file_path = os.path.join(hdfs_directory, f"{base_name}.md")
                    print(hdfs_output_file_path)
                    client.upload(hdfs_output_file_path, output_file_path, overwrite=True)

                    FunctionMongo.save_file_mongo(mongo_url,db_name, name, hdfs_file_path, hdfs_output_file_path, data[2], data[1], data[0])
                    os.remove(local_file_path)
                    os.remove(output_file_path)
                    os.rmdir(output_directory)
                except Exception as e:
                    print(f"Error processing file {file_name}: {e}")
                    continue
            os.rmdir(local_temp_directory)
            os.rmdir(output_base_directory)
     except Exception as e:
             print (f"Error processing files in HDFS directory: {e}")



