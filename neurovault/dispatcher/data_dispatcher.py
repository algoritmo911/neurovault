class DataDispatcher:
    def route(self, analyzed_item):
        classification = analyzed_item.get("analysis", {}).get("classification")
        item_id = analyzed_item.get("original_data", {}).get("id", "N/A")

        if classification in ["fact", "fiction"]:
            print(f"Элемент [{item_id}] отправлен на финальную обработку.")
        elif classification == "unverifiable":
            print(f"Элемент [{item_id}] отправлен в отдел глубинного анализа.")
