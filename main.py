import json
from flask import Flask, request, render_template_string, url_for

from urllib.parse import quote

app = Flask(__name__)

with open("video_metadata.json", "r") as f:
    video_metadata_list = json.load(f)
    

BUCKET_NAME = "mnoumannaeem3bucket"


# Define HTML templates using render_template_string for simplicity.
INDEX_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>NLP project 2025</title>
    <style>
      /* Global Styles */
      body {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        background: linear-gradient(135deg, #74ABE2, #5563DE);
        margin: 0;
        padding: 0;
        color: #333;
      }
      .container {
        max-width: 1000px;
        margin: 40px auto;
        background: #fff;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
      }
      header {
        text-align: center;
        margin-bottom: 30px;
      }
      h1 {
        color: #2C3E50;
        margin-bottom: 10px;
      }
      h2 {
        color: #34495E;
      }
      
      /* Form Styling */
      form {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 30px;
      }
      form input[type="text"] {
        padding: 12px 15px;
        font-size: 16px;
        width: 350px;
        border: 2px solid #ccc;
        border-radius: 4px;
        margin-right: 10px;
      }
      form input[type="submit"] {
        padding: 12px 20px;
        font-size: 16px;
        background-color: #3498DB;
        color: #fff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.3s ease;
      }
      form input[type="submit"]:hover {
        background-color: #2980B9;
      }
      
      /* Horizontal Rule */
      hr {
        border: 0;
        height: 1px;
        background: #eee;
        margin: 20px 0;
      }
      
      /* Results List */
      ul {
        list-style-type: none;
        padding: 0;
      }
      li {
        background: #f9f9f9;
        margin-bottom: 20px;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 8px;
      }
      
      /* Video Item Layout */
      .video-item {
        display: flex;
        flex-wrap: wrap;
      }
      .video-thumbnail {
        flex: 1 1 150px;
        margin-right: 20px;
        margin-bottom: 15px;
      }
      .video-thumbnail video {
        width: 100%;
        max-width: 200px;
        height: auto;
        border-radius: 8px;
        object-fit: cover;
      }
      .video-details {
        flex: 2 1 300px;
      }
      .video-details h3 {
        margin-top: 0;
        margin-bottom: 8px;
        color: #2C3E50;
      }
      .video-details p {
        margin: 5px 0;
      }
      
      /* Tags Section */
      .tags-container {
        max-height: 70px;
        overflow: hidden;
        transition: max-height 0.3s ease;
        margin-top: 10px;
      }
      .keyphrase {
        display: inline-block;
        background-color: #ECF0F1;
        color: #2980B9;
        border: 1px solid #2980B9;
        padding: 6px 12px;
        border-radius: 20px;
        margin: 3px;
        font-size: 14px;
      }
      button.show-all-tags {
        background: none;
        border: none;
        color: #2980B9;
        cursor: pointer;
        font-size: 14px;
        margin-top: 8px;
      }
      button.show-all-tags:hover {
        text-decoration: underline;
      }
      
      /* Link Styling */
      a {
        color: #2980B9;
        text-decoration: none;
      }
      a:hover {
        text-decoration: underline;
      }
      
      /* Responsive Adjustments */
      @media (max-width: 768px) {
        .video-item {
          flex-direction: column;
        }
        .video-thumbnail {
          margin-right: 0;
        }
        form {
          flex-direction: column;
        }
        form input[type="text"] {
          margin-right: 0;
          margin-bottom: 10px;
          width: 100%;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <header>
        <h1>>NLP project 2025</h1>
        <p>Find the best videos by topic or key phrases</p>
      </header>
      <form method="GET" action="/">
        <input type="text" name="query" placeholder="Search..." value="{{ query|default('') }}">
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
                <button class="show-all-tags" id="btn-{{ video.video_id }}" onclick="toggleTags(event, '{{ video.video_id }}')">Show All Phrases</button>
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
    <style>
      /* Basic reset */
      * {
        box-sizing: border-box;
      }
      body {
        margin: 0;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        color: #333;
        padding: 20px;
      }
      .container {
        max-width: 900px;
        margin: 50px auto;
        background: #fff;
        border-radius: 10px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        padding: 30px;
      }
      h1 {
        text-align: center;
        margin-bottom: 20px;
        color: #2c3e50;
      }
      video {
        display: block;
        margin: 20px auto;
        width: 100%;
        max-width: 800px;
        border-radius: 10px;
        border: none;
      }
      .details {
        text-align: center;
        margin-top: 30px;
      }
      .details p {
        margin: 15px 0;
        font-size: 18px;
        color: #555;
      }
      .keyphrases {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        margin: 15px 0;
      }
      .keyphrase {
        background-color: #3498db;
        color: #fff;
        padding: 8px 14px;
        border-radius: 20px;
        font-size: 14px;
        border: none;
      }
      a {
        text-decoration: none;
        color: #3498db;
        font-weight: bold;
      }
      a:hover {
        text-decoration: underline;
      }
      /* Responsive Adjustments */
      @media (max-width: 600px) {
        .container {
          margin: 20px;
          padding: 20px;
        }
        .details p {
          font-size: 16px;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>{{ video.title }}</h1>
      <video controls>
        <source src="{{ video_url }}" type="video/mp4">
        Your browser does not support the video tag.
      </video>
      <div class="details">
        <p><strong>Topic:</strong> {{ video.topic }}</p>
        <p><strong>Key Phrases:</strong></p>
        <div class="keyphrases">
          {% for key in video.key_phrases %}
            <span class="keyphrase">{{ key }}</span>
          {% endfor %}
        </div>
        <p><a href="{{ url_for('index') }}">Back to search</a></p>
      </div>
    </div>
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
    bucket = "mnoumannaeem3bucket"
    s3_key = video["s3_key"]
    encoded_key = quote(s3_key)
    video_url = f"https://{bucket}.s3.amazonaws.com/{encoded_key}"
    print(video_url)
    return render_template_string(VIDEO_TEMPLATE, video=video, video_url=video_url)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
