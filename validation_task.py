from pathlib import Path, PurePath
import sys
from yaml import YAMLError
import pika
import sys
import json
from uuid import uuid4
from rabbitmq_connection.task_consumer import Connection_maker
from common.yaml_parser import parse_yaml_config


def format_task_message(files_info:list, recipients:list):
    task_message = {
        'task' : 'Validation',
        'files_info' : files_info,
        'result_recipients' : list(recipients)
    }
    return json.dumps(task_message)

def make_task(channel, queue, task_message):
    print(task_message)
    channel.basic_publish(
        exchange='',
        routing_key= queue,
        properties= pika.BasicProperties(correlation_id=str(uuid4)),
        body=task_message
    )


    
def interface():
    print("Hello, now you can define what will be validated and where will output be send")
    ask_data = True
    list_of_files_info = set()
    list_of_rec_emails = set()
    while(ask_data):
        list_of_files_info.update(input_file_info())
        list_of_rec_emails.update(input_recipients())
        ask_data = validate_input(
            list_of_files_info ,list_of_rec_emails
            )
        answare = input("do you want to input more data[y/n]")
        if answare == "y":
            ask_data = True

    return list_of_files_info, list_of_rec_emails    
    
    

def validate_input(files_info, rec_emails):
    
    if len(files_info)==0: 
        print("there has to be at least one file to validate")
        return True
    if len(rec_emails) ==0:
        print("there has to be at least one recipient")
        return True
    return False


def input_file_info():
    repeatQuestion = True
    list_of_info = set()
    while(repeatQuestion):
        answer_f = input("Do you want to load info from file [y/n]: ")
        if answer_f == "y":
            try:
                list_of_info = get_file_info_from_file()
                repeatQuestion =False
            except (YAMLError, EnvironmentError) as e:
                print("Error with loading data from file",e)               
                
        elif answer_f == "n":
            list_of_info = manual_input_of_file_info()
            repeatQuestion =False
    return list_of_info

def input_recipients():
    repeatQuestion = True
    list_of_info = set()
    while(repeatQuestion):
        answer_f = input("Do you want to load emails from file [y/n]: ")
        if answer_f == "y":
            try:
                list_of_info = get_recipients_from_file()
                repeatQuestion= False
            except EnvironmentError as e:
                print("Error with loading data from file",e)   
        elif answer_f == "n":
            list_of_info = manual_input_of_reciepent()   
            repeatQuestion= False         
    return list_of_info

        

def get_file_info_from_file():
    fileInfo_path = input("Please input path to yamlfile with files info: ")
    file_info_yaml = parse_yaml_config(fileInfo_path)
    return parse_yamlData_to_list(file_info_yaml)

def parse_yamlData_to_list(file_info_yaml):
    list_data = set()
    list_data.update(file_info_yaml["files_id"])
    for file in file_info_yaml["files"]:
        list_data.add(tuple([
            file["file_name"],
            file["file_owner"]
        ]))
    return list_data


def get_recipients_from_file():
    rc_path = input("Please input path to file with recipients: ")
    email_list = set()
    with open(rc_path,'r') as f:
        lines= f.readlines()
    for em in lines: 
        email_list.add(em.replace("\n",""))
    
    return email_list 


def manual_input_of_file_info():
    list_file_info = set()
    repeat= True
    while(repeat is True):
        try:
            number_of_files = int(input("then please input number of files to be validated: "))
            for x in range(number_of_files): 
                fileID = input("please input file ID: ")
                if not fileID.isdigit() :
                    fileOwner = input("please input file Owner: ") 
                    fileName = input("please input file Name: ")
                    list_file_info.add(tuple([fileOwner,fileName]))
                    continue
                list_file_info.add(fileID)
                
            repeat= False
        except ValueError:
            print("please input just number")
            
    return list_file_info

def manual_input_of_reciepent():
    list_file_info = set()
    answer= False
    while(answer is False):
        try:
            number_of_files = int(input("then please input number of result reciepients: "))
        except ValueError:
            print("please input just number")
            continue
        answer= True
    for x in range(number_of_files):            
        email = input("please input email: ")
        list_file_info.add(email)   
    return list_file_info

def raise_system_exit():
    raise SystemExit(
        f"Usage: {sys.argv[0]} (-c | --config) <path to yaml config for Rabbitmq connection>"
        )

def parse_arguments(args):
    if not (len(args) == 2):
        raise_system_exit()

    config_path = None
    if args[0] == '-c' or args[0] == '--config':
        config_path = Path(args[1])
    else: 
        raise_system_exit() 
    return config_path

def main():
    
    config_path = parse_arguments(sys.argv[1:])    
    parsed_config = parse_yaml_config(config_path)
    files_info, recipients = interface()
    c_maker = Connection_maker(parsed_config.get('rabbitmq_connection'))
    
    connection = c_maker.make_connection()
    channel = connection.channel()


    for file_i in files_info:
        make_task(
            channel,
            parsed_config['rabbitmq_info'].get('task_queue'),
            format_task_message(file_i, recipients)
        ) 
    channel.close()
    connection.close()
    
    print("Everything has been done successfully, results will be in recipients email box")

if __name__ == '__main__':
    main()




