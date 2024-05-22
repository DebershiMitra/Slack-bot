from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
import json
import datetime
from slack.models import SlackUser

def fetch_channels_and_users(token):
    # Initialize WebClient
    client = WebClient(token=token)
    logger = logging.getLogger(__name__)

    # Initialize stores for conversations and users
    channel_store = {}
    users_store = {}

    try:
        # Fetch channels
        result = client.conversations_list()
        channels = result["channels"]

        # Save channel information
        for channel in channels:
            channel_id = channel["id"]
            created_timestamp = channel.get("created", "")
            created_date = datetime.datetime.fromtimestamp(created_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            channel_store[channel_id] = {
                "name": channel.get("name", ""),
                "created": created_date,
                "is_private": channel.get("is_private", False)
            }

        # Fetch users
        result = client.users_list()
        users = result["members"]


        # Save user information
        # Save user information
        for user in users:
            user_id = user["id"]
            real_name = user["real_name"]
            users_store[user_id] = real_name
        return channel_store,users_store

    except SlackApiError as e:
        logger.error(f"Error fetching data: {e}")

def retrieve_and_parse_channel_data(api_token, channel_id):
    # Initialize WebClient
    client = WebClient(token=api_token)
    # Store conversation messages
    messages = []

    try:
        # Call the conversations.history method using the WebClient
        result = client.conversations_history(channel=channel_id)
        conversation_history = result["messages"]

        u_id = SlackUser.objects.values_list('id')
        u_name = SlackUser.objects.values_list('name')
        uid = [i[0] for i in u_id]
        uname = [i[0] for i in u_name]
        users = dict(zip(u_id, u_name))

        # Define user mapping
        # users = {'U06PGS6FSUW':'Hitesh Kale', 'U06Q4LMR03B':'Debershi_Mitra', 'U06Q3THS0P3':'Deepanshu Verma',
                #  'U06QF6DJPTJ':'Soumya Kushwaha','U06PR7VUF1R':'Suraj Lambor','U06PL3Y8DEK':'Aditya Vardhan'}

        # Parse conversation history
        for message in conversation_history:
            user_id = message.get('user', '')
            user_name = users.get(user_id, 'Unknown User')
            message_text = message.get('text', '')
            timestamp = message.get('ts', '')

            # Convert timestamp to human-readable format
            dt_object = datetime.datetime.fromtimestamp(float(timestamp))
            formatted_timestamp = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            # Construct message dictionary
            message_dict = {
                "channel_id": channel_id,
                "user_id": user_id,
                "text": message_text,
                "timestamp": formatted_timestamp
            }
            messages.append(message_dict)

        return messages

    except SlackApiError as e:
        print(f"Error retrieving conversation: {e}")
        return []

def retrieve_channel_data(api, channel_id):
    # Initialize WebClient
    client = WebClient(token=api)
    # Store conversation history
    conversation_history = []
    try:
        # Call the conversations.history method using the WebClient
        result = client.conversations_history(channel=channel_id)
        conversation_history = result["messages"]

        # Print results
        print("{} messages found in {}".format(len(conversation_history), channel_id))
        # Convert conversation history to JSON string
        # conversation_json = json.dumps(conversation_history, indent=4)
        return conversation_history

    except SlackApiError as e:
        # Print error message
        print("Error retrieving conversation: {}".format(e))
        return None
    
def json_parser(json_data):
    res=''
    users={'U06PGS6FSUW':'Hitesh Kale', 'U06Q4LMR03B':'Debershi_Mitra', 'U06Q3THS0P3':'Deepanshu Verma','U06QF6DJPTJ':'Soumya Kushwaha','U06PR7VUF1R':'Suraj Lambor','U06PL3Y8DEK':'Aditya Vardhan'}
    for i in range(len(json_data)):
        # Iterate through the dictionary and print key-value pairs
        for key, value in json_data[i].items():
            # print(f"\nKey: {key}")
            # print(f"Value: {value}\n")
            if key=='user':
                if value in users:
                    user_name=users[value]
                    res+=user_name+' sent the message: \n'
            if key=='text':
                res+=str(value)+'\n'
            if key=='ts':
                dt_object = datetime.datetime.fromtimestamp(float(value))
                # Format the datetime object as a readable date
                res+='on :'+ str(dt_object)+'\n'
        res+=' \n'
    return res