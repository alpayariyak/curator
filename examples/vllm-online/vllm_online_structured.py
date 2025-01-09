"""Generate synthetic recipes for different cuisines using vLLM online API with structured output.

This script demonstrates using vLLM backend with curator to generate structured recipe data for various
world cuisines in an efficient batched manner. It uses the Qwen2.5-3B-Instruct model and expects
responses in a structured format defined by Pydantic models.

To start the vLLM server, run the following command:
vllm serve
Qwen/Qwen2.5-3B-Instruct
--host localhost
--port 8787
--api-key token-abc123
"""

import os
from typing import List

from datasets import Dataset
from pydantic import BaseModel, Field

from bespokelabs import curator


class Recipe(BaseModel):
    """A recipe with structured fields for title, ingredients, instructions and timing details."""

    title: str = Field(description="Title of the recipe")
    ingredients: List[str] = Field(description="List of ingredients needed")
    instructions: List[str] = Field(description="Step by step cooking instructions")
    prep_time: int = Field(description="Preparation time in minutes")
    cook_time: int = Field(description="Cooking time in minutes")
    servings: int = Field(description="Number of servings")


def main():
    """Generate structured recipes for different world cuisines using vLLM.

    Creates a dataset of cuisine names, sets up a recipe generation prompter using vLLM backend,
    and generates creative but realistic recipes for each cuisine. The results are parsed into
    a structured format with title, ingredients, instructions and timing details. The structured
    recipes are printed as a pandas DataFrame.
    """
    # List of cuisines to generate recipes for
    cuisines = [
        {"cuisine": cuisine}
        for cuisine in [
            "Chinese",
            "Italian",
            "Mexican",
            "French",
            "Japanese",
            "Indian",
            "Thai",
            "Korean",
            "Vietnamese",
            "Brazilian",
        ]
    ]
    cuisines = Dataset.from_list(cuisines)

    model_path = "Qwen/Qwen2.5-3B-Instruct"
    model_path = f"hosted_vllm/{model_path}"

    api_key = "token-abc123"

    os.environ["HOSTED_VLLM_API_KEY"] = api_key

    # Define the vLLM server params
    PORT = 8787
    HOST = "localhost"

    recipe_prompter = curator.LLM(
        model_name=model_path,
        prompt_func=lambda row: f"Generate a random {row['cuisine']} recipe. Be creative but keep it realistic.",
        parse_func=lambda row, response: {
            "title": response.title,
            "ingredients": response.ingredients,
            "instructions": response.instructions,
            "prep_time": response.prep_time,
            "cook_time": response.cook_time,
            "servings": response.servings,
        },
        backend="litellm",
        base_url=f"http://{HOST}:{PORT}/v1",
        response_format=Recipe,
    )

    # Generate recipes for all cuisines
    recipes = recipe_prompter(cuisines)

    # Print results
    print(recipes.to_pandas())


if __name__ == "__main__":
    main()