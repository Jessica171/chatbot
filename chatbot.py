import re
import speech_recognition as sr
import pyttsx3
import mysql.connector
import spacy
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

# Global variables
r = sr.Recognizer()
engine = pyttsx3.init()
nlp = spacy.load("en_core_web_sm")

# Connect to MySQL database
def connect_to_database():
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Jessy92100#*',
        port='3306',
        database='convocart'
    )
    return mydb

# Close database connection
def close_database(mydb):
    mydb.close()

# Extract information from text
def extract_info(text, speech_output=False):
    doc = nlp(text.lower())

    category = None
    gender = None
    size = None
    color = None
    brand = None
    price_range = None
    name = None

    categories = ["tops", "dress", "bottoms", "jacket", "bag", "footwear"]
    genders = ["male", "female", "unisex"]
    sizes = ["xsmall", "small", "medium", "large", "xlarge", "all"]
    colors = ["red", "orange", "black", "blue", "green", "yellow", "white", "grey", "pink", "purple", "brown", "all"]
    brands = ["gucci", "zara", "nike", "adidas", "brand", "all"]
    footwear_terms = ["sneakers", "heels", "shoes", "slippers", "sandal", "running"]
    tops_terms = ["tops", "blouse", "shirt", "croptop", "hoodie", "pullover"]
    dress_terms = ["dress", "skirt", "jumpsuit", "offshoulder dress"]
    jacket_terms = ["bomber", "denim", "leather", "blazer", "coat"]
    bag_terms = ["backpack", "beltbag", "clutch", "tote", "crossbag"]
    bottoms_terms = ["jeans", "leggings", "trousers", "shorts", "sweatpants", "cargo", "yoga"]

    tops_mapping = {"tops": "tops", "blouse": "tops", "shirt": "tops", "croptop": "tops", "hoodie": "tops", "pullover": "tops"}
    footwear_mapping = {"sneakers": "footwear", "heels": "footwear", "shoes": "footwear", "slippers": "footwear", "sandal": "footwear", "running": "footwear"}
    dress_mapping = {"dress": "dress", "skirt": "dress", "jumpsuit": "dress", "offshoulder dress": "dress"}
    jacket_mapping = {"bomber": "jacket", "denim": "jacket", "leather": "jacket", "blazer": "jacket", "coat": "jacket"}
    bag_mapping = {"backpack": "bag", "beltbag": "bag", "clutch": "bag", "tote": "bag", "crossbag": "bag"}
    bottoms_mapping = {"jeans": "bottoms", "leggings": "bottoms", "trousers": "bottoms", "shorts": "bottoms", "sweatpants": "bottoms", "cargo": "bottoms", "yoga": "bottoms"}

    numbers = [float(num) for num in re.findall(r'[0-9]+(?:\.[0-9]+)?', text) if float(num) > 0]
    if len(numbers) >= 2:
        price_range = f"{min(numbers)} - {max(numbers)}"

    for token in doc:
        if token.text in categories:
            category = token.text
            name = category
            if category == "dress" or category == "bag":
                gender = "female"
            elif category == "bag":
                size = "N/A"
            elif category == "footware":
                size_text = doc[token.i + 1:].text
                shoe_size = next((str(num) for num in re.findall(r'[0-9]+(?:\.[0-9]+)?', size_text)), None)
                if shoe_size is not None:
                    size = shoe_size
        elif token.text in genders:
            gender = token.text
        elif token.text in sizes:
            size = token.text
        elif token.text in colors:
            color = token.text
        elif token.text in brands:
            brand = token.text
        elif token.text in footwear_terms:
            category = footwear_mapping.get(token.text)
            name = token.text
        elif token.text in tops_terms:
            category = tops_mapping.get(token.text)
            name = token.text
        elif token.text in dress_terms:
            category = dress_mapping.get(token.text)
            name = token.text
        elif token.text in bottoms_terms:
            category = bottoms_mapping.get(token.text)
            name = token.text
        elif token.text in jacket_terms:
            category = jacket_mapping.get(token.text)
            name = token.text
        elif token.text in bag_terms:
            category = bag_mapping.get(token.text)
            name = token.text

    missing_info = []
    if category is None:
        missing_info.append('category')
    if gender is None and category not in ["dress", "bag"]:
        missing_info.append('gender')
    if size is None and category != "bag":
        missing_info.append('size')
    if color is None:
        missing_info.append('color')
    if brand is None:
        missing_info.append('brand')
    if price_range is None:
        missing_info.append('price range')

    while missing_info:
        param = missing_info[0]
        user_input = get_user_input(param, speech_output)
        if user_input is not None:
            if param == "category":
                category = user_input
            elif param == "gender" and category not in ["dress", "bag"]:
                gender = user_input
            elif param == "size" and category != "bag":
                size = user_input
            elif param == "color":
                color = user_input
            elif param == "brand":
                brand = user_input
            elif param == "price range":
                price_range = user_input
            missing_info.remove(param)

    return name, category, gender, size, color, brand, price_range

# Get user input
def get_user_input(param, speech_output):
    param_question_map = {
        "category": "What category are you interested in?\n",
        "gender": "What gender are you looking for?\n",
        "size": "What size are you looking for?\n",
        "color": "What color are you looking for?\n",
        "brand": "Do you have a specific brand in mind?\n",
        "price range": "What price range are you considering?\n"
    }

    if param == "category":
        options = ["tops", "dress", "bottoms", "jacket", "bag", "footwear"]
    elif param == "gender":
        options = ["male", "female", "unisex"]
    elif param == "size":
        options = ["xsmall", "small", "medium", "large", "xlarge", "all"]
    elif param == "color":
        options = ["red", "orange", "black", "blue", "green", "yellow", "white", "grey", "pink", "purple", "brown", "all"]
    elif param == "brand":
        options = ["gucci", "zara", "nike", "adidas", "brand", "all"]
    elif param == "price range":
        options = None

    while True:
        question = param_question_map[param]
        user_input = get_user_response(question, speech_output)

        if param == "price range":
            numbers = [float(num) for num in re.findall(r'[0-9]+(?:\.[0-9]+)?', user_input) if float(num) > 0]
            if len(numbers) >= 2:
                return f"{min(numbers)} - {max(numbers)}"
            else:
                error_message = "There is something wrong with the price range. Please try again."
                if speech_output:
                    engine.say(error_message)
                    engine.runAndWait()
                print(error_message)
                continue

        if options is None or user_input in options:
            return user_input
        else:
            error_message = f"Sorry, we do not have items in the {param} {user_input}."
            if speech_output:
                engine.say(error_message)
                engine.runAndWait()
            print(error_message)

# Get user response
def get_user_response(question, speech_output):
    if speech_output:
        engine.say(question)
        engine.runAndWait()
        print(question)
        with sr.Microphone() as source:
            audio_text = r.listen(source)
        try:
            user_input = r.recognize_google(audio_text)
            engine.say("You said: " + user_input)
            engine.runAndWait()
            print("You said:", user_input)
        except sr.UnknownValueError:
            engine.say("Sorry, I could not understand what you said.")
            engine.runAndWait()
            print("Sorry, I could not understand what you said.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None
    else:
        user_input = construct_sql_query()

    return user_input

# Display image
def display_image(image_data):
    image = Image.open(BytesIO(image_data))
    plt.imshow(image)
    plt.axis('off')
    plt.show()

# Get user input for search
def get_user_input_for_search(engine, r, speech_output):
    if speech_output:
        engine.say("Welcome to CONVOCART! please Speak your request:")
        engine.runAndWait()
        print("Welcome to CONVOCART! please Speak your request:")
        with sr.Microphone() as source:
            audio_text = r.listen(source)
        try:
            user_input = r.recognize_google(audio_text)
            engine.say("You said: " + user_input)
            engine.runAndWait()
            print("You said:", user_input)
            return user_input
        except sr.UnknownValueError:
            engine.say("Sorry, I could not understand what you said.")
            engine.runAndWait()
            print("Sorry, I could not understand what you said.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
    else:
        return "Welcome to CONVOCART!\nWhat are you looking for today? (Type 'quit' to exit)\n"

# Display user selection
def display_selection(engine, name, category, gender, size, color, brand, price_range, speech_output):
    if speech_output:
        engine.say("\nHere is your selection:")
        engine.runAndWait()
        engine.say(f"name: {name}")
        engine.runAndWait()
        engine.say(f"Category: {category}")
        engine.runAndWait()
        if category not in ["dress", "bag"]:
            engine.say(f"Gender: {gender}")
            engine.runAndWait()
        if category != "bag":
            engine.say(f"Size: {size}")
            engine.runAndWait()
        engine.say(f"Color: {color}")
        engine.runAndWait()
        engine.say(f"Brand: {brand}")
        engine.runAndWait()
        engine.say(f"Price Range: {price_range}\n")
        engine.runAndWait()
    else:
        print("\nHere is your selection:")
        print(f"name: {name}")
        print(f"Category: {category}")
        if category not in ["dress", "bag"]:
            print(f"Gender: {gender}")
        if category != "bag":
            print(f"Size: {size}")
        print(f"Color: {color}")
        print(f"Brand: {brand}")
        print(f"Price Range: {price_range}\n")

# Construct SQL query
def construct_sql_query(name, category, gender, size, color, brand, price_range):
    select_query = f"SELECT * FROM cloth_bc WHERE name= %s"
    data = [name]
    if category:
        select_query += " AND category = %s"
        data.append(category)
    if gender:
        select_query += " AND gender = %s"
        data.append(gender)
    if size and size != "all":
        select_query += " AND size = %s"
        data.append(size)
    if color and color != "all":
        select_query += " AND color = %s"
        data.append(color)
    if brand and brand != "all":
        select_query += " AND brand = %s"
        data.append(brand)
    if price_range:
        min_price, max_price = price_range.split(" - ")
        select_query += " AND price BETWEEN %s AND %s"
        data.extend([float(min_price), float(max_price)])
    return select_query, data

# Execute SQL query
def execute_query(mycursor, select_query, data):
    mycursor.execute(select_query, data)
    return mycursor.fetchall()

# Add to cart
def add_to_cart(mycursor, mydb, price, row, item_quantity):
    totalprice = price * item_quantity
    cart_query = "INSERT INTO cart (totalprice, item_quantity, user_iduser, cloth_idclothl) VALUES (%s, %s, %s,%s)"
    user_iduser = 1
    cloth_idclothl = row[0]
    mycursor.execute(cart_query, (totalprice, item_quantity, user_iduser, cloth_idclothl))
    mydb.commit()

# Add to favorites
def add_to_favorites(mycursor, mydb, row):
    favorites_query = "INSERT INTO favorites (user_iduser, cloth_idcloth) VALUES (%s, %s)"
    cloth_idcloth = row[0]
    user_iduser = 1
    mycursor.execute(favorites_query, (user_iduser, cloth_idcloth))
    mydb.commit()

# Main function
def entery(user_input , user_choice):
    mydb = connect_to_database()
    mycursor = mydb.cursor()

    while True:
        # print("Press 1 to type your request, press 2 to speak your request, press 3 to quit.")
        # choice = input()

        if user_choice == '1':
            speech_output = False

            #return get_user_response(get_user_input(extract_info(user_input, False),False),False)
        elif user_choice == '2':
            speech_output = True
            user_input = get_user_input_for_search(engine, r, speech_output)
        elif user_choice == '3':
            print("Thank you for using CONVOCART. Goodbye!")
            break
        else:
            print("Invalid choice. Please press 1, 2, or 3.")
            continue

        if user_input.lower() == "quit":
            print("Thank you for using CONVOCART. Goodbye!\n")
            break

        name, category, gender, size, color, brand, price_range = extract_info(user_input, speech_output)
        display_selection(engine, name, category, gender, size, color, brand, price_range, speech_output)

        if name:
            select_query, data = construct_sql_query(name, category, gender, size, color, brand, price_range)
            results = execute_query(mycursor, select_query, data)

            if results:
                print(f"Matching items found in the {category} table:")
               # return results
            else:
                print(f"No matching items found in the {category} table.")
                break

            returned_items = []

            for row in results:
                for i, value in enumerate(row):
                    if i != 8:
                        returned_items.append(value)
                print("")
                image_data = row[8]
                display_image(image_data)
                price = row[5]
                return returned_items
                # while True:
                #     choice = input("Do you want to add this item to your cart or favorites? (cart/favorites/none): \n").lower()
                #     if choice == 'cart':
                #         item_quantity = int(input("How many of this item would you like to add to your cart?\n"))
                #         add_to_cart(mycursor, mydb, price, row, item_quantity)
                #         print("Item added to cart successfully!")
                #         break
                #     elif choice == 'favorites':
                #         add_to_favorites(mycursor, mydb, row)
                #         print("Item added to favorites successfully!")
                #         break
                #     elif choice == 'none':
                #         print("Item not added to cart or favorites.")
                #         break
                #     else:
                #         print("Invalid choice. Please choose 'cart', 'favorites', or 'none'.")

    mycursor.close()
    close_database(mydb)

