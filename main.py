from flask import Flask, render_template_string, redirect, url_for
import boto3

app = Flask(__name__)

# Create an S3 client (ensure AWS credentials and region are properly configured)
s3 = boto3.client('s3')
BUCKET = "YOUR_BUCKET_NAME"

# Template for listing videos. For simplicity, we use render_template_string.
TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>Video List</title>
  </head>
  <body>
    <h1>Available Videos</h1>
    {% if videos %}
      {% for video in videos %}
        <div style="margin-bottom: 20px;">
          <h3>{{ video.key }}</h3>
          <!-- Video player using the presigned URL -->
          <video width="480" height="320" controls>
            <source src="{{ video.url }}" type="video/mp4">
            Your browser does not support the video tag.
          </video>
          <br>
          <!-- Optionally, a link to open the video separately -->
          <a href="{{ video.url }}" target="_blank">Open Video in New Tab</a>
        </div>
      {% endfor %}
    {% else %}
      <p>No videos found.</p>
    {% endif %}
  </body>
</html>
"""

@app.route("/")
def index():
    return "hello";
    # List objects in the bucket
    response = s3.list_objects_v2(Bucket=BUCKET)
    videos = []
    for obj in response.get('Contents', []):
        key = obj['Key']
        # Filter for .mp4 files (adjust as needed)
        if key.lower().endswith('.mp4'):
            # Generate a presigned URL valid for 1 hour
            presigned_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET, 'Key': key},
                ExpiresIn=3600
            )
            videos.append({"key": key, "url": presigned_url})
    return render_template_string(TEMPLATE, videos=videos)

@app.route("/video/<path:key>")
def stream_video(key):
    # Alternatively, you can have a route that redirects to a presigned URL.
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET, 'Key': key},
        ExpiresIn=3600
    )
    return redirect(presigned_url)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

