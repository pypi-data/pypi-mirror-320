import json
import random
import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from tecton_gen_ai.utils import structured_outputs


class Topic(BaseModel):
    topics: list[str] = Field(
        description="the topic of a conversation between a customer and a customer service representative working at a car insurance company"
    )


class Message(BaseModel):
    role: str = Field(description="role can be either customer or agent")
    message: str = Field(description="the content")

    def __str__(self) -> str:
        return f"{self.role}: {self.message}"


class Conversation(BaseModel):
    customer_name: str = Field(
        description="the name of the customer, it should be randomly generated"
    )
    policy_number: str = Field(
        description="the policy number, should starting with 'pabc', ending with with 8 random digits"
    )
    messages: list[Message] = Field(
        description="""The customer conversation with the agent, at most 25 message
    The name and policy number should be in the conversation.
    """
    )

    def to_row(self):
        return {
            "policy_number": f"pabc-{uuid.uuid4().hex[:8]}",
            "conversation": "\n".join([str(m) for m in self.messages]),
            "timestamp": datetime(2024, 1, 3, 1).isoformat(),
        }


def main():
    from pprint import pprint

    topics = structured_outputs.batch_generate(
        model="openai/gpt-4o-mini",
        texts=["Generate 10 conversation topics"],
        schema=Topic,
    )[0].topics
    pprint(topics)

    conversation_prompts = []

    for topic in topics:
        num_conversations = random.randint(1, 10)
        for _ in range(num_conversations):
            sentiment = random.choice(["negative", "positive", "neutral"])
            conversation_prompts.append(
                f"""
                Generate a conversation between a customer and a customer support agent working for a car insurance company: Insured.
                The conversation is meant to be a script for a phone call between these two individuals for training. It should be realistic.
                The topic should be: {topic}
                The sentiment should be {sentiment}
                """
            )

    conversations = structured_outputs.batch_generate(
        model="openai/gpt-4o",
        texts=conversation_prompts,
        schema=Conversation,
        concurrency=10,
    )
    data_rows = [conv.to_row() for conv in conversations]

    with open("output.jsonl", "w") as outfile:
        for entry in data_rows:
            json.dump(entry, outfile)
            outfile.write("\n")

    # print(conv.to_row())


if __name__ == "__main__":
    main()
