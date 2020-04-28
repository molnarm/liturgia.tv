def get_video(event):
    channel = event.location.youtube_channel

    return 'https://www.youtube.com/embed/live_stream?channel=' + channel
