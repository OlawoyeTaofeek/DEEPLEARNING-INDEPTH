from helpers import connect_to_weaviate, get_data, CollectionName
from weaviate.classes.config import Configure, DataType, Property, Tokenization
from tqdm import tqdm
from weaviate.util import generate_uuid5
from delete_collection import delete_collection
from weaviate import WeaviateClient
from typing import Dict, Union

def parse_data_object(data_row) -> Dict[str, Dict[str, Union[str, int, float]]]:
    # Process fields using helper functions - only extract what's needed for the simplified Movie model
    properties = data_row["properties"]
    processed_properties = {
        "movie_id": properties["movie_id"],
        "title": properties["title"],
        "original_language": properties['original_language'],
        "overview": properties["overview"],
        "genres": properties['genres'],
        "keywords":properties["keywords"],
        "credits": properties["credits"],
        "year": properties["year"],
        "popularity": properties["popularity"],
        "budget": int(properties["budget"]),
        "revenue": int(properties["revenue"]),
        "vote_average": properties["vote_average"],
        "vote_count": int(properties['vote_count']),
        "runtime": int(properties['runtime']),
        
    }
    return {
        "properties": processed_properties
    }

def create_collection(client: WeaviateClient):

    if not client.collections.exists(CollectionName.MOVIES):

        client.collections.create(
            name=CollectionName.MOVIES,
            description="A movie collection for recommendation",

            # ✅ ALL PROPERTIES (MATCHING YOUR PARSER)
            properties=[
                Property(name="movie_id", data_type=DataType.INT),
                Property(name="title", data_type=DataType.TEXT),
                Property(name="original_language", data_type=DataType.TEXT),
                Property(name="overview", data_type=DataType.TEXT),
                Property(name="genres", data_type=DataType.TEXT_ARRAY),
                Property(name="keywords", data_type=DataType.TEXT_ARRAY),
                Property(
                    name="credits", 
                    data_type=DataType.TEXT_ARRAY, 
                    tokenization=Tokenization.FIELD
                ),

                Property(name="year", data_type=DataType.INT),
                Property(name="popularity", data_type=DataType.NUMBER),
                Property(name="budget", data_type=DataType.INT),
                Property(name="revenue", data_type=DataType.INT),

                Property(name="vote_average", data_type=DataType.NUMBER),
                Property(name="vote_count", data_type=DataType.INT),
                Property(name="runtime", data_type=DataType.INT),
            ],
            vector_config=[
                Configure.Vectors.text2vec_openai(
                    name="default",
                    source_properties=[
                        "title",
                        "overview"    
                    ],
                    model="text-embedding-3-small",
                    quantizer=Configure.VectorIndex.Quantizer.rq(),
                    vector_index_config=Configure.VectorIndex.hnsw(),
                ),
                Configure.Vectors.text2vec_openai(
                    name="genres",
                    source_properties=["genres"],
                    model="text-embedding-3-small",
                    quantizer=Configure.VectorIndex.Quantizer.rq(),
                    vector_index_config=Configure.VectorIndex.hnsw(),
                ),
            ]
        )

    else:
        delete_collection(CollectionName.MOVIES)
        raise RuntimeError(
            "Collection already exists. Delete it before recreating."
        )
    
def ingest_movies_data(client: WeaviateClient, max_objects=20000):
    movies = client.collections.get(CollectionName.MOVIES)

    count = 0
    with movies.batch.fixed_size(batch_size=200) as batch:
        for raw_data in tqdm(get_data(), total=max_objects):
            parsed = parse_data_object(raw_data)
            batch.add_object(
                properties=parsed["properties"],
                uuid=generate_uuid5(parsed["properties"])
            )

            count += 1
            if count >= max_objects:
                break

    # Check failures
    if len(movies.batch.failed_objects) > 0:
        print(f"Failed objects: {len(movies.batch.failed_objects)}")

    print(f"Ingested {count} movies successfully")

def main():
    """
    Main function to run the data ingestion process
    """
    print("Starting Movie Data Ingestion into Weaviate")
    print("=" * 50)

    try:
        # Connect to Weaviate
        print("Connecting to Weaviate...")
        with connect_to_weaviate() as client:
            print("Connected successfully!")

            # Create the collection
            print("Creating Movies collection...")
            create_collection(client)
            print("Collection ready!")

            # Ingest the data
            print("Ingesting movie data...")
            ingest_movies_data(client)
            print("Data ingestion complete!")

    except Exception as e:
        print(f"Error: {str(e)}")
        print("Check your Weaviate connection and try again")

if __name__ == "__main__":
    main()

