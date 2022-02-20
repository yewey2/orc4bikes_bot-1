import os
import json
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError
from torch import exp_

ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
REGION_NAME = os.environ.get('REGION_NAME')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        super().default(obj)  # Let the json module throw the error

def float_to_decimal(obj):
    """DynamoDB require Decimal in place of float"""
    return json.loads(json.dumps(obj, cls=DecimalEncoder), parse_float=Decimal)

def decimal_to_float(obj):
    return json.loads(json.dumps(obj, cls=DecimalEncoder))

def ensure_no_floats(obj):
    if isinstance(obj, bool) or obj is None:
        return True
    if isinstance(obj, (str, int, Decimal)):
        return True
    if isinstance(obj, dict):
        return ensure_no_floats([(k,v) for k,v in obj.items()])
    if isinstance(obj, (tuple, list)):
        return all([ensure_no_floats(e) for e in obj])
    print(f"Warning: Unknown object found: {obj}")


def create_users_table(dynamodb=None):
    """Creates users table if it doesn't exist"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )
    try:
        table = dynamodb.create_table(
            TableName='users',
            AttributeDefinitions=[
                {
                    'AttributeName': 'chat_id',
                    'AttributeType': 'N'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'chat_id',
                    'KeyType': 'HASH'  
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        return table
    except ClientError:
        return None
    finally:
        return None

def get_user_data(chat_id=None, dynamodb=None):
    """Getting user data as a dictionary"""
    if not chat_id:
        return None
    # create_users_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )
    table = dynamodb.Table('users')
    response = None
    try:
        response = table.get_item(Key={'chat_id': chat_id})['Item']
        response = decimal_to_float(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    except KeyError as e:
        print('Key Error! Item not found')
        print(e)
    finally:
        return response

def set_user_data(chat_id=None, user_data={}, dynamodb=None):
    """Updating single user's data"""
    print("bef")
    print(repr(user_data))
    print()
    user_data = float_to_decimal(user_data)

    ensure_no_floats(user_data)

    print("aft")
    print(repr(user_data))
    print()
    
    
    input("Okay, no floats alr, press enter to continue")
    if not chat_id:
        return None
    # create_users_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )
    table = dynamodb.Table('users')
    response=None

    def keywords(k, a=""):
        if k=="status":
            k= a+"s"
        if k=="username":
            k= a+"u"
        if k=="bike_name":
            k= a+"bn"
        if k=="first_name":
            k= a+"fn"
        if k=="last_name":
            k= a+"ln"
        if k=="log":
            k= a+"l"
        return k

    exp_attr_val = {f':{keywords(k)}':v for k,v in user_data.items() if k!="chat_id"}
    update_exp = 'set ' + ', '.join([f'{keywords(k,"#")}=:{keywords(k)}' for k in user_data.keys() if k!="chat_id"])
    exp_attr_name = {
        '#s':'status',
        '#u':'username',
        '#fn':'first_name',
        '#ln':'last_name',
    }
    if 'bike_name' in user_data.keys():
        exp_attr_name['#bn']='bike_name'
    if 'log' in user_data.keys():
        exp_attr_name['#l']='log'
        
    print("expattrval")
    print(exp_attr_val)
    print()
    print("updateexp")
    print(update_exp)
    print()
    
    try:
        input("Press enter to try dynaoming")
        response = table.update_item(
            Key={
                'chat_id': chat_id,
            },
            UpdateExpression=update_exp,
            ExpressionAttributeValues=exp_attr_val,
            ExpressionAttributeNames=exp_attr_name,
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        print('error', e.response['Error']['Message'])
    except KeyError as e:   
        print('Key Error! Item not found')
        print(e)
    except Exception as e:
        print('error in controller,', e)
    finally:
        input("completion")
        return response

def create_bikes_table(dynamodb=None):
    """Creates bikes table if it doesn't exist"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )
    try:
        table = dynamodb.create_table(
            TableName='bikes',
            AttributeDefinitions=[
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'  
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        return table
    except ClientError:
        return None
    finally:
        return None

def get_bike_data(bike_name=None, dynamodb=None):
    """Getting bikes data as a dictionary"""
    if not bike_name:
        return None
    # create_bikes_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )
    table = dynamodb.Table('bikes')
    response = None
    try:
        response = table.get_item(Key={'name': bike_name})['Item']
    except ClientError as e:
        print(e.response['Error']['Message'])
    except KeyError as e:
        print('Key Error! Item not found')
        print(e)
    finally:
        return response

def get_all_bikes(dynamodb=None):
    """Getting all bikes data to show"""
    # create_bikes_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )
    table = dynamodb.Table('bikes')
    data = None
    try:
        response = table.scan()
        data = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        print(data)
        response = decimal_to_float(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    except KeyError as e:
        print('Key Error! Item not found')
        print(e)
    finally:
        # Quickfix
        return {e['name']:e for e in data}
        return data

def set_bike_data(bike_name=None, bike_data={}, dynamodb=None):
    """Updating single bike's data"""
    if not bike_name:
        return None
    # create_bikes_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )
    table = dynamodb.Table('bikes')
    response=None
    
    print('bike name', bike_name)

    def keywords(k, a=""):
        if k=="status":
            k= a+"s"
        if k=="username":
            k= a+"u"
        if k=="type":
            k= a+"t"
        return k
    # print('testing')
    exp_attr_val = {f':{keywords(k)}':v for k,v in bike_data.items() if k!='name'}
    update_exp = 'set ' + ', '.join([f'{keywords(k,"#")}=:{keywords(k)}' for k in bike_data.keys() if k!='name'])
    # print(exp_attr_val)
    # print(update_exp)
    try:
        response = table.update_item(
            Key={
                'name': bike_name,
            },
            UpdateExpression=update_exp,
            ExpressionAttributeValues=exp_attr_val,
            ExpressionAttributeNames={
                '#s':'status',
                '#u':'username',
                '#t':'type',
            },
            ReturnValues="UPDATED_NEW"
        )
        response = decimal_to_float(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    except KeyError as e:
        print('Key Error! Item not found')
        print(e)
    finally:
        return response

def create_usernames_table(dynamodb=None):
    """Creates usernames table if it doesn't exist"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )
    try:
        table = dynamodb.create_table(
            TableName='usernames',
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'  
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        return table
    except ClientError:
        return None
    finally:
        return None

def get_username(username="", dynamodb=None):
    """Getting username to chat_id mapping"""
    if not username:
        return None
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )
    table = dynamodb.Table('usernames')
    response = None
    try:
        response = table.get_item(Key={'username': username})['Item']
        response = decimal_to_float(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    except KeyError as e:
        print('Key Error! Item not found')
        print(e)
    finally:
        return response

def set_username(username="", chat_id=0, dynamodb=None):
    """Updating single bike's data"""
    if not username:
        return None
    # create_bikes_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION_NAME,
        )
    table = dynamodb.Table('usernames')
    response=None

    try:
        response = table.update_item(
            Key={
                'username': username,
            },
            UpdateExpression='set chat_id=:chat_id',
            ExpressionAttributeValues={f':chat_id':chat_id},
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    except KeyError as e:
        print('Key Error! Item not found')
        print(e)
    finally:
        return response

user_data = {
    "bike_name": "",
    "chat_id": 1,
    "credits": 2071.0,
    "finance": [
        {
            "change": 1000,
            "final": 1000,
            "initial": 0,
            "time": "2021/09/21, 13:28:42",
            "type": "admin"
        },
        {
            "credits": -429.0,
            "remaining": -1858.0,
            "spent": 1429.0,
            "time": "2021/09/22, 00:32:44",
            "type": "rental"
        },
        {
            "change": 2000,
            "final": 1571.0,
            "initial": -429.0,
            "time": "2021/09/22, 22:14:34",
            "type": "admin"
        },
        {
            "change": 500,
            "final": 2071.0,
            "initial": 1571.0,
            "time": "2021/09/26, 18:11:30",
            "type": "admin"
        }
    ],
    "first_name": "Yan Quan",
    "last_name": "Tan",
    "log": [
        {
            "end": "2021-09-22T00:32:44.265262",
            "start": "2021-09-21T16:36:41.786845",
            "time": "7 hours, 56 minutes, and 2 seconds"
        }
    ],
    "status": None,
    "username": "yanquan"
}

if __name__ == '__main__':
    # print('create table',create_bikes_table())
    # print('get_data', get_bike_data('fold_blue'))
    # print('set data', set_bike_data('fold_blue',
    #     {
    #         "colour": "blue",
    #         "name": "fold_blue",
    #         "oldpin": "12345",
    #         "pin": "00000",
    #         "status": 0,
    #         "type": "foldable",
    #         "username": ""
    #     }
    # ))
    # print('get again', get_bike_data('fold_blue'))
    # print('all', get_all_bikes())
    # print('create table', create_usernames_table())
    # print('get username', get_username('tt'))
    # print('set username', set_username('tt',44487))
    # print('get username', get_username('tt'))
    # print('Set up DB OK.')
    # print('get user', get_user_data(1))
    # print('set user', set_user_data(1,user_data))
    # print('get user', get_user_data(1))
    print(type(get_all_bikes()))
    print('Set up DB OK.')
