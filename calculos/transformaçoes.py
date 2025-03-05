def seconds_to_hms(seconds: float) -> str:
    """Converte segundos para o formato HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def hms_to_seconds(hours: int, minutes: int, seconds: int) -> float:
    """Converte horas, minutos e segundos para segundos."""
    return hours * 3600 + minutes * 60 + seconds