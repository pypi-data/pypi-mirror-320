
import os
# https 자체인증서 인증 경고 메시지 처리
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .config.wp import getConfig
from .wpType import WpStorage
from .hdfsService import webHdfs

#with open('./log/logging.json', 'rt') as f:
#    config = json.load(f)
#logging.config.dictConfig(config)

#o_logger = logging.getLogger('LOCAL')

class WiseStorageManager(WpStorage):
    def __init__(self, p_userno, p_type=getConfig('','STORAGE_TYPE'), p_path='', p_extra=None):
        print("WiseStorageManager p_extra : ", p_extra)
        # HDFS Client
        # HDFS IP, PORT 변경 반영
        self.o_wpStorage = None
        self.o_userno = p_userno
        self.dbinfo = getConfig('','META_DB')

        if p_path == '' :
            self.o_rootPath = getConfig('','DEFAULT_DATA_PATH')
        else :
            self.o_rootPath = p_path

        self.o_storageType = p_type

        if p_type == 'HDFS':
            self.o_wpStorage = webHdfs(p_userno ,self.o_rootPath)
        else :
            self.o_wpStorage = webHdfs(p_userno,self.o_rootPath)


    def createBuffer(self, p_path, p_option='rb', p_encType ='utf-8'):
        '''
        Buffer 읽기 
        p_path: 파일 경로
        p_option :  'r' : open for reading (default)
                    'w' : open for writing, truncating the file first
                    'x' : open for exclusive creation, failing if the file already exists
                    'a' : open for writing, appending to the end of file if it exists
                    'b' : binary mode
                    't' : text mode (default) 
                    '+' : open for updating (reading and writing)
        p_encType: 인코딩 타입
        '''
        s_cloudTF = getConfig('','CLOUD')
        if any(idx in p_option for idx in ['w', 'a', 'x']) and s_cloudTF:
            self.checkUserDirSize()
        return self.o_wpStorage.createBuffer(self.o_rootPath + p_path,p_option,p_encType)

    def getPath(self):
        return self.o_rootPath
    
    def moveFile(self, p_target, p_newPath):
        '''
        파일 이동
        p_target: 원래 경로
        p_newPath: 이동할 경로
        '''
        s_deleteFlag = self.checkExist(p_newPath)
        if s_deleteFlag:
            self.o_wpStorage.removeFile(self.o_rootPath + p_newPath)

        return self.o_wpStorage.moveFile(self.o_rootPath + p_target, self.o_rootPath + p_newPath)

    #175 HDFS 파일 읽기 (워크플로우에서 파일 쓸 때 utf-8 포맷으로 해서  default encType = utf-8 )
    def readFile(self, p_path, p_option='read', p_mode='r', p_readsize=0, p_encType ='utf-8', p_sep=',',p_fullPath=False):
        '''
        LOCAL 파일 읽기 
        p_path: 파일 경로
        p_option: read option(read, readline, csv, parquet)
        p_mode: open mode(r, rb...) - 현재 local만 사용
        p_readsize: p_option이 'read'일 때 read_size. 0 일 경우 전체 파일 읽음
        p_encType: 인코딩 타입 (현재 local만 세분화 되어있음.)
        p_sep: 구분자
        p_fullPath: (p_path의) o_rootPath 포함여부
        '''
        try:
            s_path = self.o_rootPath + p_path
            if p_fullPath:
                s_path = p_path
            s_df = self.o_wpStorage.readFile(s_path, p_option, p_mode, p_readsize, p_encType, p_sep)
            return s_df

        except Exception as ex:
            print(ex)
            raise

    def removeFile(self, p_target, p_recursive=False):
        '''
        파일 삭제
        p_target: 파일 경로
        p_recursive: 내부 파일까지 삭제하는지
        '''
        try:
            return self.o_wpStorage.removeFile(self.o_rootPath + p_target,p_recursive)
        except Exception as ex:
            print(ex)
            # o_logger.info('######## readFile Error ########')
            # _LoggerConfiguration.info(ex)
            raise
        

    def readView(self, p_viewName):
        '''
        p_viewName: 뷰 이름
        '''
        try:
            return self.o_wpStorage.readView(p_viewName)
        except Exception as ex:
            print(ex)
            # o_logger.info('######## readView Error ########')
            # o_logger.info(ex)
            raise

    def createView(self, p_viewName, p_df, p_option='csv', p_index=False, p_encType ='utf-8', p_writeMode='w'):
        '''
        View 생성 
        p_viewName: 뷰 네임
        p_df: 데이터프레임
        p_option: write option(csv, parquet, h5, pkl)
        p_index: index 저장 option
        p_encType: 인코딩 타입
        p_writeMode: write mode (w, a, ...)
        '''
        try:
            return self.o_wpStorage.createView(p_viewName, p_df, p_option)
        
        except Exception as ex:
            print(ex)
            # o_logger.info('######## createView Error ########')
            # o_logger.info(ex)
            raise
    #175 HDFS 파일 쓰기
    def writeFile(self, p_path, p_df, p_option='csv', p_index=False, p_encType ='utf-8', p_writeMode='w'):
        '''
        파일 쓰기 
        p_path: 파일 경로
        p_df: 데이터프레임
        p_option: write option(csv, parquet, h5, pkl)
        p_index: index 저장 option
        p_encType: 인코딩 타입
        p_writeMode: write mode (w, a, ...)
        '''

        try :
            s_cloudTF = getConfig('','CLOUD')
            if s_cloudTF:
                self.checkUserDirSize()
            return self.o_wpStorage.writeFile(self.o_rootPath + p_path, p_df, p_option, p_index, p_encType, p_writeMode)        

        except Exception as ex:

            print("ex : ", ex)
            # o_logger.info('######## writeFile Error ########')
            # o_logger.info(ex)
            raise
        
    # 파일 존재 체크 여부 
    def checkExist(self, p_path):
        s_existFlag = self.o_wpStorage.checkExist(self.o_rootPath + p_path)    
        return s_existFlag

    #175 LOCAL 경로 생성
    def createDirs(self, p_path,p_fullPath=False):
        '''
        LOCAL 경로 생성
        p_path: 파일 경로
        p_fullPath: (p_path의) o_rootPath 포함여부
        '''
        s_path = self.o_rootPath + p_path
        if p_fullPath:
            s_path = p_path
        self.o_wpStorage.createDirs(s_path)

    # LOCAL 경로 삭제
    def deleteDirs(self, p_path):
        '''
        LOCAL 경로 생성
        p_path: 파일 경로
        '''
        self.o_wpStorage.deleteDirs(self.o_rootPath + p_path)        
    
    def listFile(self, p_path, p_status=False):
        '''
        LOCAL 파일 리스트
        p_path: 파일 경로
        p_status: Also return each file's corresponding FileStatus
        '''
        return self.o_wpStorage.listFile(self.o_rootPath + p_path,p_status)
        
    # 모델 저장
    def saveModel(self, p_path, p_df, p_option='pkl', p_tmpModel=False):
        '''
        p_path: 파일 경로
        p_df: 모델파일
        p_option 모델 확장자
        p_tmpModel: hdfs && h5일 경우 local에 임시 모델 저장하기 위해 추가
        '''
        try:
            s_cloudTF = getConfig('','CLOUD')
            if s_cloudTF:
                self.checkUserDirSize()
                
            s_path = self.o_rootPath + p_path
            if p_tmpModel:
                s_path = p_path
            # HDFS의 경우 keras sequential 모델을 h5로 변환할 수 없어  local에 임시 저장후 hdfs에 복사
            if p_option == 'h5' and self.o_storageType == 'HDFS':
                s_path = 'py_result/' + p_path
                s_wiseStorage = WiseStorageManager(self.o_userno,'LOCAL')
                s_folderPath = os.path.split(s_path)
                s_wiseStorage.createDirs(s_folderPath[0],True)
                s_wiseStorage.saveModel(s_path, p_df, p_option, p_tmpModel=True)
                s_path = p_path
            elif p_option == 'gpt' and self.o_storageType == 'HDFS':
                s_path = 'py_result/' + p_path
                s_wiseStorage = WiseStorageManager(self.o_userno,'LOCAL')
                s_folderPath = os.path.split(s_path)
                s_wiseStorage.createDirs(s_folderPath[0],True)
                s_wiseStorage.saveModel(s_path, p_df, p_option, p_tmpModel=True)
                s_path = p_path

            s_output = self.o_wpStorage.saveModel(s_path, p_df, p_option)
            return s_output

        except Exception as ex:
            print(ex)
            # o_logger.info('######## saveModel Error ########')
            # o_logger.info(ex)
            raise
            
    # 모델 로드 
    def loadModel(self, p_path, p_option='pkl'):
        '''
        p_path: 파일 경로
        p_option 모델 확장자
        '''
        try:
            s_path = self.o_rootPath + p_path
            if p_option=='h5' and self.o_storageType == 'HDFS':
                s_wiseStorage = WiseStorageManager(self.o_userno,'LOCAL')
                s_folderPath = os.path.split('py_result/' + p_path)
                s_wiseStorage.createDirs(s_folderPath[0],True)
                s_path = p_path
            s_output = self.o_wpStorage.loadModel(s_path, p_option)
            return s_output

        except Exception as ex:
            print(ex)
            # o_logger.info('######## loadModel Error ########')
            # o_logger.info(ex)
            raise
        
    def getDirSize(self, p_path):
        '''
        p_path: 파일 경로
        '''
        return self.o_wpStorage.getDirSize(self.o_rootPath + p_path)    
    
    # dir check && hdd 비교 코드 추가
    # 각 service에 dirsize 코드(local 외에는 true, 0)
    def checkUserDirSize(self):
        '''
        user dir size check(aws-market)
        '''
        return True
       
    def bytesToSize(self, p_bytes:int, p_sep=""):
        import math
        if p_bytes == 0:
            return f'0{p_sep}Bytes'
        s_sizeName = ("Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(p_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(p_bytes / p, 2)
        
        return f'{s}{p_sep}{s_sizeName[i]}'
    
    def sizeToBytes(self, p_size:str, p_sep=""):
        import math
        s_sizeName = ("Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        s_size = p_size
        s_idx = 0
        for idx, val in enumerate(s_sizeName):
            if val in p_size:
                s_size = s_size.split(p_sep+val)[0]
                s_idx = idx
        
        return float(s_size)*(1024** s_idx)

    # Owner
    def setOwner(self, p_path, p_user):
        print("path")
        s_result = self.o_wpStorage.setOwner(f"{self.o_rootPath}{p_path}", p_user)    
