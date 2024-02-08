import spacy

nlp = spacy.load("en_core_web_sm")

def extract_info(text):
    doc = nlp(text.lower())

    category = None
    size = None
    color = None
    brand = None
    price_range = None

    for token in doc:
        if token.text in ["t-shirt", "dress", "pants", "jacket"]:
            category = token.text
        elif token.text == "bag":
            category = token.text
            size = "N/A"  # Set size to "N/A" if category is "bag"
        elif token.text == "shoes":
            category = token.text
            size_text = doc[token.i + 1:].text
            try:
                size = float(size_text)  # Try converting the text to a number
            except ValueError:
                size = None  # Set size to None if conversion fails
        elif token.text in ["small", "medium", "large"]:
            size = token.text
        elif token.text in ["red", "orange", "black", "blue", "green", "yellow"]:
            color = token.text
        elif token.text in ["gucci", "zara", "nike", "adidas"]:
            brand = token.text
        elif token.text == "price" and doc[token.i + 1].text == "range":
            price_range = doc[token.i + 2:].text

    missing_info = []
    if category is None:
        missing_info.append('category')
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
            category = input("What category are you interested in?\n")
            missing_info.remove("category")
        elif param == "size" and category != "bag":  # Exclude "bag" from size question
            size = input("What size are you looking for?\n")
            missing_info.remove("size")
        elif param == "color":
            color = input("What color are you looking for?\n")
            missing_info.remove("color")
        elif param == "brand":
            brand = input("Do you have a specific brand in mind?\n")
            missing_info.remove("brand")
        elif param == "price range":
            price_range = input("What price range are you considering?\n")
            missing_info.remove("price range")

    return category, size, color, brand, price_range


# Beginning greeting
print("Welcome to the online shopping assistant!")

while True:
    user_input = input("What are you looking for today? (Type 'quit' to exit)\n")
    if user_input.lower() == "quit":
        print("Thank you for using our service. Goodbye!\n")
        break

    category, size, color, brand, price_range = extract_info(user_input)

    print("Here is your selection:")
    print(f"Category: {category}")
    if category != "bag":  # Exclude "bag" from size printing
        print(f"Size: {size}")
    print(f"Color: {color}")
    print(f"Brand: {brand}")
    print(f"Price Range: {price_range}")
