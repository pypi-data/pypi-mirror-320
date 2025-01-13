# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 14:02:55 2024

The programs make use of MongoDB as agent to record the heartbeat of
certain app. The object are meant to run in 2 cases:
    (1) Part of a endless loop routine
    (2) Additional process or thread spawn from main process

This program only "drop a beat". i.e. other program need to check the
heartbeat signature for monitoring purpose.

@author: yangl
"""
from neuondb import neuondb
from neuon.neuon_utils import print_debug as print
from neuon.neuon_utils import enable_debug_print
import os
import json
from bson.objectid import ObjectId
from datetime import datetime

# seconds, slightly longer than intented time. i.e. if 5 minutes is the
# expiry target, put 6 minutes for the threshold for creating new session
NEW_SESSION_THRESHOLD = 360 

COLL = {}
COLL['heartbeat'] = 'heartbeat'

class heartbeat(object):
    def __init__(self,
                 name:str,
                 heart_type:str,
                 db_uri:str,
                 db_name:str,
                 new_session_threshold:int=NEW_SESSION_THRESHOLD):
        """
        Hearbeat object class init the object with MongoDB details

        Parameters
        ----------
        name : str
            name of the app to generate heartbeat.
        heart_type : str
            type of the heartbeat.
        db_uri : str
            MongoDB URI.
        db_name : str
            Database name to save the heartbeat. Default collection name
            is 'heartbeat'

        Returns
        -------
        None.

        """
        self.db = neuondb(
            uri = db_uri,
            dbname = db_name)
        
        self.name = name
        self.agent_name = self.db.user['username'] # mongo user
        self.heart_type = heart_type

        self.new_session_threshold = new_session_threshold

        self.dir_path = os.path.split(os.path.dirname(
            os.path.realpath(__file__)))[0]
        self.data_path = os.path.join(self.dir_path,'data')
        
        self._load_app_id()
                        
    def _load_app_id(self):      
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
            
        heartbeat_id_path = os.path.join(self.data_path,f'{self.name}.json')
        if not os.path.exists(heartbeat_id_path):
            with open(heartbeat_id_path,'w') as jfid:
                json.dump(
                    {
                        "app_id":str(ObjectId())
                        },
                    jfid, indent = 6
                    )        
        try:
            with open(heartbeat_id_path,'r') as jfid:
                data = json.load(jfid)
                print(data)
        except json.JSONDecodeError:
            print('JSON format is not correct')
            raise Exception(f"{heartbeat_id_path}:JSON format not correct. Delete the file to generate new app_id or provide the correct formatted file")
            
        self.app_id = data.get('app_id',None)
        if self.app_id is None:
            raise Exception(f"{heartbeat_id_path}: File does not content app_id. Delete the file to generate new app_id or provide the correct formatted file")
        
    def drop_a_beat(self):
        """
        Drop a heartbeat signal to MongoDB

        Returns
        -------
        None.

        """
        ret = self.db.get_record(COLL['heartbeat'],
                                 {"app_id":ObjectId(self.app_id)},
                                 {"_id":1, "updatedAt":1, "createdAt":1},
                                 ("createdAt",-1),limit=1)
        
        print(ret)
        if len(ret) > 0:
            latest_heartbeat = ret[0]
            updated_time = latest_heartbeat.get("updatedAt",None)
            created_time = latest_heartbeat.get("createdAt",None)
            elapsed = 0
            if updated_time is not None:
                elapsed = (self.db.timezone_aware(datetime.now()) - updated_time).seconds
            else:
                if created_time is not None:
                    elapsed = (self.db.timezone_aware(datetime.now()) - created_time).seconds
                else:
                    print("Field createdAt is missing from document, invalid format")
                    self.create_new_session() 
                                        
            print(f"Elapsed time since last heartbeat {elapsed} second(s)") 
            if elapsed > 0:
                if elapsed > self.new_session_threshold:
                    self.create_new_session()
                else:
                    self.update_session(latest_heartbeat['_id'])                                
        else:
            print(f'No record(s) found for app_id {self.app_id}')            
            self.create_new_session()
            
    def create_new_session(self):
        """
        Create a new session with same app_id

        Returns
        -------
        bool
            If new session successfuly created.

        """
        ret = self.db.insert_record(COLL['heartbeat'], 
                              {
                                  "app_id": ObjectId(self.app_id),
                                  "name" : self.name,
                                  "heart_type" : self.heart_type,
                                  "createdBy" : self.agent_name
                                  })
        
        if ret is not None:
            print(f'New session {ret.inserted_id} created')
            return True
        else:
            print('Session creation FAILED')
            return False
        
    def update_session(self,session_id):
        """
        Update the current session_id field : updateAt to current time

        Parameters
        ----------
        session_id : ObjectId
            The session object id to update.

        Returns
        -------
        bool
            If the session is updated.

        """
        ret = self.db.update_record(COLL['heartbeat'], 
                                    session_id, 
                                    {})
        
        if ret is not None:
            print(f'Session {session_id} updated')
            return True
        else:
            print(f'Session {session_id} update FAILED')
            return False
        
if __name__ == '__main__':
    enable_debug_print()
    
    hb = heartbeat(
        name = 'heartbeat_main',
        heart_type = 'daemon',
        db_uri = os.environ.get('MONGO_URI'),
        db_name = "aidoc"
        )
    
    hb.drop_a_beat()
    