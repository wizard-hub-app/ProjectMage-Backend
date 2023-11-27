from openai import OpenAI
import os
from datetime import datetime
import pytz

import json

client = OpenAI()

def generate_poem(info: dict):
    
    prompt = f"""
        Visual Weather Artist GPT is designed to provide a unique and artistic representation of the weather in a poem. 

        It can get the city, weather adn time based on the content later

        It must then issue a whimsical, rhymed poem about the current weather conditions, time of day, and location after confirming a city-level location from the user. 

        It should not display search results or speak outside of providing the poem. 


        The GPT should persistently seek a specific city location if not provided and refrain from any further dialogue until a location is given. It should follow these steps in sequence without prompting from the user after the location is received. (First Poem, Then DALL-E generated weather report)

    """

    
    now = datetime.now(tz=pytz.timezone('Asia/Shanghai'))

    dt_string = now.strftime("%H:%M:%S")
    
    city = info.get("city")
    weather = info.get("weather")
    temperature = info.get("temperature")
    
    user_input =  f"city:{city}, time:{dt_string}, weather: {weather}, temperature: {temperature} Celsius degree"

    response = client.chat.completions.create(
      model="gpt-4-1106-preview",
      messages=[

        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input}
      ]
    )
    poem = response.choices[0].message.content
    
    return user_input, poem

def generate_image(user_input: str, poem: str):
    image_poem_prompt = f"""
    Visual Weather Artist GPT is designed to provide a unique and artistic representation of the weather in a image based on the poem, city, time and weather.

    So it works as  weather report image generator.

    The image should incorporate the weather conditions stylistically, such as having elements in the image reflect the weather (e.g., text of the temperature that looks wet in rainy conditions). 

    However，if the image has some text, please limit to temperature and weather. Do not add any other text.

    {user_input}

    poem:{poem}
    """
    response = client.images.generate(
      model="dall-e-3",
      prompt=image_poem_prompt,
      size="1024x1024",
      quality="standard",
      n=1,
    )
    
    image_url = response.data[0].url
    
    return image_url

def generate(info: dict):
    user_info, poem = generate_poem(info)
    
    image_url = generate_image(user_info, poem)
    
    return poem, image_url

def lambda_handler(event, context):
	parameters = event.get("queryStringParameters")
	poem, image_url = generate(parameters)
	
	return {
		'statusCode': 200,
		'headers': {
			'Content-Type': 'application/json',
			'Access-Control-Allow-Origin': '*'
		},
		'body': json.dumps({"poem": poem, "image_url": image_url}),
		"isBase64Encoded": False
	}
