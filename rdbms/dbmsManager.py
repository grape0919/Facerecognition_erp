import sys
import os
import pymysql
from jproperties import Properties
import logging
import static.staticValues as staticValues

"""db 관리 클래스"""
class DbmsManager:

    logging.basicConfig(filename=staticValues.logFilePath,level=logging.DEBUG)
    host = "HOST"
    port = "PORT"
    user = "USER"
    passwd = "PASSWORD"
    databaseName = "DB_NAME"
    
    def __init__(self):
        
        #logging.basicConfig(filename='log\\andy_error.log',level=logging.DEBUG) #logger setting
        logging.info("rdbms 정보 가져오기....")
        self.prop = Properties() #rdbms.properties 에서 properties를 읽기 위한 객체
        with open(os.path.abspath(staticValues.rdbmsPropFilePath), 'rb') as prop_file: #rdbms.properties 읽기
            self.prop.load(prop_file)

        try:
            #db 커넥션
            self.conn = pymysql.connect(host=self.prop.get(self.host).data, port=int(self.prop.get(self.port).data), user=self.prop.get(self.user).data
                                        , password=self.prop.get(self.passwd).data, db=self.prop.get(self.databaseName).data, charset='utf8')
            self.curs = self.conn.cursor()
            # self.conn.escape_string()
        except:
            logging.error("DB 연결에 실패했습니다.")
            logging.error("rdbms.properties 파일을 확인해주세요.")
            logging.error("HOST=" + self.prop.get(self.host).data)
            logging.error("PORT=" + self.prop.get(self.port).data)
            logging.error("USER=" + self.prop.get(self.user).data)
            logging.error("PASSWORD=" + self.prop.get(self.passwd).data)
            logging.error("DB_NAME=" + self.prop.get(self.databaseName).data)
            logging.error("또는 DB SERVER 상태확인 및 관리자에게 문의하세요.")
            logging.error("프로그램을 종료합니다.")

            sys.exit()

        #초기 디비 생성
        self.init_db()

    #초기 디비 생성
    def init_db(self):
        #테이블 생성 sql
        try:
            self.select_all_info()
        except:

            sql = self.get_sql_from_file(staticValues.rdbmsDir+"\\init_db.sql")
            
            if sql is not False:
                for s in sql:
                    self.curs.execute(s + ";")
            else :
                logging.error("DB TABLE 생성에 실패하였습니다.")
                logging.error("프로그램을 종료합니다.")
                sys.exit()

            self.conn.commit()
        

    #싱글 데이터 insert
    def insert_single_info(self,single):
        try:
            eid = self.getMaxId()
            values = (eid+1,)+single
            sql = 'INSERT INTO ANDY_INFORMATION(ID, IMAGE, NAME, AGE, POSITION) VALUES (%s, %s, %s, %s, %s)'

            self.curs.execute(sql,values)
            self.conn.commit()
        except Exception as e:
            logging.error(e)
            logging.error(sql)

    #싱글 데이터 삭제
    def delete_single_info(self, single):
        sql = 'DELETE FROM ANDY_INFORMATION WHERE ID = ' + single
        self.curs.execute(sql)
        self.conn.commit()

    #모든 데이터 select
    def select_all_info(self):
        sql = 'SELECT ID, NAME, AGE, POSITION, IMAGE FROM ANDY_INFORMATION'
        self.curs.execute(sql)
        result = self.curs.fetchall()

        return result

    #마지막 ID 가져오기
    def getMaxId(self):
        sql = 'SELECT MAX(ID) FROM ANDY_INFORMATION'
        try:
            self.curs.execute(sql)
            selResult = self.curs.fetchall()
            result = selResult[0][0]
            if(result==None):
                result=0
        except:
            result = 0

        return result

    #file to sql module
    def get_sql_from_file(self, filename):
        """
        Get the SQL instruction from a file

        :return: a list of each SQL query whithout the trailing ";"
        """
        from os import path

        # File did not exists
        if path.isfile(filename) is False:
            logging.error("File load error : {}".format(filename))
            return False

        else:
            with open(filename, "r") as sql_file:
                # Split file in list
                ret = sql_file.read().split(';')
                # drop last empty entry
                ret.pop()
                return ret

    def close(self):
        self.conn.close()