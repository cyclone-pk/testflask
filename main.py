import json
from flask import Flask, request, render_template_string, url_for

from urllib.parse import quote

app = Flask(__name__)

with open("video_metadata.json", "r") as f:
    video_metadata_list = json.load(f)
    

BUCKET_NAME = "nlpprojectbucketforstoringthevideos2025lakehead"


# Define HTML templates using render_template_string for simplicity.
INDEX_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>Video Search Dashboard</title>
  </head>
  <body>
    <h1>Video Search Dashboard</h1>
    <form method="GET" action="/">
      <input type="text" name="query" placeholder="Search by topic or key phrase" value="{{ query|default('') }}" style="width: 300px;">
      <input type="submit" value="Search">
    </form>
    <hr>
    <h2>Results:</h2>
    {% if results %}
      <ul>
      {% for video in results %}
        <li>
          <a href="{{ url_for('view_video', video_id=video.video_id) }}">{{ video.title }}</a>
          <br><strong>Topic:</strong> {{ video.topic }}<br>
          <strong>Key Phrases:</strong> {{ video.key_phrases | join(', ') }}
        </li>
      {% endfor %}
      </ul>
    {% else %}
      <p>No videos match your search.</p>
    {% endif %}
  </body>
</html>
"""

VIDEO_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>{{ video.title }}</title>
  </head>
  <body>
    <h1>{{ video.title }}</h1>
    <video width="640" height="480" controls>
      <source src="{{ video_url }}" type="video/mp4">
      Your browser does not support the video tag.
    </video>
    <p><strong>Topic:</strong> {{ video.topic }}</p>
    <p><strong>Key Phrases:</strong> {{ video.key_phrases | join(', ') }}</p>
    <p><a href="{{ url_for('index') }}">Back to search</a></p>
  </body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("query", "").strip().lower()
    if query:
        filtered = []
        for video in video_metadata_list:
            # Search in topic and key phrases (case-insensitive)
            if query in video["topic"].lower() or any(query in phrase.lower() for phrase in video["key_phrases"]):
                filtered.append(video)
    else:
        filtered = video_metadata_list
    return render_template_string(INDEX_TEMPLATE, results=filtered, query=query)



@app.route("/video/<video_id>")
def view_video(video_id):
    # Find the video by video_id.
    video = next((v for v in video_metadata_list if v["video_id"] == video_id), None)
    if not video:
        return "Video not found", 404
    # Construct the public URL.
    bucket = "nlpprojectbucketforstoringthevideos2025lakehead"
    s3_key = video["s3_key"]
    encoded_key = quote(s3_key)
    video_url = f"https://{bucket}.s3.amazonaws.com/{encoded_key}"
    print(video_url)
    return render_template_string(VIDEO_TEMPLATE, video=video, video_url=video_url)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
