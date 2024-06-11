from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import spacy

# Load pre-trained transformer model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
nlp = pipeline("ner", model=model, tokenizer=tokenizer)


# Function to extract information using transformer model
def extract_info_transformer(text):
    doc = nlp(text)
    category, gender, size, color, brand, price_range = None, None, None, None, None, None

    categories = ["tops", "dress", "bottoms", "jacket", "bag", "footwear"]
    genders = ["male", "female", "unisex"]
    sizes = ["xsmall", "small", "medium", "large", "xlarge", "all"]
    colors = ["red", "orange", "black", "blue", "green", "yellow", "white", "grey", "pink", "purple", "brown", "all"]
    brands = ["gucci", "zara", "nike", "adidas", "brand", "all"]

    for entity in doc:
        if entity['entity'] == 'CATEGORY' and entity['word'].lower() in categories:
            category = entity['word'].lower()
        elif entity['entity'] == 'GENDER' and entity['word'].lower() in genders:
            gender = entity['word'].lower()
        elif entity['entity'] == 'SIZE' and entity['word'].lower() in sizes:
            size = entity['word'].lower()
        elif entity['entity'] == 'COLOR' and entity['word'].lower() in colors:
            color = entity['word'].lower()
        elif entity['entity'] == 'BRAND' and entity['word'].lower() in brands:
            brand = entity['word'].lower()
        elif entity['entity'] == 'PRICE':
            price_range = entity['word']

    return category, gender, size, color, brand, price_range


# Function to run the chatbot with transformer model
def main_transformer():
    while True:
        user_input = input("Welcome to CONVOCART!\nWhat are you looking for today? (Type 'quit' to exit)\n")
        if user_input.lower() == "quit":
            print("Thank you for using CONVOCART. Goodbye!\n")
            break

        category, gender, size, color, brand, price_range = extract_info_transformer(user_input)
        print(
            f"Extracted Info:\nCategory: {category}\nGender: {gender}\nSize: {size}\nColor: {color}\nBrand: {brand}\nPrice Range: {price_range}\n")


if __name__ == "__main__":
    main_transformer()


