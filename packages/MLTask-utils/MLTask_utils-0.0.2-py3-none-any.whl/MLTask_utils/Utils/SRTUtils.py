def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"


def format_srt_entry(order, start_time, end_time, text):
    return f"{order}\n{format_time(start_time)} --> {format_time(end_time)}\n{text.strip()}"
