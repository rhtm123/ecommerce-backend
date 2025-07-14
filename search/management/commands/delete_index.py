from django.core.management.base import BaseCommand

from meilisearch import Client

from search.client import client

def delete_all_indexes(meilisearch_client: Client) -> None:
    """
    Deletes all indexes in the Meilisearch instance.
    
    Args:
        meilisearch_client: Initialized Meilisearch client instance.
    """
    try:
        # Get all indexes
        indexes = meilisearch_client.get_indexes()
        
        if not indexes.get("results"):
            print("No indexes found to delete.")
            return

        # Iterate through all indexes and delete them
        for index in indexes.get("results"):
            print(f"Deleting index: {index.uid}")
            task = meilisearch_client.delete_index(index.uid)
            # Wait for the deletion task to complete
            meilisearch_client.wait_for_task(task.task_uid)
            task_status = meilisearch_client.get_task(task.task_uid)
            print(f"Deletion status for {index.uid}: {task_status.status}")
            if task_status.status == "succeeded":
                print(f"Successfully deleted index: {index.uid}")
            else:
                print(f"Failed to delete index: {index.uid}. Error: {task_status.error}")

    except Exception as e:
        print(f"Error deleting indexes: {str(e)}")

class Command(BaseCommand):
    help = "Delete all products to Meilisearch"

    def handle(self, *args, **kwargs):
        delete_all_indexes(client)
        print("DELETED EVERYTHING") 