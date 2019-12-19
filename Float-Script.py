#!/usr/bin/env python
# -*- coding: utf-8 -*-~

'''This script is suppose to read a bunch of .txt files
generated by a Firefox script regarding the reading of
float data from the website "hidrógrafico.pt".
It processes the file generated, saving the data that we
want and putting it into the database.'''

import os
import re
import codecs
import psycopg2
import time
from configparser import ConfigParser
from datetime import datetime

folder_name = "C:\Users\morocha\Documents\Float Data"
float_names = ["leixoes", "sines", "faro", "lisboa", "faro_oceanica", "monican01", "monican02"] 
data_array = [None] * 7
regex = re.compile(r'[\n\r\t]')
os.chdir(folder_name)

def sendDataToDatabase(float_name, float_id): #Does the actual inserts into the database.
    conn = None
    sql_query = """INSERT INTO boia_dados VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%d-%b-%Y %H:%M:%S")
    try:
        conn = psycopg2.connect(host="193.136.106.203", port="5432", database="rdfs_input", user="rdfs_run", password="")

        cur = conn.cursor()

        cur.execute(sql_query, (data_array[0], float_id, data_array[1], None, data_array[3], data_array[4], None, None, data_array[5], data_array[6], ))

        conn.commit()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def processText(line): #Gets the actual data from each line and saves it to an array.
    if("Última leitura" in line):
        new_text = regex.sub(" ", line)
        split_text = new_text.split(" ")
        data_array[0] = split_text[2] + " " + split_text[3] + ":00"
    elif("Altura significativa" in line):
        new_text = regex.sub(" ", line)
        split_text = new_text.split(" ")
        split_text = split_text[2].split("m")
        data_array[1] = split_text[0]
    elif("Altura máxima" in line):
        new_text = regex.sub(" ", line)
        split_text = new_text.split(" ")
        split_text = split_text[2].split("m")
        data_array[2] = split_text[0]
    elif("Período médio" in line):
        new_text = regex.sub(" ", line)
        split_text = new_text.split(" ")
        split_text = split_text[2].split("s")
        data_array[3] = split_text[0]
    elif("Período máx." in line):
        new_text = regex.sub(" ", line)
        split_text = new_text.split(" ")
        split_text = split_text[3].split("s")
        data_array[4] = split_text[0]
    elif("Dir. ondulação" in line):
        new_text = regex.sub(" ", line)
        split_text = new_text.split(" ")
        data_array[5] = split_text[2]
    elif("Temp. água" in line):
        new_text = regex.sub(" ", line)
        split_text = new_text.split(" ")
        split_text = split_text[2].split("º")
        data_array[6] = split_text[0]

def cleanDataArray(): #empties data between each float so there's no contamination
    for i in range(len(data_array)):
        data_array[i] = None

def getFloatId(float_name): #Returns the corresponding float it from each float.
    float_id = 0
    for i in range(len(float_names)):
        if(float_name == float_names[i]):
            float_id = i + 1
    return float_id

for file_name in os.listdir(folder_name): #For every float that exists, a file is read for each.
    try:   
        #Declaration of variables
        f = codecs.open(file_name, "r", "utf-8")
        float_name = os.path.splitext(file_name)[0]

        file_content = f.read()
        f.close() #to make sure it won't kill the computer

        string = "" #purelly for debug purposes
        count = 0 #used to check if the array has elements on it
        broken_flag = 0 #used to check if the file is ok to be submitted into the database

        if((len(file_content)) == 0): #checks if the file is corrupt
            break #corrupt file
        else:
            f = open(file_name, 'r')
            file_lines = f.readlines() #reads the file line by line
            for line in file_lines:
                if("Última leitura" in line or "Altura significativa" in line or "Altura máxima" in line or "Período médio" in line or "Período máx." in line or "Dir. ondulação" in line or "Temp. água" in line):
                    string = string + line
                    processText(line)
                elif("Hora legal" in line):
                    break #we've gotten all the data
        
        for i in range(7):
            if(data_array[i] is None):
                counter = counter + 1
        
        if(counter == 7):
            broken_flag = 1
        
        if(broken_flag == 0)
            sendDataToDatabase(float_name, getFloatId(float_name))
        
        cleanDataArray()
        f.close()
        if(os.path.exists(file_name)):
            os.remove(file_name)

#the following lines are to handle possible exception that occur within the execution of the script.
    except OSError as err:
        f.close()
    except ValueError:
        f.close()
