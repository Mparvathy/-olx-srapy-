class CustomPipeline(object):
    def process_item(self, item, spider):
        # Access item fields
        property_name = item['property_name']
        price = f"{item['price']['currency']}{item['price']['amount']}"
        location = item['location']

        # Format the output as a string
        output_string = f"Property Name: {property_name}\nPrice: {price}\nLocation: {location}\n"

        # You can also create a list or dictionary for further processing
        output_list = [property_name, price, location]

        # Return the modified item or a new item
        return item  # Or return output_string, output_list, etc.