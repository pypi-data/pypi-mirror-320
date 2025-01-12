#!/usr/bin/python3

from base64 import b64encode
from mutagen.flac import FLAC, Picture
from mutagen.oggvorbis import OggVorbis
from deezspot.models import Track, Episode
import requests

def request(url):
    response = requests.get(url)
    response.raise_for_status()
    return response

from mutagen.id3 import (
	ID3NoHeaderError,
	ID3, APIC, USLT, SYLT,
	COMM, TSRC, TRCK, TIT2,
	TLEN, TEXT, TCON, TALB, TBPM,
	TPE1, TYER, TDAT, TPOS, TPE2,
	TPUB, TCOP, TXXX, TCOM, IPLS
)

def __write_flac(song, data):
	tag = FLAC(song)
	tag.delete()
	images = Picture()
	images.type = 3
	images.data = data['image']
	tag.clear_pictures()
	tag.add_picture(images)
	tag['lyrics'] = data['lyric']
	tag['artist'] = data['artist']
	tag['title'] = data['music']
	tag['date'] = f"{data['year'].year}/{data['year'].month}/{data['year'].day}"
	tag['album'] = data['album']
	tag['tracknumber'] = f"{data['tracknum']}"
	tag['discnumber'] = f"{data['discnum']}"
	tag['genre'] = data['genre']
	tag['albumartist'] = data['ar_album']
	tag['author'] = data['author']
	tag['composer'] = data['composer']
	tag['copyright'] = data['copyright']
	tag['bpm'] = f"{data['bpm']}"
	tag['length'] = f"{data['duration']}"
	tag['organization'] = data['label']
	tag['isrc'] = data['isrc']
	tag['lyricist'] = data['lyricist']
	tag['version'] = data['version']
	tag.save()

def __write_mp3(song, data):
	try:
		audio = ID3(song)
		audio.delete()
	except ID3NoHeaderError:
		audio = ID3()

	audio.add(
		APIC(
			mime = "image/jpeg",
			type = 3,
			desc = "album front cover",
			data = data['image']
		)
	)

	audio.add(
		COMM(
			lang = "eng",
			desc = "my comment",
			text = "DO NOT USE FOR YOUR OWN EARNING"
		)
	)

	audio.add(
		USLT(
			text = data['lyric']
		)
	)

	audio.add(
		SYLT(
			type = 1,
			format = 2,
			desc = "sync lyric song",
			text = data['lyric_sync']
		)
	)

	audio.add(
		TSRC(
			text = data['isrc']
		)
	)

	audio.add(
		TRCK(
			text = f"{data['tracknum']}/{data['nb_tracks']}"
		)
	)

	audio.add(
		TIT2(
			text = data['music']
		)
	)

	audio.add(
		TLEN(
			text = f"{data['duration']}"
		)
	)

	audio.add(
		TEXT(
			text = data['lyricist']
		)
	)

	audio.add(
		TCON(
			text = data['genre']
		)
	)

	audio.add(
		TALB(
			text = data['album']
		)
	)

	audio.add(
		TBPM(
			text = f"{data['bpm']}" 
		)
	)

	audio.add(
		TPE1(
			text = data['artist']
		)
	)

	audio.add(
		TYER(
			text = f"{data['year'].year}"
		)
	)

	audio.add(
		TDAT(
			text = f"{data['year'].day}{data['year'].month}"
		)
	)

	audio.add(
		TPOS(
			text = f"{data['discnum']}/{data['discnum']}"
		)
	)

	audio.add(
		TPE2(
			text = data['ar_album']
		)
	)

	audio.add(
		TPUB(
			text = data['label']
		)
	)

	audio.add(
		TCOP(
			text = data['copyright']
		)
	)

	audio.add(
		TXXX(
			desc = "REPLAYGAIN_TRACK_GAIN",
			text = f"{data['gain']}"
		)
	)

	audio.add(
		TCOM(
			text = data['composer']
		)
	)

	audio.add(
		IPLS(
			people = [
				data['author']
			]
		)
	)

	audio.save(song, v2_version = 3)

def __write_ogg(song, song_metadata):
    audio = OggVorbis(song)
    audio.delete()

    for key in ['music', 'artist', 'album', 'tracknum', 'discnum', 'year', 'genre', 'isrc', 'description']:
        if key in song_metadata:
            audio[key] = str(song_metadata[key])

    if 'image' in song_metadata:
        image = Picture()
        image.type = 3
        image.desc = 'Cover'
        image.mime = 'image/jpeg'
        
        try:
            if isinstance(song_metadata['image'], bytes):
                image.data = song_metadata['image']
            else:
                image.data = request(song_metadata['image']).content
                
            import base64
            img_data = base64.b64encode(image.write())
            audio['metadata_block_picture'] = [img_data.decode('utf-8')]
        except Exception as e:
            print(f"Warning: Could not add cover image: {str(e)}")

    audio.save()

def write_tags(media):
    if isinstance(media, Track):
        song = media.song_path
    elif isinstance(media, Episode):
        song = media.episode_path
    else:
        raise ValueError("Unsupported media type")

    song_metadata = media.tags
    f_format = media.file_format

    if f_format == ".flac":
        __write_flac(song, song_metadata)
    elif f_format == ".ogg":
        __write_ogg(song, song_metadata)
    else:
        __write_mp3(song, song_metadata)

def check_track(media):
    if isinstance(media, Track):
        song = media.song_path
    elif isinstance(media, Episode):
        song = media.episode_path
    else:
        raise ValueError("Unsupported media type")

    f_format = media.file_format
    is_ok = False

    # Add your logic to check the track/episode here

    return is_ok