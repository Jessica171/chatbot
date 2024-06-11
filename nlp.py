import re
import speech_recognition as sr
import pyttsx3
import mysql.connector
import spacy
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt


# Connect to MySQL database

def establish_db_connection():
    try:
        # Connect to MySQL database
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Jessy92100#*',  # Replace with your password
            port='3306',
            database='convocart'
        )
        return mydb
    except mysql.connector.Error as e:
        print("Error:", e)
        return None

# Function to execute query
# def execute_query(mydb, name, category, gender, size, color, brand, price_range, speech_output):
#     if mydb is None:
#         print("Database connection not established.")
#         return
#
#     try:
#         mycursor = mydb.cursor()
#
#         # Your query execution logic here
#
#     except mysql.connector.Error as e:
#         print("Error executing query:", e)

# Function to close database connection
def close_db_connection(mydb):
    if mydb is not None:
        mydb.close()

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_info(text, speech_output=False):
    doc = nlp(text.lower())

    category = None
    gender = None
    size = None
    color = None
    brand = None
    price_range = None
    name = None

    # Define your lists
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

    # Mappings from terms to the category
    tops_mapping ={"tops": "tops", "blouse": "tops", "shirt": "tops", "croptop": "tops", "hoodie": "tops","pullover": "tops"}
    footwear_mapping = {"sneakers": "footwear", "heels": "footwear", "shoes": "footwear", "slippers": "footwear","sandal": "footwear", "running": "footwear"}
    dress_mapping = {"dress": "dress", "skirt": "dress", "jumpsuit": "dress", "offshoulder dress": "dress"}
    jacket_mapping = {"bomber": "jacket", "denim": "jacket", "leather": "jacket", "blazer": "jacket", "coat": "jacket"}
    bag_mapping = {"backpack": "bag", "beltbag": "bag", "clutch": "bag", "tote": "bag", "crossbag": "bag"}
    bottoms_mapping = {"jeans": "bottoms", "leggings": "bottoms", "trousers": "bottoms", "shorts": "bottoms", "sweatpants": "bottoms", "cargo": "bottoms", "yoga": "bottoms"}

    # Find all numbers in the text
    numbers = [float(num) for num in re.findall(r'[0-9]+(?:\.[0-9]+)?', text) if float(num) > 0]
    if len(numbers) >= 2:
        # If there are at least two numbers, consider them as the price range
        price_range = f"{min(numbers)} - {max(numbers)}"

    for token in doc:
        if token.text in categories:
            category = token.text
            name = category
            if category == "dress" or category == "bag":
                gender = "female"
            elif category == "bag":
                size = "N/A"  # Set size to "N/A" if category is "bag"
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
    if size is None and category != "bag":  # Exclude "bag" from size check
        missing_info.append('size')
    if color is None:
        missing_info.append('color')
    if brand is None:
        missing_info.append('brand')
    if price_range is None:
        missing_info.append('price range')

    while missing_info:
        param = missing_info[0]

        if param == "category":
            question = "What category are you interested in?\n"
            if speech_output:
                engine.say(question)
                engine.runAndWait()
                with sr.Microphone() as source:
                    audio_text = r.listen(source)
                    user_input = r.recognize_google(audio_text)
            else:
                user_input = input(question)
            if user_input not in categories:
                error_message = f"Sorry, I do not understand the category {user_input}."
                if speech_output:
                    engine.say(error_message)
                    engine.runAndWait()
                print(error_message)
                continue
            category = user_input
            missing_info.remove("category")
        elif param == "gender" and category not in ["dress", "bag"]:
            question = "What gender are you looking for?\n"
            if speech_output:
                engine.say(question)
                print( "What gender are you looking for?")
                engine.runAndWait()
                with sr.Microphone() as source:
                    audio_text = r.listen(source)
                    user_input = r.recognize_google(audio_text)
                    engine.say("You said: " + user_input)
                    engine.runAndWait()
                    print("You said:", user_input)
            else:
                user_input = input(question)
            if user_input not in genders:
                error_message = f"Sorry, we do not have items in the gender {user_input}."
                if speech_output:
                    engine.say(error_message)
                    engine.runAndWait()
                print(error_message)
                continue
            gender = user_input
            missing_info.remove("gender")
        elif param == "size" and category != "bag":  # Exclude "bag" from size question
            question = "What size are you looking for?\n"
            if speech_output:
                engine.say(question)
                print("What size are you looking for?")
                engine.runAndWait()
                with sr.Microphone() as source:
                    audio_text = r.listen(source)
                    user_input = r.recognize_google(audio_text)
                    engine.say("You said: " + user_input)
                    engine.runAndWait()
                    print("You said:", user_input)
            else:
                user_input = input(question)
            if category == "footware":
                try:
                    user_input = str(user_input)  # Try converting the input to a number
                except ValueError:
                    error_message = "Please enter a numeric value for the shoe size."
                    if speech_output:
                        engine.say(error_message)
                        engine.runAndWait()
                    print(error_message)
                    continue
            else:
                if user_input not in sizes:
                    error_message = f"Sorry, we do not have items in the size {user_input}."
                    if speech_output:
                        engine.say(error_message)
                        engine.runAndWait()
                    print(error_message)
                    continue
            size = user_input
            missing_info.remove("size")
        elif param == "color":
            question = "What color are you looking for?\n"
            if speech_output:
                engine.say(question)
                print("What color are you looking for?")
                engine.runAndWait()
                with sr.Microphone() as source:
                    audio_text = r.listen(source)
                    user_input = r.recognize_google(audio_text)
                    engine.say("You said: " + user_input)
                    engine.runAndWait()
                    print("You said:", user_input)
            else:
                user_input = input(question)
            if user_input not in colors:
                error_message = f"Sorry, we do not have items in the color {user_input}."
                if speech_output:
                    engine.say(error_message)
                    engine.runAndWait()
                print(error_message)
                continue
            color = user_input
            missing_info.remove("color")
        elif param == "brand":
            question = "Do you have a specific brand in mind?\n"
            if speech_output:
                engine.say(question)
                print("Do you have a specific brand in mind?")
                engine.runAndWait()
                with sr.Microphone() as source:
                    audio_text = r.listen(source)
                    user_input = r.recognize_google(audio_text)
                    engine.say("You said: " + user_input)
                    engine.runAndWait()
                    print("You said:", user_input)
            else:
                user_input = input(question)
            if user_input not in brands:
                error_message = f"Sorry, we do not have items from the brand {user_input}."
                if speech_output:
                    engine.say(error_message)
                    engine.runAndWait()
                print(error_message)
                continue
            brand = user_input
            missing_info.remove("brand")
        elif param == "price range":
            while True:  # Keep asking until a valid price range is provided
                question = "What price range are you considering?\n"
                if speech_output:
                    engine.say(question)
                    print( "What price range are you considering?")
                    engine.runAndWait()
                    with sr.Microphone() as source:
                        audio_text = r.listen(source)
                        user_input = r.recognize_google(audio_text)
                        engine.say("You said: " + user_input)
                        engine.runAndWait()
                        print("You said:", user_input)
                else:
                    user_input = input(question)
                # Extract the numbers from the price range
                numbers = [float(num) for num in re.findall(r'[0-9]+(?:\.[0-9]+)?', user_input) if float(num) > 0]
                if len(numbers) >= 2:
                    # If there are at least two positive numbers, consider them as the price range
                    price_range = f"{min(numbers)} - {max(numbers)}"
                    break
                else:
                    error_message = "There is something wrong with the price range. Please try again."
                    if speech_output:
                        engine.say(error_message)
                        engine.runAndWait()
                    print(error_message)
            missing_info.remove("price range")

    return name, category, gender, size, color, brand, price_range
    name, category, gender, size, color, brand, price_range = execute_query(name, category, gender, size, color, brand, price_range,speech_output)
    # return name, category, gender, size, color, brand, price_range
def display_image(image_data):
    # Convert image data to PIL Image object
    image = Image.open(BytesIO(image_data))

    # Display the image
    plt.imshow(image)
    plt.axis('off')  # Hide axis
    plt.show()



# Speech recognition setup
r = sr.Recognizer()
engine = pyttsx3.init()
def entry():
 while True:
    print("Press 1 to type your request, press 2 to speak your request, press 3 to quit.")
    choice = input()

    if choice == '1':
        speech_output = False
        user_input = input("Welcome to CONVOCART!\nWhat are you looking for today? (Type 'quit' to exit)\n")
    elif choice == '2':
        speech_output = True
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
        except sr.UnknownValueError:
            engine.say("Sorry, I could not understand what you said.")
            engine.runAndWait()
            print("Sorry, I could not understand what you said.")
            continue
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            continue
    elif choice == '3':
        print("Thank you for using CONVOCART. Goodbye!")
        break
    else:
        print("Invalid choice. Please press 1, 2, or 3.")
        continue

    if user_input.lower() == "quit":
        print("Thank you for using CONVOCART. Goodbye!\n")
        break


    name, category, gender, size, color, brand, price_range = extract_info(user_input, speech_output)
    display_userselection(name, category, gender, size, color, brand, price_range, speech_output)
    name, category, gender, size, color, brand, price_range= execute_query(name, category, gender, size, color, brand, price_range, speech_output=False)


def display_userselection( name, category, gender, size, color, brand, price_range,speech_output):
    if speech_output == True:
        print("\nHere is your selection:")
        engine.say("\nHere is your selection:")
        engine.runAndWait()
        print(f"name: {name}")
        engine.say(f"name: {name}")
        engine.runAndWait()
        print(f"Category: {category}")
        engine.say(f"Category: {category}")
        engine.runAndWait()
        if category not in ["dress", "bag"]:  # Exclude "bag" from size printing
            print(f"Gender: {gender}")
            engine.say(f"Gender: {gender}")
            engine.runAndWait()
        if category != "bag":  # Exclude "bag" from size printing
            print(f"Size: {size}")
            engine.say(f"Size: {size}")
            engine.runAndWait()
        print(f"Color: {color}")
        engine.say(f"Color: {color}")
        engine.runAndWait()
        print(f"Brand: {brand}")
        engine.say(f"Brand: {brand}")
        engine.runAndWait()
        print(f"Price Range: {price_range}\n")
        engine.say(f"Price Range: {price_range}\n")
        engine.runAndWait()
    else:
        print("\nHere is your selection:")
        print(f"name: {name}")
        print(f"Category: {category}")
        if category not in ["dress", "bag"]:  # Exclude "bag" from size printing
            print(f"Gender: {gender}")
        if category != "bag":  # Exclude "bag" from size printing
            print(f"Size: {size}")
        print(f"Color: {color}")
        print(f"Brand: {brand}")
        print(f"Price Range: {price_range}\n")

def execute_query(mydb,name, category, gender, size, color, brand, price_range,speech_output):
    # If category is identified, execute SQL query
    if mydb is None:
        print("Database connection not established.")
        return

    try:
        mycursor = mydb.cursor()

        # Your query execution logic here

    except mysql.connector.Error as e:
        print("Error executing query:", e)
    mycursor = mydb.cursor()
    if name:
        # Construct SQL query based on available parameters
        select_query = f"SELECT * FROM cloth_bc WHERE name= %s"
        data = [name]
        if category:
            select_query += " AND category = %s"
            data.append(category)
        if gender:
            select_query += " AND gender = %s"
            data.append(gender)
        if size == "all":
            select_query += ""
        else:
            select_query += " AND size = %s"
            data.append(size)
        if color == "all":
            select_query += ""
        else:
            select_query += " AND color = %s"
            data.append(color)
        if brand == "all":
            select_query += ""
        else:
            select_query += " AND brand = %s"
            data.append(brand)
        if price_range:
            # Modify this line to use the 'price' column instead of 'price_range'
            select_query += " AND price BETWEEN %s AND %s"
            min_price, max_price = price_range.split(" - ")
            data.extend([float(min_price), float(max_price)])
        mycursor.execute(select_query, data)
        results = mycursor.fetchall()
        found_results = bool(results)
        if results:
            if speech_output == True:
                print(f"Matching items found in the {category} table:")
                engine.say("Matching items found in the {category} table:")
                engine.runAndWait()
            else:
                print(f"Matching items found in the {category} table:")


    if name and not found_results:
        found_results = False
        # Construct SQL query based on available parameters
        select_query = f"SELECT * FROM cloth_bc WHERE name= %s"
        data = [name]
        if category:
            select_query += " AND category = %s"
            data.append(category)
        if gender:
            select_query += " AND gender = %s"
            data.append(gender)
        if size:
            select_query += " AND (size = %s"
            data.append(size)
        if color:
            select_query += " OR color = %s"
            data.append(color)
        if brand:
            select_query += " OR brand = %s"
            data.append(brand)
        if price_range:
            select_query += " OR (price BETWEEN %s AND %s)"
            min_price, max_price = price_range.split(" - ")
            data.extend([float(min_price), float(max_price)])
            select_query += ")"
        mycursor.execute(select_query, data)
        results = mycursor.fetchall()
        mycursor.close()
        if results:
            if speech_output == True:
                print(
                    "Unfortunately, we couldn't find an exact match for your request, but here are some similar options you might like:")
                engine.say(
                    "Unfortunately, we couldn't find an exact match for your request, but here are some similar options you might like:")
                engine.runAndWait()
            else:
                print(
                    "Unfortunately, we couldn't find an exact match for your request, but here are some similar options you might like.:")
        else:
            print(f"No matching items found in the {category} table.")
        return select_query

        # After displaying the matching items found in the database
    if results:
        for row in results:
                for i, value in enumerate(row):
                    if i != 8:  # Exclude the column containing the image data (assuming it's the 9th column)
                        print(value)
                print("")  # Add a new line after printing each row
                image_data = row[8]  # Assuming the image data is in the 9th column
                display_image(image_data)
                # Store the price of the selected item in a variable
                price = row[5]  # Assuming the price is in the 6th column
        favcart(mydb, mycursor, price, speech_output, row)
def favcart(mydb,mycursor,price, speech_output,row):
        # Ask the user if they want to add the product to cart or favorites
        while True:
                if speech_output == True:
                    print("Do you want to add this item to your cart or favorites? \n(cart/favorites/none): \n")
                    engine.say("Do you want to add this item to your cart or favorites?")
                    engine.runAndWait()
                    with sr.Microphone() as source:
                        audio_text = r.listen(source)
                        try:
                            choice = r.recognize_google(audio_text)
                            engine.say("You said: " + choice)
                            engine.runAndWait()
                            print("You said:", choice)
                        except sr.UnknownValueError:
                            engine.say("Sorry, I could not understand what you said.")
                            engine.runAndWait()
                            print("Sorry, I could not understand what you said.")
                            continue
                else:
                    choice = input(
                           "Do you want to add this item to your cart or favorites? \n(cart/favorites/none): \n").lower()
                if choice == 'cart':
                    if speech_output == True:
                        print("How many of this item would you like to add to your cart?\n")
                        engine.say(
                             "How many of this item would you like to add to your cart?\n")
                        engine.runAndWait()
                        with sr.Microphone() as source:
                         audio_text = r.listen(source)
                        user_input = r.recognize_google(audio_text)
                    else:
                         # Ask for quantity
                        item_quantity = int(input("How many of this item would you like to add to your cart?\n"))
                        # Calculate total price
                    totalprice = price * item_quantity
                    # Add the product to the cart
                    cart_query = "INSERT INTO cart (totalprice, item_quantity, user_iduser,cloth_idclothl) VALUES (%s, %s, %s,%s)"
                    totalprice
                    item_quantity
                    user_iduser = 1
                    cloth_idclothl = row[0]  # Assuming the first column contains the item ID
                    mycursor.execute(cart_query, (totalprice, item_quantity, user_iduser, cloth_idclothl))
                    mydb.commit()
                    if speech_output == True:
                        print("Item added to cart successfully!")
                        engine.say("Item added to cart successfully!")
                        engine.runAndWait()
                    else:
                         print("Item added to cart successfully!")
                    break
                elif choice == 'favourites':
                      # Add the product to favorites
                    # Similar to adding to cart, you may want to add more details
                    # Let's assume the user just wants to add one item to favorites
                    favorites_query = "INSERT INTO favorites (user_iduser,cloth_idcloth) VALUES (%s,%s)"
                    cloth_idcloth = row[0]
                    user_iduser = 1
                    mycursor.execute(favorites_query, (user_iduser,cloth_idcloth))
                    mydb.commit()
                    if speech_output == True:
                        print("Item added to favorites successfully!")
                        engine.say("Item added to favorites successfully!")
                        engine.runAndWait()
                    else:
                        print("Item added to favorites successfully!")
                    break
                elif choice == 'none':
                    if speech_output == True:
                        print("Item not added to cart or favorites.")
                        engine.say("Item not added to cart or favorites.")
                        engine.runAndWait()
                    else:
                        print("Item not added to cart or favorites.")
                    break
                else:
                    if speech_output == True:
                        print("Invalid choice. Please choose 'cart', 'favorites', or 'none'.")
                        engine.say("Invalid choice. Please choose 'cart', 'favorites', or 'none'.")
                        engine.runAndWait()
                    else:
                        print("Invalid choice. Please choose 'cart', 'favorites', or 'none'.")

# Close cursor and database connection
# mycursor.close()
# mydb.close()
if __name__ == "__main__":
    mydb = establish_db_connection()
    entry()