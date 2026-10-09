"""Short, generated technical movies; no AI or game footage, no paid APIs."""
from pathlib import Path
import shutil
import subprocess


def create_video(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('Selection movie checks require ffmpeg with libtheora')
    common = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
              '-f', 'lavfi', '-i', 'testsrc2=size=1360x768:rate=24', '-t', '1.25']
    subprocess.run([*common, '-an', '-c:v', 'libtheora', '-q:v', '4', str(folder/'movie.ogv')], check=True)
    movie = (folder/'movie.ogv').read_bytes()
    (folder/'truncated.ogv').write_bytes(movie[:-40])
    (folder/'invalid.ogv').write_bytes(b'not an Ogg Theora movie')
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
                    '-i', str(folder/'movie.ogv'), '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                    '-t', '1.25', '-c:v', 'copy', '-c:a', 'libvorbis', str(folder/'with-audio.ogv')], check=True)
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
                    '-i', str(folder/'movie.ogv'), '-frames:v', '1', str(folder/'video-poster.png')], check=True)
    return folder/'movie.ogv'
