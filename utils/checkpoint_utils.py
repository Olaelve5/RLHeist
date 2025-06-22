import os


def list_checkpoints():
    """
    Lists all models in the models folder.
    """

    models_dir = os.path.join(os.getcwd(), "policies_checkpoints")
    if not os.path.exists(models_dir):
        print("Models directory does not exist.")
        return []
    models = []
    for filename in os.listdir(models_dir):
        if filename.startswith("RLHeist_checkpoint_iteration_"):
            model_path = os.path.join(models_dir, filename)
            models.append(
                {
                    "name": filename,
                    "path": model_path,
                }
            )
    models = sort_checkpoints(models)
    return models


def sort_checkpoints(checkpoints):
    """
    Sorts the checkpoints based on the iteration number.
    """
    return sorted(
        checkpoints,
        key=lambda x: int(x["name"].split("_")[-1].split(".")[0]),
        reverse=False,
    )


def choose_model():
    """
    Prompts the user to choose a model from the available checkpoints.
    """
    models = list_checkpoints()
    if not models:
        print("No models available.")
        return None

    print("Available models:")
    for i, model in enumerate(models):
        print(f"{i + 1}: {model["name"]}")

    while True:
        try:
            choice = int(input("Choose a model by number: ")) - 1
            if 0 <= choice < len(models):
                return models[choice]["path"]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_latest_checkpoint():
    checkpoints = list_checkpoints()
    if not checkpoints:
        print("No checkpoints found.")
        return None
    latest_checkpoint = checkpoints[-1]  # Get the last checkpoint in the sorted list

    return latest_checkpoint["path"]
