from psycopg2.sql import NULL
from datetime import date
import datetime
import os
import pathlib
import hashlib

class UploadFiles():
    createDir=False
    nameDir=""
    nameFile=""
    def __init__(self,nameDir=NULL,nameFile=NULL,createDir=False):
        self.nameDir = nameDir
        self.createDir = createDir
        self.nameFile=nameFile
        
    def setNameFile(self,nameFile):
        self.nameFile = nameFile
    
    def getNameFile(self):
        return self.nameFile
    
    def upload(self,fileItem):
        try:
            extension = ""
            print("inicia subida", fileItem)
            if not fileItem.file: 
                print("no file")
                return
            else:
                extension = self.getExtensionFile(fileItem.filename)
            
            if self.nameDir == NULL:
                print("no no dir")
                return
            
            if self.createDir == True:
                print("crear dir solicitado: ")
                if not os.path.exists(self.nameDir):
                    print("el dir no existe")
                    os.makedirs(self.nameDir)
            
            if self.nameFile == NULL:
                print("archivo sin nombre")
                strFileName = "file_"+datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
                md5 = hashlib.md5(strFileName.encode('utf-8')).hexdigest() 
                self.nameFile = md5 + self.getExtensionFile(fileItem.filename)
                
            
            print(self.getExtensionFile())
            file = open(os.path.join(self.nameDir, self.nameFile), 'wb')    
            
            while 1:
                chunk = fileItem.file.read(100000)
                if not chunk: break
                file.write (chunk)
            file.close()
            return {"status":"OK","error":"","namefile":self.nameFile}
        except IOError as e:
            return {"status":"ERROR","error":e,"namefile":self.nameFile}
        
    def deleteFile(self,fullPath):
        if os.path.exists(fullPath):
          os.remove(fullPath)
        return True
    
    def getExtensionFile(self,fullPath = NULL):
        if fullPath != NULL:
            return str(pathlib.Path(fullPath).suffix)
        else:
            path = str(self.nameDir)+"/"+str(self.nameFile)
            print(path)
            return str(pathlib.Path(path).suffix) 
         