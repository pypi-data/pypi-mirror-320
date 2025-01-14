
from .wpType import WpStorage
import requests
from hdfs import Client
import base64
import pandas as pd
import joblib
import shutil
import pickle
import yaml
import os


# https 자체인증서 인증 경고 메시지 처리
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dask import dataframe as dd
from .config.wp import getConfig

# with open('./log/logging.json', 'rt') as f:
#     config = json.load(f)
# logging.config.dictConfig(config)

# o_logger = logging.getLogger('WebHdfs')
o_rootPath = getConfig('','DEFAULT_DATA_PATH')

class webHdfs(WpStorage):
    def __init__(self, p_userno, p_rootPath=o_rootPath):
        # HDFS Client
        # HDFS IP, PORT 변경 반영
        self.hdfs_port = getConfig('WEB_HDFS', 'port')
        self.hdfs_web_port = getConfig('WEB_HDFS', 'port')
        self.hdfs_ip = getConfig('WEB_HDFS', 'host')
        self.hdfs_user = getConfig('WEB_HDFS', 'hadoop-id')
        self.hdfs_url = f'https://{self.hdfs_ip}:{self.hdfs_port}/gateway/sandbox'
        self.s = requests.Session()
        self.s.verify = False
        self.authToken = ''
        self.o_rootPath = p_rootPath
        self.dbinfo = getConfig('','META_DB')
        print(self.hdfs_url)
        
        self.authToken = "Basic " + str(base64.b64encode(f"root:0261ea1f8edf2d6bfbc0497d002f2f9bd9471f2c".encode('utf8'))).replace("b'","").replace("'","")
        self.s.headers.update({
            'Content-Type': "application/json",
            'Authorization': self.authToken,
            'rejectUnauthorized': 'False',
        })

        print(self.hdfs_url)
        # client_hdfs = InsecureClient(f'https://{hdfs_ip}:{hdfs_port}', user='root',session=s)
        self.client_hdfs = Client(url=self.hdfs_url, root=self.hdfs_user,session=self.s)

    def setOwner(self,p_filepath,p_userId):

        try:
            self.client_hdfs.set_owner(p_filepath,  owner=p_userId, group='wise')
            return True

        except Exception as ex:
            print(ex)
            # o_logger.info('######## createDirs Error ########')
            # o_logger.info(ex)
            raise

    def getPath(self):
        return self.o_rootPath
        
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
        return open(p_path,p_option,p_encType)        
    #175 HDFS 파일 읽기 (워크플로우에서 파일 쓸 때 utf-8 포맷으로 해서  default encType = utf-8 )
    def readFile(self, p_path, p_option='read', p_mode='r', p_readsize=0, p_encType ='utf-8', p_sep=','):
        print("hdfs readFile : ", p_path)
        '''
        HDFS 파일 읽기 
        p_path: 파일 경로
        p_option: read option(read, readline, csv, parquet)
        p_mode: open mode
        p_readsize: p_option이 read일 때 read_size. 0 일 경우 전체 파일 읽음
        p_encType: 인코딩 타입
        '''
        # 경고 LOG가 너무 많이 나오기에 이부분은 변경
        # s_logger = logging.getLogger()
        # s_logger.setLevel(logging.WARN)
        try:
            if p_option == 'read':
                with self.client_hdfs.read(p_path) as rawdata:
                    if p_readsize > 0 :
                        s_df = rawdata.read(p_readsize)
                    else :
                        s_df = rawdata.read()
                    rawdata.close()
            if p_option == 'readline':
                with self.client_hdfs.read(p_path) as rawdata:
                    s_df = rawdata.readline()
                    rawdata.close()
            if p_option == 'readlines':
                with self.client_hdfs.read(p_path) as rawdata:
                    s_df = rawdata.readlines()
                    rawdata.close()
            if p_option == 'csv':
                with self.client_hdfs.read(p_path, encoding = p_encType) as reader:
                    try :
                        s_df = pd.read_csv(reader, engine='python', encoding = p_encType,  on_bad_lines='skip')
                    except Exception as ex:
                        s_df = pd.read_csv(reader, engine='python', encoding = p_encType, error_bad_lines=False) 
                    reader.close()
            if p_option == 'parquet':
                print("hdfs_ip : ", self.hdfs_ip)
                # s_daskDf = dd.read_parquet(f'webhdfs://{self.hdfs_ip}:{self.hdfs_web_port}{p_path}',engine='pyarrow', split_row_groups=100000)
                s_daskDf = dd.read_parquet(f'hdfs://{p_path}',engine='pyarrow', split_row_groups=100000)
                s_df = s_daskDf.compute()
                s_df = s_df.reset_index(drop=True)
                del s_daskDf
            if p_option == 'yaml':
                with self.client_hdfs.read(p_path, encoding = p_encType) as reader:
                    s_df = yaml.load(reader, Loader=yaml.SafeLoader)
            if p_option == 'txt':
                with self.client_hdfs.read(p_path, encoding = p_encType) as reader:
                    s_df = reader.read()
                    reader.close()

            return s_df
        except Exception as ex:            
            print(ex)
            # s_logger.info('######## readFile Error ########')
            # s_logger.info(ex)
            raise

    #175 HDFS 파일 쓰기
    def writeFile(self, p_path, p_df, p_option='csv', p_index=False, p_encType ='utf-8', p_writeMode='w'):
        '''
        HDFS 파일 쓰기 
        p_path: 파일 경로
        p_df: 데이터프레임
        p_option: write option(csv, parquet, h5, pkl, yaml)
        p_index: index 저장 option
        p_encType: 인코딩 타입
        p_writeMode: write mode (w, a, ...)
        '''
        s_header = True
        s_overwrite = True
        s_append = False
        # 모드가 append이고 csv저장일 경우. 최초파일이 있는지 없는지 체크해서 설정
        if p_writeMode == 'a' and p_option == 'csv':
            s_exist = self.client_hdfs.content(p_path, strict=False)
            if s_exist != None:
                s_header = False
                s_overwrite = False
                s_append = True

        try:
            if p_option == 'csv':
                with self.client_hdfs.write(p_path, encoding=p_encType, overwrite=s_overwrite, append=s_append) as writer:
                    p_df.to_csv(writer, index=p_index, header=s_header, encoding=p_encType, mode = p_writeMode)
            elif p_option == 'parquet':
                # WP-126 to_parquet 적용시 문자/숫자 섞여있는 object 컬럼 str 타입으로 명시해야 함.
                for col in p_df.columns:
                    if str(p_df[col].dtype) == 'object':
                        p_df[col] = p_df[col].astype(str)
                p_df = p_df.to_parquet(index=p_index)
                self.client_hdfs.write(p_path, data=p_df, overwrite=True, blocksize=1048576)
            elif p_option == 'h5':
                self.client_hdfs.write(p_path, data=p_df, overwrite=True)
            elif p_option == 'pkl':
                with self.client_hdfs.write(p_path, overwrite=True) as writer:
                    joblib.dump(p_df, writer)
            elif p_option == 'yaml':
                with self.client_hdfs.write(p_path, overwrite=True) as writer:
                    yaml.dump(p_df, writer,
                              encoding = p_encType,
                              default_flow_style=False,
                              allow_unicode=True,
                              sort_keys=True,
                              Dumper=yaml.SafeDumper)
            elif p_option == 'pdf':
                with self.client_hdfs.write(p_path, overwrite=True) as writer:
                    p_df.write_pdf(writer)
            elif p_option == 'txt':
                self.client_hdfs.write(p_path, data=p_df, overwrite=True, encoding=p_encType)

            else :
                if p_writeMode == 'a':
                    s_append = True
                    s_overwrite = False
                self.client_hdfs.write(p_path, data=p_df,append=s_append, encoding=p_encType, overwrite=s_overwrite)
            return True
        
        except Exception as ex:
            print("ex", ex)
            # o_logger.info('######## writeFile Error ########')
            # o_logger.info(ex)
            raise
        
    def isDir(self, p_path):
        '''
        유효한 경로인지 확인 
        p_path: 폴더 경로
        '''
        try:
            s_status = self.client_hdfs.status(p_path, strict=None)
            if s_status is not None and s_status['type'] == 'DIRECTORY' : 
                return True
            else :
                return False
        # 경로가 아니면 예외 발생함.
        except Exception as e:
            raise
    
    def getFileInfo(self, p_path):
        '''
        파일 정보 확인
        p_path: 파일 경로
        '''
        try:
            s_fileInfo = self.client_hdfs.status(p_path, strict=None)
            if s_fileInfo is not None and s_fileInfo['type'] == 'FILE' : 
                return s_fileInfo
            else :
                return False
        # 경로가 아니면 예외 발생함.
        except Exception as e:
            raise
        
    # 파일 존재 체크 여부 
    def checkExist(self, p_path):
        s_existFlag = False
        s_check = self.client_hdfs.content(p_path, strict=False)
        if s_check != None:
            s_existFlag = True
    
        return s_existFlag

    #175 HDFS 경로 생성
    def createDirs(self, p_path):
        '''
        HDFS 경로 생성
        p_path: 파일 경로
        '''
        s_Flag = True
        # makedirs - 중간 경로 폴더 자동 생성
        # e이미 경로 존재하는 경우 에러 발생하지 않고 넘어감(덮어쓰기 하지않음)
        try:
            s_create = self.client_hdfs.makedirs(p_path, permission=755)
            if s_create != None:
                s_Flag = False
            return s_Flag
        except Exception as ex:
            print(ex)
            # o_logger.info('######## createDirs Error########')
            # o_logger.info(ex)
            raise
        # s_existFlag = self.checkExist(p_path)
        # if s_existFlag == False:
        #     self.client_hdfs.makedirs(p_path, permission=755)
    
    # LOCAL 경로 삭제
    def deleteDirs(self, p_path):
        try:
            shutil.rmtree(p_path, ignore_errors=True)
            return True
        except Exception as ex:
            print(ex)
            # o_logger.info('######## deleteDirs Error########')
            # o_logger.info(ex)
            raise
        
    def listFile(self, p_path, p_status=False):
        '''
        HDFS 파일 리스트
        p_path: 파일 경로
        p_status: Also return each file's corresponding FileStatus
        '''
        listResult = None
        if p_status:
            listResult = self.client_hdfs.list(p_path, p_status)
        return listResult
    
    # 모델 저장 
    def saveModel(self, p_path, p_df, p_option='pkl'):
        '''
        p_path: 파일 경로
        p_option 모델 확장자
        '''
        try:
            if p_option == 'h5' or p_option == 'gpt':
                # from pyarrow import fs    
                self.client_hdfs.upload(self.getPath()+p_path, 'py_result/'+p_path)
            if p_option == 'pkl':
                with self.client_hdfs.write(p_path, overwrite=True) as writer:
                    pickle.dump(p_df, writer)
                # hdfs = PyWebHdfsClient(host=self.hdfs_ip,port=self.hdfs_port,base_uri_pattern=self.hdfs_url+'/webhdfs/v1/', user_name=self.hdfs_user,
                #                        request_extra_opts={"verify":False,'auth': ('root', '0261ea1f8edf2d6bfbc0497d002f2f9bd9471f2c')})
                # model_pickle = pickle.dumps(p_df)
                # hdfs.create_file(p_path, model_pickle, overwrite=True)                
            return True     
        
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
            if p_option == 'h5':
                from tensorflow.keras.models import load_model
                self.client_hdfs.download(self.getPath()+p_path,'py_result/'+p_path,overwrite=True)
                s_output = load_model('py_result/'+p_path) 
                # with self.client_hdfs.read(p_path) as reader:
                #     # with h5py.File('py_result/1194/pkl/'+os.path.split(p_path)[1], "r") as h5file:                 
                #     # s_output = load_model(h5file)                 
                #     s_output = load_model(reader.data)
                #     # print(h5file.keys())
                #     # h5file.close()

            if p_option == 'pkl':
                with self.client_hdfs.read(p_path) as reader:
                    s_output = pickle.loads(reader.data)
                # hdfs = PyWebHdfsClient(host=self.hdfs_ip,port=self.hdfs_port,base_uri_pattern=self.hdfs_url+'/webhdfs/v1/', user_name=self.hdfs_user,
                #                        request_extra_opts={"verify":False,'auth': ('root', '0261ea1f8edf2d6bfbc0497d002f2f9bd9471f2c')})
                # pickled_model = hdfs.read_file(p_path)
                # s_output = pickle.loads(pickled_model)

            return s_output     
        
        except Exception as ex:
            print(ex)
            # o_logger.info('######## loadModel Error ########')
            # o_logger.info(ex)
            raise
        
    def removeFile(self, p_target, p_recursive=False):
        '''
        파일 삭제
        p_target: 파일 경로
        p_recursive: 내부 파일까지 삭제하는지
        '''
        self.client_hdfs.delete(p_target, p_recursive)
        
    def moveFile(self, p_target, p_newPath):
        '''
        파일 이동
        p_target: 원래 경로
        p_newPath: 이동할 경로
        '''
        s_deleteFlag = self.checkExist(p_newPath)
        if s_deleteFlag:
            self.removeFile(p_newPath)

        self.client_hdfs.rename(p_target, p_newPath)

    def getAbsPath(self, p_path):
        '''
        절대 경로 반환
        p_target: 파일 경로
        '''
        s_absPath = self.client_hdfs.resolve(p_path)
        return s_absPath
    
    def getRelPath(self, p_path, p_start):
        '''
        상대 경로 반환
        p_path: 상대 경로 대상 path
        p_start: 상대 경로를 계산할 출발 path
        '''
        s_path = self.getAbsPath(p_path)
        s_start = self.getAbsPath(p_start)
        s_relpath = os.path.relpath(s_path, s_start)
        return s_relpath
    
    def getDirSize(self, p_path):
        '''
        p_path: 파일 경로
        '''
        try:            
            size = 0            
            return size

        except Exception as ex:
            print(ex)
            # o_logger.info('######## getDirSize Error########')
            # o_logger.info(ex)
            raise
