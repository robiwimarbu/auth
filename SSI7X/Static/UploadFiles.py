import datetime
import os
import pathlib
import hashlib

class UploadFiles():
    createDir=False
    nameDir=""
    nameFile=""
    def __init__(self, nameDir=None, nameFile=None, createDir=False):
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
            if not fileItem.filename: 
                return
            else:
                extension = self.getExtensionFile(fileItem.filename)
            
            if self.nameDir == None:
                
                return
            
            if self.createDir == True:
                if not os.path.exists(self.nameDir):
                    os.makedirs(self.nameDir)
            
            if self.nameFile == None:
                strFileName = "file_"+datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
                md5 = hashlib.md5(strFileName.encode('utf-8')).hexdigest() 
                self.nameFile = md5 + extension
            
            ruta = os.path.join(self.nameDir, self.nameFile)
            
            file = open(ruta, 'wb')    
            
            while 1:
                chunk = fileItem.read(100000)
                if not chunk: 
                    break
                
                file.write (chunk)
            
            file.close()
            return {"status":"OK","error":"","namefile":self.nameFile}
        except IOError as e:
            return {"status":"ERROR","error":e,"namefile":self.nameFile}
        
    def deleteFile(self,fullPath):
        if os.path.exists(fullPath):
            os.remove(fullPath)
        return True
    
    def getExtensionFile(self,fullPath = None ):
        if fullPath != None :
            return str(pathlib.Path(fullPath).suffix)
        else:
            path = str(self.nameDir)+"/"+str(self.nameFile)
            return str(pathlib.Path(path).suffix) 