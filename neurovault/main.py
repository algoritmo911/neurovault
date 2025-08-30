from dispatcher.data_dispatcher import DataDispatcher

def main():
    dispatcher = DataDispatcher()

    # Example 1: Fact
    fact_item = {
        "original_data": {"id": "123", "text": "The sky is blue."},
        "analysis": {"classification": "fact"}
    }
    print("Routing item 123 (fact):")
    dispatcher.route(fact_item)

    # Example 2: Fiction
    fiction_item = {
        "original_data": {"id": "456", "text": "The moon is made of cheese."},
        "analysis": {"classification": "fiction"}
    }
    print("\nRouting item 456 (fiction):")
    dispatcher.route(fiction_item)

    # Example 3: Unverifiable
    unverifiable_item = {
        "original_data": {"id": "789", "text": "There is a teapot orbiting the Sun."},
        "analysis": {"classification": "unverifiable"}
    }
    print("\nRouting item 789 (unverifiable):")
    dispatcher.route(unverifiable_item)

if __name__ == "__main__":
    main()
