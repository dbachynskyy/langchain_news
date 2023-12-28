from flask import Flask, render_template, request
import newspaper
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

app = Flask(__name__)

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# List of CNN news categories
news_categories = ['business', 'media', 'tech', 'economy', 'food', 'investing', 'cars', 'opinions', 'politics', 'europe', 'world', 'entertainment', 'asia', 'china', 'india', 'us', 'style', 'health', 'travel', 'sport', 'middleeast', 'weather', 'climate', 'golf']

def scrape_articles(selected_categories):
    cnn_paper = newspaper.build('http://cnn.com', memoize_articles=False, request_timeout=10)

    selected_articles = []

    for article in cnn_paper.articles:
        try:
            url_split = article.url.split('/')

            for category in selected_categories:
                if category.lower() in url_split:
                    article.download()
                    article.parse()
                    selected_articles.append(article.title)

        except newspaper.article.ArticleException as e:
            print(f"Error downloading article: {e}")
            continue

    return set(selected_articles)


def generate_overview(articles):
    prompt = ChatPromptTemplate.from_template("write a short overview of today's news based on these article titles: {input}")
    model = ChatOpenAI()
    chain = prompt | model

    return chain.invoke({"input": articles})

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_categories = request.form.getlist('category')
        selected_articles = scrape_articles(selected_categories)
        overview = generate_overview(selected_articles)
        return render_template('result.html', selected_articles=selected_articles, overview=overview)

    return render_template('index.html', news_categories=news_categories)

if __name__ == '__main__':
    app.run(debug=True)
