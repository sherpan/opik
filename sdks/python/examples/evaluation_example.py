from typing import Dict, Any

from opik.evaluation.metrics import (
    Contains,
    IsJson,
    Hallucination,
)
from opik.evaluation import evaluate
from opik import Opik, DatasetItem, track
from opik.integrations.openai import track_openai
import openai


# os.environ["OPENAI_ORG_ID"] = "<>"
# os.environ["OPENAI_API_KEY"] = "<>"

openai_client = track_openai(openai.OpenAI())

contains_hello = Contains(searched_value="hello", name="ContainsHello")
contains_bye = Contains(searched_value="bye", name="ContainsBye")
is_json = IsJson()
hallucination = Hallucination()

client = Opik()
dataset = client.create_dataset(name="My 42 dataset", description="For storing stuff")
# dataset = client.get_dataset(name="My 42 dataset")

json = """
    [
        {
            "Model inputs": {"message": "Greet me!", "context": []}
        },
        {
            "Model inputs": {"message": "Ok, I'm leaving, bye!", "context": []}
        },
        {
            "Model inputs": {"message": "How are you doing?", "context": []}
        },
        {
            "Model inputs": {"message": "Give a json example!", "context": []}
        },
        {
            "Model inputs": {
                "message": "What is the main currency in european union?",
                "context": ["Euro is the main european currency. It is used across most EU countries"]
            }
        }
    ]
"""

dataset.insert_from_json(json_array=json, keys_mapping={"Model inputs": "input"})


@track()
def llm_task(item: DatasetItem) -> Dict[str, Any]:
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": item.input["message"]}],
    )

    return {
        "output": response.choices[0].message.content,
        "input": item.input["message"],
        "context": item.input["context"],
    }


evaluate(
    experiment_name="My experiment",
    dataset=dataset,
    task=llm_task,
    scoring_metrics=[contains_hello, contains_bye, is_json, hallucination],
)
