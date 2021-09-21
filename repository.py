from image_detector import Detector
import sys
import sqlite3
import base64
import cv2
import numpy as np
from datetime import datetime

def singleton(cls):
    _instance = {}
    
    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner
    
@singleton
class Repository(object):
    def __init__(self, db_name = 'image_DB'):
        self.conn = sqlite3.connect(db_name)
        self.detector = None
        c = self.conn.cursor()
        try:
            c.execute('create table IF NOT EXISTS\
                %s(picID INTEGER PRIMARY KEY AUTOINCREMENT, \
                    picName TEXT, \
                    image_bytes BLOB, \
                    picTags TEXT, \
                    addTime TEXT)'%'pictureTable') 
            self.conn.commit()
        except Exception as e:
            print(e)
            print("Create table failed")
    
    def upload(self):
        path = None
        f = None
        while True:
            try:
                path = input('>Please enter path to image: ')
                f = open(path, 'rb')
                break
            except FileNotFoundError:
                print("File/Path does not exsite, try again")
        image_name = input('>Please enter the name of image: ')
        with f:
            Pic_byte = f.read()
            #base64 encoding
            content = base64.b64encode(Pic_byte)
            #insert binary representation of image to DB
            c = self.conn.cursor()
            sql = f"INSERT INTO pictureTable (picName, image_bytes, picTags, addTime) VALUES (?,?,?,?);"
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            c.execute(sql, (image_name, content, 'N/A', str(now)))
            self.conn.commit()
            print('Successfully uploaded ', image_name, ' @ ', now)

    def show_all(self):
        sql = f'SELECT * FROM pictureTable'
        c = self.conn.cursor()
        c.execute(sql)
        for row in c:
            print(row[0], row[1], row[3], row[4])


    def get_id(self):
        c = self.conn.cursor()
        #sql statement to fetch image from DB
        count_sql = f'SELECT COUNT(*) FROM pictureTable WHERE picName=?'
        info_sql = f'SELECT * FROM pictureTable WHERE picName=?'
        name_id_sql = f'SELECT COUNT(*) FROM pictureTable WHERE picID=?'

        image_name = None
        id = None
        cnt = 0
        while True:
            image_name = input('>Please enter the name of image: ')
            c.execute(count_sql, (image_name, ))
            #get the total number of images that have the name input by user
            cnt = c.fetchone()[0]
            #image not found
            if cnt == 0:
                print('Image does not exist, please enter again. You can use `show all` comman to list information about all images')
            #multiple image has the same name
            elif cnt > 1:
                print('The following images have the same name: ')
                c.execute(info_sql, (image_name, ))
                for row in c:
                    print(row[0], row[1], row[3], row[4])
                
                #id existes flag
                id_found = False
                #check if id in database
                while not id_found:
                    id = input('>Please enter the ID of image:')
                    c.execute(name_id_sql, (id, ))
                    counter = c.fetchone()[0]
                    if counter == 0:
                        print('image not existe, please enter id again')
                    else:
                        id_found = True
                break
            #image unique, return id
            elif cnt == 1:
                c.execute('SELECT picID FROM pictureTable WHERE picName=?', (image_name,))
                id = c.fetchone()[0]
                break

        return image_name, id         
    
    def decode(self, image_byte):
        #decode as 64 base
        str_encode=base64.b64decode(image_byte)
        #convert to open_cv readable format
        nparr = np.frombuffer(str_encode, np.uint8)
        img_decode = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img_decode

    def display(self):
        #get id from user input
        image_name, id = self.get_id()
        c = self.conn.cursor()
        c.execute('SELECT image_bytes FROM pictureTable WHERE picID=?', (id, ))
        value = c.fetchone()[0]
        #print(value)
        if value:
            img_decode = self.decode(value)
            cv2.imshow(image_name,img_decode)
            cv2.waitKey(0)            


    def delete(self):
        image_name, id = self.get_id()
        c = self.conn.cursor()
        c.execute('DELETE FROM pictureTable WHERE picID=?', (id, ))
        self.conn.commit()

    def quit(self):
        self.conn.close()
        print('Thank you for using, bye.')

    def analyze(self):
        if self.detector == None:
            print('[WARNING]Due to some limitation, this operation might take some time, please be patient.')
        if self.detector == None:
            self.detector = Detector()
        c = self.conn.cursor()
        #find ids of images that don't have a tag
        c.execute('SELECT picID, image_bytes FROM pictureTable WHERE picTags==?',('N/A',))
        
        #store ids to be update later
        ids_list = []
        tag_list = []
        for row in c:
            print('adding tags to image #', row[0])
            ids_list.append(row[0])
            img_decode = self.decode(row[1])
            tags = self.detector.get_tags(img_decode)
            tag_list.append(tags)

        #update database
        for id, tags in zip(ids_list,tag_list):
            if tags:
                tags = set(tags)
                str_tags = ','.join(tags)

                c.execute('UPDATE pictureTable \
                    SET picTags = ?  \
                    WHERE picID = ? \
                    ', (str_tags,id))

        self.conn.commit()

    def search(self):
        c = self.conn.cursor()
        category = str(input('>please enter something you want to look for: '))
        c.execute('SELECT * FROM pictureTable \
            WHERE picTags LIKE ?', ('%'+category+'%',))
        for row in c:
            print(row[0], row[1], row[3], row[4])

if __name__ == '__main__':
    print('Welcome to the image repo CLI version') 
    print('Here are the commands you may need to operate the repository:')

    print('`upload` to upload the picture you want')

    print('`show all` to list all the images information')

    print('`display` to display specific images, please follow the instructions')

    print('`delete ` to delete specific image,  please follow the instructions')

    print('`analyze` to automatically add tags to all the pictures in database, this operation may take a few moments')

    print('`search` to search the image with content you want, different categories need to be separated by columnes. example: find cat,dog')

    print('`quit` to hault the program')

    repo = Repository()
    #repo.connect()

    while True:
        command = input('>')
        if command.startswith('upload'):
            repo.upload()
        elif command.startswith('show all'):
            repo.show_all()
        elif command.startswith('display'):
            repo.display()
        elif command.startswith('delete'):
            repo.delete()
        elif command.startswith('analyze'):
            repo.analyze()
        elif command.startswith('search'):
            repo.search()
        elif command.startswith('quit'):
            repo.quit()
            break
        else:
            print('invalid command, please enter again')