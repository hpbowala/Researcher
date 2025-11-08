from typing import Annotated, List

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from web_operations import reddit_search as reddit_search_api, reddit_post_retrieval
from web_operations import serp_search
from prompts import (
    get_reddit_url_analysis_messages,
    get_google_analysis_messages,
    get_bing_analysis_messages,
    get_reddit_analysis_messages,
    get_synthesis_messages,
)

load_dotenv()

# initialize the llm
llm = init_chat_model(model="gpt-4.1")


class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_questions: str | None
    google_results: str | None
    reddit_results: str | None
    bing_results: str | None
    selected_reddit_urls: str | None
    reddit_post_data: str | None
    google_analysis: str | None
    reddit_analysis: str | None
    bing_analysis: str | None
    final_answer: str | None

class RedditURLAnalysis(BaseModel):
    selected_urls: List[str] = Field(description="List of Reddit URLs that contain valuable information for answering the user's question")


def google_search(state: State) -> State:
    user_questions = state.get("user_questions", "")
    print(f"Searching Google for: {user_questions}")
    google_results = serp_search(user_questions, engine="google")
    #  print(f"Google results: {google_results}")
    if google_results:
        print(f"Google Results found")
    return {"google_results": google_results}


def reddit_search(state: State) -> State:
    user_questions = state.get("user_questions", "")
    print(f"Searching Reddit for: {user_questions}")
    reddit_results = reddit_search_api(user_questions)
    return {"reddit_results": reddit_results}


def bing_search(state: State) -> State:
    user_questions = state.get("user_questions", "")
    print(f"Searching Bing for: {user_questions}")
    bing_results = serp_search(user_questions, engine="bing")
    return {"bing_results": bing_results}


def analyze_reddit_posts(state: State) -> State:
    user_questions = state.get("user_questions", "")
    reddit_results = state.get("reddit_results", "")
    
    if not reddit_results:
        return {"selected_reddit_urls": []}

    structured_llm = llm.with_structured_output(RedditURLAnalysis)
    messages = get_reddit_url_analysis_messages(user_questions, reddit_results)

    try:
        analysis = structured_llm.invoke(messages)
        selected_urls = analysis.selected_urls

        for i, url in enumerate(selected_urls, start=1):
            print(f"Analyzing Reddit post {i+1} of {len(selected_urls)}: {url}")
        

    except Exception as e:
        print(f"Error analyzing Reddit posts: {e}")
        selected_urls = []
        
    return {"selected_reddit_urls": selected_urls}


def retrieve_reddit_posts(state: State) -> State:
    print(f"Getting Reddit Post Comments")
    selected_urls = state.get("selected_reddit_urls", [])
    if not selected_urls:
        return {"reddit_post_data": []}

    print(f"Processing {len(selected_urls)} Reddit posts")

    reddit_post_data = reddit_post_retrieval(selected_urls)

    if reddit_post_data:
        print(f"Successfully retrieved {len(reddit_post_data)} posts")
    else:
        print(f"Failed to retrieve comments for selected Reddit posts")
        reddit_post_data = []

    return {"reddit_post_data": reddit_post_data}

def analyze_google_results(state: State) -> State:
    print(f"Analyzing Google Results")
    user_questions = state.get("user_questions", "")
    google_results = state.get("google_results", "")

    print(f"Analyzing {len(google_results)} Google results")

    messages = get_google_analysis_messages(user_questions, google_results)
    reply = llm.invoke(messages)

    return {"google_analysis": reply.content}


def analyze_bing_results(state: State) -> State:
    print(f"Analyzing Bing Results")
    user_questions = state.get("user_questions", "")
    bing_results = state.get("bing_results", "")

    print(f"Analyzing {len(bing_results)} Bing results")

    messages = get_bing_analysis_messages(user_questions, bing_results)
    reply = llm.invoke(messages)

    return {"bing_analysis": reply.content}


def analyze_reddit_results(state: State) -> State:
    print(f"Analyzing Reddit Results")
    user_questions = state.get("user_questions", "")
    reddit_results = state.get("reddit_results", "")
    reddit_post_data = state.get("reddit_post_data", "")


    print(f"Analyzing {len(reddit_results)} Reddit results")

    messages = get_reddit_analysis_messages(user_questions, reddit_results, reddit_post_data)
    reply = llm.invoke(messages)

    return {"reddit_analysis": reply.content}

def synthesize_analysis(state: State) -> State:
    print(f"Combine All Results Together")
    user_questions = state.get("user_questions", "")
    google_analysis = state.get("google_analysis", "")
    bing_analysis = state.get("bing_analysis", "")
    reddit_analysis = state.get("reddit_analysis", "")

    messages = get_synthesis_messages(user_questions, google_analysis, bing_analysis, reddit_analysis)
    reply = llm.invoke(messages)

    return {"final_answer": reply.content, "messages": [{"role": "assistant", "content": reply.content}]}
  


graph_builder = StateGraph(State)

graph_builder.add_node("google_search", google_search)
graph_builder.add_node("bing_search", bing_search)
graph_builder.add_node("reddit_search", reddit_search)
graph_builder.add_node("analyze_reddit_posts", analyze_reddit_posts)
graph_builder.add_node("retrieve_reddit_posts", retrieve_reddit_posts)
graph_builder.add_node("analyze_google_results", analyze_google_results)
graph_builder.add_node("analyze_bing_results", analyze_bing_results)
graph_builder.add_node("analyze_reddit_results", analyze_reddit_results)
graph_builder.add_node("synthesize_analysis", synthesize_analysis)

# connecting the nodes with edges
# connecting all search nodes to start will run all searches in parallel
graph_builder.add_edge(START, "google_search")
graph_builder.add_edge(START, "bing_search")
graph_builder.add_edge(START, "reddit_search")

# we wait for reddit posts
graph_builder.add_edge("google_search", "analyze_reddit_posts")
graph_builder.add_edge("bing_search", "analyze_reddit_posts")
graph_builder.add_edge("reddit_search", "analyze_reddit_posts")

# we analyze the reddit posts
graph_builder.add_edge("analyze_reddit_posts", "retrieve_reddit_posts")

# we analyze the google and bing results
graph_builder.add_edge("retrieve_reddit_posts", "analyze_google_results")
graph_builder.add_edge("retrieve_reddit_posts", "analyze_bing_results")
graph_builder.add_edge("retrieve_reddit_posts", "analyze_reddit_results")

# synthesize the analysis
graph_builder.add_edge("analyze_google_results", "synthesize_analysis")
graph_builder.add_edge("analyze_bing_results", "synthesize_analysis")
graph_builder.add_edge("analyze_reddit_results", "synthesize_analysis")

# we end the graph
graph_builder.add_edge("synthesize_analysis", END)

graph = graph_builder.compile()

# run the graph  execute the agent


def run_chatbot():
    print("Multi Source Agent: \n")
    print("Type 'exit' to quit: ")

    while True:
        user_input = input("Ask me anything: ")
        if user_input.lower() == "exit":
            break
        state = graph.invoke(
            {
                "messages": [{"role": "user", "content": user_input}],
                "user_questions": user_input,
                "google_results": None,
                "reddit_results": None,
                "bing_results": None,
                "selected_reddit_urls": None,
                "reddit_post_data": None,
                "google_analysis": None,
                "reddit_analysis": None,
                "bing_analysis": None,
                "final_answer": None,
            }
        )

        print("\nStarting parallel research process...")
        print("Launching Google, Bing, and Reddit searches...")
        final_state = graph.invoke(state)
        if final_state["final_answer"]:
            print(f"\nFinal Answer: {final_state['final_answer']}\n ")
        else:
            print("\nNo answer found\n\n")
        print("\nResearch process completed\n")

        print("-" * 50)


if __name__ == "__main__":
    run_chatbot()
