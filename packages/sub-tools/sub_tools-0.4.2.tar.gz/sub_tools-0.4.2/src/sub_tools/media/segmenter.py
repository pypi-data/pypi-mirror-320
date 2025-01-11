import glob

from typing import Union
from dataclasses import dataclass
from pydub import AudioSegment, silence


@dataclass
class SegmentConfig:
    """
    Configuration for audio segmentation.
    """

    max_silence_length: int = 3_000  # 3 seconds
    min_silence_length: int = 200  # 1 second
    silence_threshold_db: int = -40
    db_increment: int = 10
    seek_step: int = 10  # 10 ms
    directory: str = "tmp"


def segment_audio(
    audio_file: str,
    audio_segment_prefix: str,
    audio_segment_format: str,
    audio_segment_length: int,
    overwrite: bool = False,
    config: SegmentConfig = SegmentConfig(),
) -> None:
    """
    Segments an audio file using natural pauses.
    """
    pattern = f"{config.directory}/{audio_segment_prefix}_[0-9]*.{audio_segment_format}"
    if glob.glob(pattern) and not overwrite:
        print("Segmented audio files already exist. Skipping segmentation...")
        return

    print(f"Segmenting audio file {audio_file}...")

    audio = AudioSegment.from_file(audio_file, format="mp3")
    segment_ranges = _get_segment_ranges(audio, audio_segment_length, config)

    for start_ms, end_ms in segment_ranges:
        output_file = f"{config.directory}/{audio_segment_prefix}_{start_ms}.{audio_segment_format}"
        partial_audio = audio[start_ms:end_ms]
        partial_audio.export(output_file, format=audio_segment_format)


def _get_segment_ranges(
    audio: AudioSegment,
    segment_length: int,
    config: SegmentConfig,
) -> list[tuple[int, int]]:
    """
    Returns a list of segment ranges for the audio file.
    """
    total_length = len(audio)
    ranges = []
    current_start = 0

    while current_start < total_length:
        current_end = current_start + min(segment_length, total_length - current_start)
        split_range = _find_split_range(audio, current_start, current_end, config)

        if split_range:
            start_ms, end_ms = split_range
            if end_ms - start_ms >= config.min_silence_length:
                ranges.append((start_ms, end_ms))
            current_start = end_ms
        else:
            current_start = current_end

    return ranges


def _find_split_range(
    audio: AudioSegment,
    start_ms: int,
    end_ms: int,
    config: SegmentConfig,
) -> Union[tuple[int, int], None]:
    """
    Find optimal split points in audio segment.
    """
    segment = audio[start_ms:end_ms]
    silence_threshold_db = config.silence_threshold_db
    non_silent_ranges = []

    while silence_threshold_db < 0:
        non_silent_ranges += silence.detect_nonsilent(
            segment,
            min_silence_len=config.min_silence_length,
            silence_thresh=silence_threshold_db,
            seek_step=config.seek_step,
        )

        if len(non_silent_ranges) > 0:
            break

        silence_threshold_db += config.db_increment

    non_silent_ranges = _filter_ranges(non_silent_ranges, config.max_silence_length)
    
    if len(non_silent_ranges) > 0:
        start_ms, end_ms = non_silent_ranges[0][0] + start_ms, non_silent_ranges[-1][1] + start_ms
        return (start_ms, end_ms)

    return None


def _filter_ranges(
    ranges: list[tuple[int, int]],
    max_silence_length: int,
) -> list[tuple[int, int]]:
    """
    Filters ranges by keeping only consecutive segments within max_silence_length.
    """
    if not ranges:
        return []
    
    filtered_ranges = [ranges[0]]
    for current_range in ranges[1:]:
        if current_range[0] - filtered_ranges[-1][1] > max_silence_length:
            break
        filtered_ranges.append(current_range)

    return filtered_ranges
