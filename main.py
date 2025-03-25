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
    <style>
      /* General styling */
      body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        margin: 0;
        padding: 20px;
      }
      .container {
        max-width: 800px;
        margin: auto;
        background: #fff;
        padding: 20px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        border-radius: 5px;
      }
      h1, h2 {
        color: #333;
      }
      form {
        margin-bottom: 20px;
      }
      form input[type="text"] {
        padding: 10px;
        font-size: 16px;
        width: 300px;
        border: 1px solid #ccc;
        border-radius: 4px;
      }
      form input[type="submit"] {
        padding: 10px 20px;
        font-size: 16px;
        background-color: #007BFF;
        color: #fff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
      }
      form input[type="submit"]:hover {
        background-color: #0056b3;
      }
      ul {
        list-style-type: none;
        padding: 0;
      }
      li {
        background: #fafafa;
        margin-bottom: 15px;
        padding: 15px;
        border: 1px solid #ddd;
        border-radius: 5px;
      }
      /* Flex container for each video item */
      .video-item {
        display: flex;
        align-items: flex-start;
      }
      /* Left side: Square video thumbnail */
      .video-thumbnail {
        margin-right: 15px;
      }
      .video-thumbnail video {
        width: 150px;
        height: 150px;
        object-fit: cover;
        border-radius: 5px;
      }
      /* Right side: Video details */
      .video-details h3 {
        margin: 0 0 5px 0;
      }
      .video-details p {
        margin: 5px 0;
      }
      /* Key phrases container styling */
      .tags-container {
        max-height: 65px;
        overflow: hidden;
        transition: max-height 0.3s ease;
      }
      .keyphrase {
        display: inline-block;
        background-color: #e7f3ff;
        color: #007BFF;
        border: 1px solid #007BFF;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 2px;
        font-size: 14px;
      }
      button.show-all-tags {
        background: none;
        border: none;
        color: #007BFF;
        cursor: pointer;
        font-size: 14px;
        margin-top: 5px;
      }
      button.show-all-tags:hover {
        text-decoration: underline;
      }
      a {
        color: #007BFF;
        text-decoration: none;
      }
      a:hover {
        text-decoration: underline;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Video Search Dashboard</h1>
      <form method="GET" action="/">
        <input type="text" name="query" placeholder="Search by topic or key phrase" value="{{ query|default('') }}">
        <input type="submit" value="Search">
      </form>
      <hr>
      <h2>Results:</h2>
      {% if results %}
        <ul>
        {% for video in results %}
          <li>
            <div class="video-item">
              <div class="video-thumbnail">
                <video muted playsinline>
                  <source src="https://nlpprojectbucketforstoringthevideos2025lakehead.s3.amazonaws.com/{{ video.s3_key }}" type="video/mp4">
                  Your browser does not support the video tag.
                </video>
              </div>
              <div class="video-details">
                <a href="{{ url_for('view_video', video_id=video.video_id) }}">
                  <h3>{{ video.title }}</h3>
                </a>
                <p><strong>Topic:</strong> {{ video.topic }}</p>
                <p><strong>Key Phrases:</strong></p>
                <div class="tags-container" id="tags-container-{{ video.video_id }}">
                  {% for key in video.key_phrases %}
                    <span class="keyphrase">{{ key }}</span>
                  {% endfor %}
                </div>
                <button class="show-all-tags" id="btn-{{ video.video_id }}" onclick="toggleTags(event, '{{ video.video_id }}')">Read all tags</button>
              </div>
            </div>
          </li>
        {% endfor %}
        </ul>
      {% else %}
        <p>No videos match your search.</p>
      {% endif %}
    </div>
    <script>
      function toggleTags(event, videoId) {
        event.preventDefault();
        var container = document.getElementById('tags-container-' + videoId);
        container.style.maxHeight = "none";
        var btn = document.getElementById('btn-' + videoId);
        btn.style.display = 'none';
      }

      // On window load, check if each tags-container is overflowing; if not, hide its button
      window.addEventListener('load', function() {
        document.querySelectorAll('.tags-container').forEach(function(container) {
          if (container.scrollHeight <= container.clientHeight) {
            var videoId = container.id.replace('tags-container-', '');
            var btn = document.getElementById('btn-' + videoId);
            if (btn) {
              btn.style.display = 'none';
            }
          }
        });
      });
    </script>
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
