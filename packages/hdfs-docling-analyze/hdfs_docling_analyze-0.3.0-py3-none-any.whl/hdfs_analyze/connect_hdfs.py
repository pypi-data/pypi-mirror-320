from hdfs import InsecureClient

def hdfs_connection(hdfs_url, user = "root"):
    try:
        client = InsecureClient(hdfs_url,user = user)
        status = client.list('/')
        if status:
         return client
        else:
            return False
    except:
        return False