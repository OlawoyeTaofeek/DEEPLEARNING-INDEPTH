from helpers import connect_to_weaviate

def delete_collection(name: str):
    """Delete collection from Weaviate Cloud if exist"""
    try:
       with connect_to_weaviate() as client:
            if client.collections.exists(name):
               print(f"Found collect: {name}")
               print(f"📊 Collection size: {len(client.collections.get(name))} objects")
               
               client.collections.delete(name)
               print("Collection deleted Successfully")
            else:
               print(f"Collection '{name}' does not exist.")
               print('Nothing to delete!')
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Check your Weaviate connection and try again.")


if __name__ == "__main__":
    delete_collection()
    